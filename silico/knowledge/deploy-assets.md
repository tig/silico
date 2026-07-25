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

## ESP-IDF path: SPIFFS partition (language=c)

Under ESP-IDF there is no mpremote filesystem — ship multi-MB assets in a
dedicated flash partition instead of embedding them in the app binary:

1. Add a `storage` **SPIFFS** partition to `partitions.csv` sized for the
   asset (a 16 MB flash module fits app + multi-MB audio comfortably;
   confirm the module size before assuming >4 MB).
2. `spiffs_create_partition_image(storage <dir> FLASH_IN_PROJECT)` in the
   component CMake builds and flashes the image with `idf.py flash`.
3. **Do not commit the generated binary asset.** Keep the *source* asset or
   a regeneration script (e.g. `tools/make_song.sh` ffmpeg → raw u8 PCM) in
   the repo, gitignore the output, and document “regenerate before first
   build on a fresh checkout” in the GCU README.
4. Firmware fails closed on missing/zero-length asset (rule 4 above) — a
   fresh checkout that skipped regeneration must show a clear error, not
   silence.
