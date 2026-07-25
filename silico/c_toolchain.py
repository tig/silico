"""Espressif C-toolchain discovery (language=c host path).

Agents should not hand-parse ``eim_idf.json`` or re-probe
``C:\\Espressif\\tools`` every shell. ``silico doctor`` and ``silico env --print``
surface activation scripts and resolved tool paths (tig/silico#79).

Two catalogs exist in the field:

* **EIM** (``eim_idf.json``): list-shaped ``idfInstalled`` with activation
  scripts (Windows-first).
* **idf_tools.py** (``~/.espressif/idf-env.json``): dict-shaped
  ``idfInstalled`` keyed by install id — the normal macOS/Linux
  ``install.sh`` result. A pre-installed IDF registered here is invisible on
  PATH until ``export.sh`` is sourced; discovery must find it before
  concluding "no ESP-IDF" (tig/silico#87).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Espressif Install Manager (EIM) default roots (Windows + portable).
_EIM_JSON_CANDIDATES = (
    Path(r"C:\Espressif\tools\eim_idf.json"),
    Path(r"C:\Espressif\eim_idf.json"),
)


@dataclass
class IdfInstall:
    name: str
    path: str  # IDF_PATH
    idf_tools_path: str
    activation_script: str
    python: str
    id: str = ""


@dataclass
class CToolchainReport:
    ok: bool
    lines: list[str] = field(default_factory=list)
    installs: list[IdfInstall] = field(default_factory=list)
    selected: IdfInstall | None = None
    cmake: str | None = None
    ninja: str | None = None
    idf_py: str | None = None
    eim_json: Path | None = None
    idf_env_json: Path | None = None


def eim_json_search_paths(
    *,
    env: dict[str, str] | None = None,
    extra: list[Path] | None = None,
) -> list[Path]:
    """Ordered paths to probe for EIM's eim_idf.json."""
    env = env if env is not None else os.environ
    out: list[Path] = []
    if extra:
        out.extend(extra)
    tools = env.get("IDF_TOOLS_PATH")
    if tools:
        out.append(Path(tools) / "eim_idf.json")
        out.append(Path(tools).parent / "eim_idf.json")
    idf = env.get("IDF_PATH")
    if idf:
        # uncommon, but allow IDF tree adjacent tools
        out.append(Path(idf).parent.parent / "tools" / "eim_idf.json")
    out.extend(_EIM_JSON_CANDIDATES)
    # de-dupe preserving order
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def find_eim_json(
    *,
    env: dict[str, str] | None = None,
    extra: list[Path] | None = None,
) -> Path | None:
    for p in eim_json_search_paths(env=env, extra=extra):
        if p.is_file():
            return p
    return None


def parse_eim_idf_json(data: dict) -> tuple[list[IdfInstall], str | None]:
    """Parse EIM eim_idf.json body → (installs, selected_id)."""
    raw = data.get("idfInstalled") or []
    installs: list[IdfInstall] = []
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            path = str(item.get("path") or "").strip()
            if not path:
                continue
            installs.append(
                IdfInstall(
                    name=str(item.get("name") or "").strip() or path,
                    path=path,
                    idf_tools_path=str(item.get("idfToolsPath") or "").strip(),
                    activation_script=str(item.get("activationScript") or "").strip(),
                    python=str(item.get("python") or "").strip(),
                    id=str(item.get("id") or "").strip(),
                )
            )
    selected = data.get("idfSelectedId")
    selected_id = str(selected).strip() if selected else None
    return installs, selected_id


def load_eim_installs(
    path: Path | None = None,
    *,
    env: dict[str, str] | None = None,
    extra: list[Path] | None = None,
) -> tuple[Path | None, list[IdfInstall], str | None]:
    """Load installs from *path* or auto-discovered eim_idf.json."""
    p = path or find_eim_json(env=env, extra=extra)
    if p is None or not p.is_file():
        return None, [], None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return p, [], None
    if not isinstance(data, dict):
        return p, [], None
    installs, selected_id = parse_eim_idf_json(data)
    return p, installs, selected_id


