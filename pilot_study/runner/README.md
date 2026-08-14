# Runner — orchestrates one agent attempt per (task, skill file) pair

## How it works

The agent process runs **on your host**, not inside the container — that's what lets
it reach the Anthropic API while the container itself stays as isolated as the
sandbox was designed to be (`--network none` for tasks 2 & 3 is preserved; the agent's
shell commands are the only thing that touch the container, via `docker exec`, and its
own reasoning/API calls happen outside it).

The skill file's raw content is injected verbatim into the system prompt for every
attempt — there's no skill-discovery/triggering step, since the point of the
experiment is to test the skill file's content itself, not whether some framework
decides to load it.

Each attempt:
1. Starts a **fresh** container from the task's clean/broken image (no state carries
   over between attempts)
2. Runs a hand-rolled tool-use loop against `claude-opus-5` (or whatever `--model` you
   pass), giving it exactly one tool: `run_shell_command`, which executes via
   `docker exec` into that attempt's container
3. Saves the full turn-by-turn transcript (every message, every tool call, every
   result) as `transcript.json` — this is the raw material for later
   attribution/ablation analysis
4. Copies out whatever deliverable files exist (`issue_report.md`, `summary.csv`,
   the reorganized `inbox/`, etc. — see `tasks.json`) into `deliverables/`
5. Tears the container down

## Setup

```bash
pip install anthropic
cp .env.example .env
# then edit .env and fill in ANTHROPIC_API_KEY (and GH_TOKEN, for task1-git)
```

`run_attempt.py` loads `runner/.env` automatically (pass `--env-file` to use a
different path). `.env` is gitignored — only `.env.example` is meant to be committed.
Values already exported in your shell take precedence over the `.env` file.

If you'd rather not use a file at all:
```bash
export ANTHROPIC_API_KEY=...
export GH_TOKEN=...     # only needed for task1-git
```

Results are organized `results/<runner-model>/<task>/attempt_<n>/<variant>/`, so
`attempt_N` groups every variant run in that pass together, and it's always clear
which backend model produced a given run.

## Running one attempt

```bash
python3 run_attempt.py \
    --task task1-git-clean \
    --skill ../skills/task1-git/gpt-5.6-terra-medium/00_baseline_SKILL.md \
    --attempt 1 \
    --out results/claude-opus-5/task1-git-clean/attempt_1/00_baseline
```

## Running 3 attempts of every skill variant for one task (pilot study, step 2.3)

```bash
MODEL=claude-opus-5
for attempt in 1 2 3; do
    for skill in ../skills/task1-git/gpt-5.6-terra-medium/*.md; do
        name=$(basename "$skill" _SKILL.md)
        python3 run_attempt.py \
            --task task1-git-clean \
            --skill "$skill" \
            --attempt "$attempt" \
            --model "$MODEL" \
            --out "results/$MODEL/task1-git-clean/attempt_$attempt/$name"
    done
done
```

## Task registry (`tasks.json`)

Each entry maps a task key to: the image to run, which env vars must be present on
your host, which files (if any) get bind-mounted in (e.g. `orders_broken.csv` for
`task2-data-broken`), whether the container gets `--network none`, and which
in-container paths count as deliverables to collect.

## Notes / things not built yet

- **No grader.** This collects deliverables; it doesn't score them against the
  milestone checklists yet (Implementation Plan step 1.5/1.6). The answer keys should
  stay host-side only, same principle as the containers themselves — never baked into
  an image the agent can read.
- **No retry/rate-limit handling.** A dropped API call currently just crashes the
  attempt; worth adding backoff before running this at real pilot-study volume.
- **`--max-turns` (default 20)** is a blunt safety cap, not tuned per task.
