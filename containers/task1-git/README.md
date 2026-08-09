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

Target repo (frozen state: 12 open issues, 4 open PRs) is decided separately and referenced
by the agent's task prompt, not baked into this image.
