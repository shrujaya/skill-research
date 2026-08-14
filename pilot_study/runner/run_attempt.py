#!/usr/bin/env python3
"""Run one agent attempt against one (task, skill file) pair, inside a disposable
Docker container.

The agent process itself runs here, on the host (so it can reach the Anthropic API).
Only the agent's shell commands are executed inside the container, via `docker exec`,
so the container's own network isolation (e.g. --network none) stays intact -- the
agent can't reach out to the internet from inside the sandbox, only its "brain" can.

The skill file's raw content is injected verbatim into the system prompt. No skill
auto-discovery/triggering logic is involved -- for this experiment the skill file
under test must always be in context, deterministically, every run.

Usage:
    cp .env.example .env   # then fill in your own values
    python3 run_attempt.py \\
        --task task1-git \\
        --skill ../pilot_study/skills/task1-git/gpt-5.6-terra-medium/00_baseline_SKILL.md \\
        --attempt 1 \\
        --out results/task1-git/00_baseline/attempt_1

    # or skip the .env file and export directly:
    export ANTHROPIC_API_KEY=...
    export GH_TOKEN=...   # only needed for task1-git
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER_DIR = Path(__file__).resolve().parent
TASKS_FILE = RUNNER_DIR / "tasks.json"


def load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines from a .env file into the environment. Never
    overrides a variable that's already set (e.g. via `export` in the shell) --
    matches standard dotenv precedence."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

SHELL_TOOL = {
    "name": "run_shell_command",
    "description": "Run a shell command inside your working sandbox and return its stdout/stderr and exit code.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The shell command to run."}
        },
        "required": ["command"],
    },
}

MAX_TOOL_OUTPUT_CHARS = 8000


def load_task(task_key: str) -> dict:
    tasks = json.loads(TASKS_FILE.read_text())
    if task_key not in tasks:
        sys.exit(f"Unknown task '{task_key}'. Known tasks: {', '.join(tasks)}")
    return tasks[task_key]


def start_container(task: dict, container_name: str) -> None:
    cmd = ["docker", "run", "-d", "--name", container_name]

    for env_name in task["env"]:
        value = os.environ.get(env_name)
        if not value:
            sys.exit(f"Required environment variable {env_name} is not set.")
        cmd += ["-e", f"{env_name}={value}"]

    # Hardcoded, non-secret values (e.g. a deliberately revoked token for a
    # broken-variant task) -- these are baked into tasks.json directly, not
    # read from .env, since they're meant to be invalid on purpose.
    for env_name, value in task.get("env_literal", {}).items():
        cmd += ["-e", f"{env_name}={value}"]

    context_dir = REPO_ROOT / task["context_dir"]
    for host_rel, container_path in task["mounts"].items():
        host_path = context_dir / host_rel
        if not host_path.exists():
            sys.exit(f"Mount source not found: {host_path}")
        cmd += ["-v", f"{host_path}:{container_path}:ro"]

    if task["network"] == "none":
        cmd += ["--network", "none"]

    cmd += [task["image"], "tail", "-f", "/dev/null"]
    subprocess.run(cmd, check=True, capture_output=True)


def run_in_container(container_name: str, command: str, workdir: str, timeout: int = 60) -> str:
    try:
        result = subprocess.run(
            ["docker", "exec", "-w", workdir, container_name, "bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"[command timed out after {timeout}s]"

    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    output += f"\n[exit code: {result.returncode}]"
    if len(output) > MAX_TOOL_OUTPUT_CHARS:
        output = output[:MAX_TOOL_OUTPUT_CHARS] + "\n[...output truncated...]"
    return output


def build_system_prompt(skill_content: str, workdir: str) -> str:
    return (
        "You are an autonomous coding agent working inside a sandboxed environment. "
        "You have access to a `run_shell_command` tool that executes shell commands "
        "in your working sandbox. Use it to complete the task the user describes. "
        f"Every command starts fresh in `{workdir}` -- this is not a persistent shell "
        "session, so a `cd` in one command does not carry over to the next one. Use "
        f"relative paths (they resolve against `{workdir}`) or repeat any `cd` within "
        "a single command if you need to chain steps; there's no need to `cd` back to "
        "a home directory for consistency, every command already starts in the same place. "
        "When you are finished, reply with a final message summarizing what you did, "
        "with no further tool calls.\n\n"
        "The following is a skill file with instructions for this kind of task:\n\n"
        f"{skill_content}"
    )


def run_agent(client, container_name, system_prompt, task_prompt, model, max_turns, workdir):
    messages = [{"role": "user", "content": task_prompt}]
    transcript = []

    for turn in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=[SHELL_TOOL],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        transcript.append({"role": "assistant", "content": [block.model_dump() for block in response.content]})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "run_shell_command":
                command = block.input["command"]
                output = run_in_container(container_name, command, workdir)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": tool_results})
        transcript.append({"role": "user", "content": tool_results})
    else:
        transcript.append({"role": "system", "content": f"[stopped: hit max_turns={max_turns}]"})

    return transcript


def collect_deliverables(task: dict, container_name: str, out_dir: Path) -> None:
    deliverables_dir = out_dir / "deliverables"
    deliverables_dir.mkdir(parents=True, exist_ok=True)
    for path in task["workdir_deliverables"]:
        dest = deliverables_dir / Path(path).name
        result = subprocess.run(
            ["docker", "cp", f"{container_name}:{path}", str(dest)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  [warn] could not collect {path}: {result.stderr.strip()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task", required=True, help="Task key from tasks.json")
    parser.add_argument("--skill", required=True, type=Path, help="Path to the SKILL.md file to inject")
    parser.add_argument("--attempt", required=True, type=int, help="Attempt number (for naming only)")
    parser.add_argument("--out", required=True, type=Path, help="Output directory for transcript + deliverables")
    parser.add_argument("--model", default="claude-opus-5", help="Backend model for the runner agent")
    parser.add_argument("--max-turns", type=int, default=20, help="Max agent turns before giving up")
    parser.add_argument("--env-file", type=Path, default=RUNNER_DIR / ".env", help="Path to a .env file to load (default: runner/.env)")
    args = parser.parse_args()

    load_dotenv(args.env_file)

    task = load_task(args.task)
    skill_content = args.skill.read_text()
    system_prompt = build_system_prompt(skill_content, task["workdir"])

    container_name = f"{args.task}-a{args.attempt}-{uuid.uuid4().hex[:6]}"
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{container_name}] starting container from image '{task['image']}' (network={task['network']})...")
    start_container(task, container_name)

    try:
        client = anthropic.Anthropic()
        print(f"[{container_name}] running agent (model={args.model}, max_turns={args.max_turns})...")
        started = time.time()
        transcript = run_agent(client, container_name, system_prompt, task["task_prompt"], args.model, args.max_turns, task["workdir"])
        elapsed = time.time() - started
        print(f"[{container_name}] agent finished in {elapsed:.1f}s ({len(transcript)} turns)")

        (out_dir / "transcript.json").write_text(json.dumps(transcript, indent=2, default=str))

        print(f"[{container_name}] collecting deliverables...")
        collect_deliverables(task, container_name, out_dir)
    finally:
        print(f"[{container_name}] tearing down container...")
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    print(f"Done. Results in {out_dir}")


if __name__ == "__main__":
    main()
