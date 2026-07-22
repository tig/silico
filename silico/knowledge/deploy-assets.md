# Deploying large non-Python assets (self-improving)

Host notes for GCUs that ship **binary files** next to firmware (PCM riffs, fonts, images). Not product asset lists.

## Problem

`mpremote cp` (and thin wrappers) can fail mid-transfer on multi‑MB files and leave a **0-byte or truncated** remote file. A later “play song” path then looks like a DAC bug when the file is empty.

## Rules

1. **Verify size after copy.** After every large asset upload, `os.stat` (or `mpremote fs ls`) and require `size == local_size` and `size > 0`.
2. Prefer **chunked upload** (small blocks with progress) or a host script that base64/hex streams through raw REPL when `cp` is flaky.
3. Put large binaries in `[deploy].core` only if the deploy tool copies them as **opaque files** (host hygiene must not try to import them as UTF-8 Python).
4. Product firmware must **fail closed** if a required asset is missing or zero-length (clear link error / UI), not hang in an empty read loop.
5. Do not claim metal audio “works” until the asset size on device is checked once after deploy.

## Agent checklist

1. List required non-`.py` assets and expected byte sizes in the GCU (README or deploy notes).
2. After deploy, verify each large asset size before operator audio acceptance.
3. If you invent a more reliable upload path, extend **this file** or improve `silico deploy` — do not leave the recipe only in chat.
