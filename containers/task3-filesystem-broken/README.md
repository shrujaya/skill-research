# Task 3: Directory cleanup — shell sandbox (broken)

Identical to `../task3-filesystem-clean/` (same `build_inbox.sh`, same 40-file manifest),
with one addition at the end of the Dockerfile: `roadtrip.jpg` is `chown root:root` +
`chmod 000` after the general `chown -R agent:agent` step, so that one lock wins.

This is a **separate image**, not a runtime toggle like Task 1's `GH_TOKEN` or Task 2's
bind-mounted CSV — the fault is a filesystem permission bit, which has to be baked into
a build-time layer. A bind mount can't reliably fake root ownership across Docker
Desktop's filesystem translation, so a second, standalone Dockerfile is the more robust
choice here.

```bash
docker build -t task3-filesystem-broken .
docker run --rm -it --network none task3-filesystem-broken
```

Because the container always runs as the non-root `agent` user (never root), `agent`
genuinely cannot read, move, or delete `roadtrip.jpg` — this tests the F7 question from
the spec: does the agent detect and report the unmovable file and still finish
everything else, or does it crash/skip silently?

`build_inbox.sh` is duplicated here rather than shared via a symlink or common base
image, to keep this directory fully self-contained. If the file manifest changes, update
both copies (`task3-filesystem-clean/build_inbox.sh` and this one) together.

No answer key is included in this image, same as the clean variant.