def select_install(
    installs: list[IdfInstall],
    selected_id: str | None,
) -> IdfInstall | None:
    if not installs:
        return None
    if selected_id:
        for inst in installs:
            if inst.id == selected_id:
                return inst
    return installs[0]


# --- idf_tools.py catalog (~/.espressif/idf-env.json) — macOS/Linux (#87) ---


def idf_env_search_paths(
    *,
    env: dict[str, str] | None = None,
    extra: list[Path] | None = None,
) -> list[Path]:
    """Ordered paths to probe for idf_tools.py's idf-env.json."""
    env = env if env is not None else os.environ
    out: list[Path] = []
    if extra:
        out.extend(extra)
    tools = env.get("IDF_TOOLS_PATH")
    if tools:
        out.append(Path(tools) / "idf-env.json")
    out.append(Path.home() / ".espressif" / "idf-env.json")
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def find_idf_env_json(
    *,
    env: dict[str, str] | None = None,
    extra: list[Path] | None = None,
) -> Path | None:
    for p in idf_env_search_paths(env=env, extra=extra):
        if p.is_file():
            return p
    return None


def _python_env_for(espressif_root: Path | None, version: str) -> str:
    """Best python under <root>/python_env for an IDF *version* (e.g. '5.3')."""
    if espressif_root is None:
        return ""
    env_root = espressif_root / "python_env"
    if not env_root.is_dir():
        return ""
    exact: list[Path] = []
    other: list[Path] = []
    for d in sorted(env_root.iterdir()):
        if not d.is_dir():
            continue
        py = d / "bin" / "python"
        if not py.is_file():
            py = d / "Scripts" / "python.exe"
            if not py.is_file():
                continue
        if version and d.name.startswith(f"idf{version}_"):
            exact.append(py)
        else:
            other.append(py)
    # Prefer an env matching the install's version; latest name wins either way.
    if exact:
        return str(exact[-1])
    if other:
        return str(other[-1])
    return ""


def parse_idf_env_json(
    data: dict,
    *,
    espressif_root: Path | None = None,
) -> tuple[list[IdfInstall], str | None]:
    """Parse idf_tools.py idf-env.json body → (installs, selected_id).

    Schema differs from EIM: ``idfInstalled`` is a **dict** keyed by install
    id, each value carrying ``version`` and ``path``. The bash activation is
    the install's ``export.sh`` (there is no activationScript field).
    """
    raw = data.get("idfInstalled")
    installs: list[IdfInstall] = []
    if isinstance(raw, dict):
        for key, item in raw.items():
            if not isinstance(item, dict):
                continue
            path = str(item.get("path") or "").strip()
            if not path:
                continue
            version = str(item.get("version") or "").strip()
            export_sh = Path(path) / "export.sh"
            installs.append(
                IdfInstall(
                    name=f"ESP-IDF {version}".strip() if version else path,
                    path=path,
                    idf_tools_path=str(espressif_root) if espressif_root else "",
                    activation_script=str(export_sh) if export_sh.is_file() else "",
                    python=_python_env_for(espressif_root, version),
                    id=str(key),
                )
            )
    selected = data.get("idfSelectedId")
    selected_id = str(selected).strip() if selected else None
    return installs, selected_id


def load_idf_env_installs(
    path: Path | None = None,
    *,
    env: dict[str, str] | None = None,
    extra: list[Path] | None = None,
) -> tuple[Path | None, list[IdfInstall], str | None]:
    """Load installs from *path* or auto-discovered idf-env.json."""
    p = path or find_idf_env_json(env=env, extra=extra)
    if p is None:
        return None, [], None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return p, [], None
    if not isinstance(data, dict):
        return p, [], None
    installs, selected_id = parse_idf_env_json(data, espressif_root=p.parent)
    return p, installs, selected_id


