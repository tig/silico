# Install / update (C plate)

Host gate:

```text
cmake -S host -B build/host
cmake --build build/host --target host_test
```

Deploy (after operator confirms board identity):

```text
silico deploy --port COMx --yes --verify
```

Requires ESP-IDF (`idf.py` or `IDF_PATH`). First flash and app update use the same image path.

## Data-partition assets

If the product ships payloads outside the app image (audio, LUTs, calibration), declare them as `[[deploy.data]]` in `silico.toml`. `silico deploy` plans and flashes them with the image, behind the same `--yes` confirm.

Do **not** paste a raw `esptool write_flash` line into this file as the operator's path. An asset flashed by a hand-run command is an asset that goes missing on the next bench — and the firmware then has to guess what to do about it. Silico grew `[[deploy.data]]` (tig/silico#79) specifically to delete that command wall.
