# Task 3: Directory cleanup — shell sandbox (clean)

Base: `ubuntu:24.04`. Installs nothing beyond `coreutils` (already in base, explicit for
clarity) and `file` (type-detection utility). Runs as non-root user `agent`, home
`/home/agent`, so the task's `~/inbox` resolves to `/home/agent/inbox`.

```bash
docker run --rm -it --network none task3-filesystem-clean
```

## The inbox (40 files, deterministic)

Built by `build_inbox.sh` during the image build (baked into the image layer, not
generated at container start), so every run has an identical inbox:

- **12 images** (`.jpg`/`.png`), **12 documents** (`.pdf`/`.docx`), **12 spreadsheets**
  (`.csv`/`.xlsx`) — 2 of each dozen dated pre-2024 (archive-eligible), the rest 2024+
- **3 `tmp`-named files** spread across types/dates — must be deleted regardless of
  type or date (tests that this rule overrides both sorting and archiving)
- **1 `notes.txt`** — must remain untouched, in place

Every file has real magic-byte headers matching its extension (so `file` and
extension-based sorting agree), but the files are stand-in content only, not genuinely
openable documents/images — the task never requires reading file contents, only moving,
renaming, and deleting based on type, name, and modification date.

**Archive-rule interpretation**: "older than 2024" = modification time before
`2024-01-01`. Anything dated 2024 or later is sorted normally by type.

No filenames encode their dates — the agent has to check actual modification time
(e.g. via `stat`/`ls -l --time-style`), not infer it from the name.

## Determinism check

Timestamps are set with `touch -t` inside a `RUN` layer at build time, so they're part
of the image filesystem and don't change between container starts. Verified with:
```bash
docker build -t task3-filesystem-clean .
docker run --rm task3-filesystem-clean ls -la --time-style=full-iso inbox > /tmp/run1.txt
docker run --rm task3-filesystem-clean ls -la --time-style=full-iso inbox > /tmp/run2.txt
diff /tmp/run1.txt /tmp/run2.txt   # expect no differences
```

## Broken variant

See `../task3-filesystem-broken/` — same manifest, but one ordinary image file
(`roadtrip.jpg`) is locked `root:root` + `chmod 000` so the non-root `agent` user can't
read or move it. Built as a separate image since the fault is a filesystem permission
bit baked at build time, not something togglable at `docker run` time.

## No answer key in this image

The correct final directory tree is intentionally not included here, same principle as
Task 2 — grading happens host-side later, never inside the sandbox the agent operates in.