def _which_under(tools_root: Path | None, name: str) -> str | None:
    """Find *name* on PATH or under Espressif tools trees.

    Prefer the EIM layout (``tools/<name>/<ver>/bin/<name>``) before a full
    recursive scan — walking all of ``C:\\Espressif\\tools`` is slow (PR #80 CR).
    """
    found = shutil.which(name)
    if found:
        return found
    if tools_root is None or not tools_root.is_dir():
        return None
    # Narrow first: EIM layout tools/cmake/<ver>/bin/cmake[.exe]
    narrow = [
        f"{name}/*/bin/{name}.exe",
        f"{name}/*/bin/{name}",
        f"{name}/*/{name}.exe",
        f"{name}/*/{name}",
    ]
    for pat in narrow:
        for hit in tools_root.glob(pat):
            if hit.is_file():
                return str(hit)
    # Fallback: broader scan only if the tool is not in the usual place
    broad = [
        f"**/{name}.exe",
        f"**/{name}",
    ]
    for pat in broad:
        for hit in tools_root.glob(pat):
            if hit.is_file():
                return str(hit)
    return None


def resolve_tools(install: IdfInstall | None) -> tuple[str | None, str | None, str | None]:
    """Return (cmake, ninja, idf_py) paths for *install* (or PATH-only if None)."""
    tools_root = Path(install.idf_tools_path) if install and install.idf_tools_path else None
    cmake = _which_under(tools_root, "cmake")
    ninja = _which_under(tools_root, "ninja")
    idf_py = shutil.which("idf.py")
    if not idf_py and install and install.path:
        cand = Path(install.path) / "tools" / "idf.py"
        if cand.is_file():
            idf_py = str(cand)
    return cmake, ninja, idf_py


def discover_c_toolchain(
    *,
    env: dict[str, str] | None = None,
    eim_json: Path | None = None,
    extra_json_paths: list[Path] | None = None,
) -> CToolchainReport:
    """Full discovery report for doctor / env print."""
    env = env if env is not None else dict(os.environ)
    lines: list[str] = []
    path, installs, selected_id = load_eim_installs(
        eim_json, env=env, extra=extra_json_paths
    )
    selected = select_install(installs, selected_id)

    # Fall back to idf_tools.py's ~/.espressif/idf-env.json (macOS/Linux, #87):
    # a pre-installed IDF lives there without touching PATH or IDF_PATH.
    idf_env_path: Path | None = None
    if selected is None:
        idf_env_path, env_installs, env_selected_id = load_idf_env_installs(env=env)
        if env_installs:
            installs = env_installs
            selected = select_install(env_installs, env_selected_id)
    cmake, ninja, idf_py = resolve_tools(selected)

    # Fall back to env IDF_PATH if catalogs missing but IDF is active
    if selected is None and env.get("IDF_PATH"):
        selected = IdfInstall(
            name="IDF_PATH",
            path=env["IDF_PATH"],
            idf_tools_path=env.get("IDF_TOOLS_PATH") or "",
            activation_script="",
            python=sys.executable,
        )
        cmake, ninja, idf_py = resolve_tools(selected)

    report = CToolchainReport(
        ok=bool(selected and (idf_py or selected.path)),
        lines=lines,
        installs=installs,
        selected=selected,
        cmake=cmake,
        ninja=ninja,
        idf_py=idf_py,
        eim_json=path,
        idf_env_json=idf_env_path,
    )
    return report


