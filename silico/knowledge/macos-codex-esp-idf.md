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
- **Homebrew python linkage rot:** a brew-installed python can fail with
  `pyexpat` / `libexpat` symbol errors, which breaks `install.sh` and
  `idf_tools.py` in confusing ways. `silico doctor` now checks pyexpat;
  fix by using a **uv-managed interpreter** (`uv venv --python 3.11`) rather
  than fighting brew relinks.
- **Project venv shadows the IDF env.** If the GCU/agent venv is on PATH
  ahead of the IDF python env, `idf.py` resolves the wrong interpreter and
  fails on missing IDF packages. Deactivate (or strip the venv `bin` from
  PATH) before `. $IDF_PATH/export.sh`, or invoke the IDF python explicitly.
- **Find an existing install before installing a new one:**
  `~/.espressif/idf-env.json` (written by `install.sh`/`idf_tools.py`) lists
  installed IDF versions and paths. `silico doctor` / `silico env --print`
  read it (dict-keyed `idfInstalled` schema) in addition to EIM's
  `eim_idf.json`. Check it before spending 20 minutes re-installing an IDF
  that is already on the machine.
- `silico doctor` (language=c) and `silico env --print` surface activation and tool paths when EIM/IDF is present.

## Sandbox / sudo

- Agent sandboxes often have **no interactive sudo**. Anything needing
  admin (driver install, `brew install` of casks, udev-ish permissions)
  must be front-loaded with the operator; don't discover it mid-flash.

## Serial

- CH9102: keep default identity probe **without** DTR/RTS pulse; do not run `monitor` and `inspect`/`deploy --verify` on the same port in parallel (port busy → clear HINT).
- After `idf.py flash`, wait for CDC re-enumeration before identity verify (silico deploy does this).

## Provenance

- Record start: `silico session start --mode evaluation --agent codex`
- Do not past-HEAD salvage product face from older commits; build from current HEAD (AGENTS **Product truth is HEAD**).
