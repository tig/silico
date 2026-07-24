# macOS + Codex + ESP-IDF (host knowledge)

Learned from Mac/Codex first-ship on M5GO / CH9102 (tig/silico#84).

## Shell

- Codex desktop may default to **PowerShell** on macOS.
- Espressif `export.ps1` can emit **Windows-style backslash paths** for `idf.py` that break on macOS.
- Prefer:
  - bash/`zsh` and `source $IDF_PATH/export.sh`, or
  - shell-free: full path to IDF python + `idf.py` after env is set.

```bash
# Working pattern (example)
export IDF_PATH=...
export IDF_PYTHON_ENV_PATH=$HOME/.espressif/python_env/idf5.3_py3.12_env
. "$IDF_PATH/export.sh"
idf.py --version
```

## Python env

- `install.sh esp32` with **system Python 3.9** often creates a bad checker/env.
- Prepend a **3.11+** (3.12 preferred) interpreter, then install; set `IDF_PYTHON_ENV_PATH` to the resulting `idf*_py3.12_env`.
- `silico doctor` (language=c) and `silico env --print` surface activation and tool paths when EIM/IDF is present.

## Serial

- CH9102: keep default identity probe **without** DTR/RTS pulse; do not run `monitor` and `inspect`/`deploy --verify` on the same port in parallel (port busy → clear HINT).
- After `idf.py flash`, wait for CDC re-enumeration before identity verify (silico deploy does this).

## Provenance

- Record start: `silico session start --mode evaluation --agent codex`
- Do not past-HEAD salvage product face from older commits; build from current HEAD (AGENTS **Product truth is HEAD**).