def doctor_c_toolchain_lines(
    *,
    env: dict[str, str] | None = None,
    eim_json: Path | None = None,
) -> list[str]:
    """Lines for ``silico doctor`` when language=c (or always as optional section)."""
    r = discover_c_toolchain(env=env, eim_json=eim_json)
    lines: list[str] = []
    if r.eim_json:
        lines.append(f"EIM catalog: {r.eim_json}")
    elif r.idf_env_json:
        lines.append(f"IDF catalog: {r.idf_env_json} (idf_tools.py install.sh)")
    else:
        lines.append(
            "INFO: no ESP-IDF catalog found (checked eim_idf.json under "
            "IDF_TOOLS_PATH / C:\\Espressif\\tools, and ~/.espressif/idf-env.json). "
            "Install ESP-IDF (install.sh / EIM) or export IDF_PATH."
        )
    if r.installs:
        lines.append(f"IDF installs known: {len(r.installs)}")
        for inst in r.installs:
            mark = " (selected)" if r.selected and inst.id == r.selected.id else ""
            lines.append(f"  - {inst.name}: {inst.path}{mark}")
    if r.selected:
        lines.append(f"Active IDF: {r.selected.name} @ {r.selected.path}")
        if r.selected.activation_script:
            lines.append(f"  activation: {r.selected.activation_script}")
            if r.selected.activation_script.endswith(".sh"):
                lines.append(
                    '  bash/zsh: . "' + r.selected.activation_script + '"'
                )
            else:
                lines.append(
                    "  PowerShell: . '" + r.selected.activation_script.replace("'", "''") + "'"
                )
        if r.selected.idf_tools_path:
            lines.append(f"  IDF_TOOLS_PATH: {r.selected.idf_tools_path}")
        if r.selected.python:
            lines.append(f"  IDF python: {r.selected.python}")
    else:
        lines.append("WARN: no ESP-IDF install resolved for this host")
    lines.append(f"  cmake: {r.cmake or '(not found)'}")
    lines.append(f"  ninja: {r.ninja or '(not found)'}")
    lines.append(f"  idf.py: {r.idf_py or '(not found)'}")
    if r.selected and r.selected.activation_script and not r.cmake:
        lines.append(
            "HINT: cmake missing on PATH — activate the EIM script above in this shell, "
            "or run: silico env --print"
        )
    # macOS / Codex: PowerShell export.ps1 often breaks idf.py paths (#84).
    if sys.platform == "darwin":
        lines.append(
            "HINT (macOS/Codex): prefer bash or shell-free `python -m`/`idf.py` after "
            "sourcing export.sh — PowerShell export.ps1 may emit Windows-style paths."
        )
        py_ver = sys.version_info
        if py_ver < (3, 11):
            lines.append(
                f"WARN: this Python is {py_ver.major}.{py_ver.minor}; ESP-IDF 5.3+ "
                "often needs 3.11+ (set IDF_PYTHON_ENV_PATH to an idf*_py3.12_env)."
            )
        idf_py_env = (env or os.environ).get("IDF_PYTHON_ENV_PATH", "")
        if idf_py_env:
            lines.append(f"  IDF_PYTHON_ENV_PATH: {idf_py_env}")
        else:
            lines.append(
                "INFO: IDF_PYTHON_ENV_PATH unset — if install.sh used system Python 3.9, "
                "re-run with a 3.12 interpreter first (see knowledge/macos-codex-esp-idf.md)."
            )
    return lines


def env_print_block(
    *,
    env: dict[str, str] | None = None,
    eim_json: Path | None = None,
    shell: str | None = None,
) -> list[str]:
    """Emit shell assignments agents can apply (PowerShell default on Windows)."""
    r = discover_c_toolchain(env=env, eim_json=eim_json)
    if shell is None:
        shell = "powershell" if sys.platform == "win32" else "bash"
    shell = shell.lower()
    lines: list[str] = []
    if not r.selected:
        lines.append("# No IDF install resolved. Install Espressif EIM or set IDF_PATH.")
        return lines
    idf_path = r.selected.path
    tools = r.selected.idf_tools_path
    if shell in ("powershell", "pwsh", "ps1"):
        lines.append(f"$env:IDF_PATH = '{idf_path}'")
        if tools:
            lines.append(f"$env:IDF_TOOLS_PATH = '{tools}'")
        if r.selected.activation_script:
            lines.append(f". '{r.selected.activation_script}'")
        else:
            lines.append("# No activationScript in EIM catalog — export PATH to cmake/ninja manually.")
        if r.cmake:
            lines.append(f"# cmake -> {r.cmake}")
        if r.ninja:
            lines.append(f"# ninja -> {r.ninja}")
        if r.idf_py:
            lines.append(f"# idf.py -> {r.idf_py}")
    else:
        lines.append(f'export IDF_PATH="{idf_path}"')
        if tools:
            lines.append(f'export IDF_TOOLS_PATH="{tools}"')
        if r.selected.activation_script and r.selected.activation_script.endswith(".sh"):
            lines.append(f". \"{r.selected.activation_script}\"")
        if r.cmake:
            lines.append(f"# cmake -> {r.cmake}")
        if r.ninja:
            lines.append(f"# ninja -> {r.ninja}")
    return lines
