# Task 1: GitHub issue report — `gh` CLI sandbox

Base: `ubuntu:24.04`. Installs `gh`, `git`, `curl`, `jq`, `nano`. Runs as non-root user `agent`,
working directory `/workspace`.

`GH_TOKEN` is passed at `docker run` time, never baked into the image. This lets the same
image serve both sandbox variants from the spec:

- **Clean**: valid token for the frozen target repo.
  ```bash
  docker run --rm -it -e GH_TOKEN=<valid_token> task1-git
  ```
- **Broken (auth fault)**: same image, garbage/revoked token.
  ```bash
  docker run --rm -it -e GH_TOKEN=revoked_or_garbage task1-git
  ```

## Target repo

`github.com/shrujaya/test-repo` — frozen state: **2 open issues, 2 open PRs**.
Not baked into the image; the agent reaches it over the network using `GH_TOKEN`.

- Issues: #1 "Fix typo in README", #2 "Add CONTRIBUTING guidelines"
- PRs: #3 "Add license placeholder section" (branch `add-license-note`),
  #4 "Add usage placeholder section" (branch `add-usage-section`)

Do not touch this repo's issues/PRs going forward — its state needs to stay frozen so the
milestone checklist's hardcoded correct answer (count = 2, excluding the 2 PRs) stays valid
across every run.
