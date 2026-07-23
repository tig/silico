"""Board product-face pin packs (first-ship face candidates).

Agents should not invent GPIO maps from tribal knowledge alone. Silico ships
**board profiles** under ``silico/boards/`` with candidate pins for the
operator-observable **product face** (LED strip, speaker, …).

Workflow:
1. Name the board in ``parts.toml`` with ``profile = "<id>"`` (role = board).
2. ``silico board-profile`` / ``show`` — list candidates + knowledge pointers.
3. ``silico board-profile seed [--yes]`` — dry-run or write ``firmware/defaults.py``
   keys from ``[defaults_candidates]``.
4. Operator still confirms the **product face** on metal (AGENTS Stage D1).

These are **candidates**, not metal truth. Never claim first-ship metal done from a
profile alone.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from silico.parts import load_parts

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_ASSIGN_RE = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)(\s*(?:#.*)?)?$"
)


@dataclass
class BoardProfile:
    id: str
    name: str
    family: str = ""
    mcu: str = ""
    notes: str = ""
    product_face_summary: str = ""
    product_face: dict = field(default_factory=dict)
    defaults_candidates: dict[str, object] = field(default_factory=dict)
    pointers: dict[str, str] = field(default_factory=dict)
    path: Path | None = None


def profiles_root() -> Path:
    """Filesystem path to packaged board profiles."""
    try:
        root = resources.files("silico").joinpath("boards")
        if root.is_dir():
            return Path(str(root))
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    cand = here / "boards"
    if cand.is_dir():
        return cand
    raise FileNotFoundError("silico board profiles tree not found (silico/boards)")


def list_profiles() -> list[BoardProfile]:
    root = profiles_root()
    out: list[BoardProfile] = []
    for path in sorted(root.glob("*.toml")):
        try:
            out.append(_load_path(path))
        except Exception:
            continue
    return out


def load_profile(profile_id: str) -> BoardProfile:
    pid = (profile_id or "").strip()
    if not _ID_RE.match(pid):
        raise FileNotFoundError(f"unknown board profile {profile_id!r}")
    path = profiles_root() / f"{pid}.toml"
    if not path.is_file():
        known = ", ".join(p.id for p in list_profiles()) or "(none)"
        raise FileNotFoundError(
            f"unknown board profile {pid!r}; known: {known}"
        )
    return _load_path(path)


def _load_path(path: Path) -> BoardProfile:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    pid = str(data.get("id") or path.stem).strip()
    face = data.get("product_face") or {}
    if not isinstance(face, dict):
        face = {}
    cands = data.get("defaults_candidates") or {}
    if not isinstance(cands, dict):
        cands = {}
    ptrs = data.get("pointers") or {}
    if not isinstance(ptrs, dict):
        ptrs = {}
    return BoardProfile(
        id=pid,
        name=str(data.get("name") or pid).strip(),
        family=str(data.get("family") or "").strip(),
        mcu=str(data.get("mcu") or "").strip(),
        notes=str(data.get("notes") or "").strip(),
        product_face_summary=str(face.get("summary") or "").strip(),
        product_face={k: face[k] for k in face},
        defaults_candidates={str(k): cands[k] for k in cands},
        pointers={str(k): str(v) for k, v in ptrs.items() if v},
        path=path,
    )


def resolve_profile_id(root: Path | None = None) -> str | None:
    """Return board profile id from parts.toml (role=board with profile=)."""
    report = load_parts(root)
    boards = [
        p
        for p in report.parts
        if getattr(p, "profile", "") and p.role == "board"
    ]
    if boards:
        return boards[0].profile
    any_p = [p for p in report.parts if getattr(p, "profile", "")]
    if any_p:
        return any_p[0].profile
    return None


def show_profile_lines(profile: BoardProfile) -> list[str]:
    lines = [
        f"Board profile: {profile.id} — {profile.name}",
    ]
    if profile.family or profile.mcu:
        lines.append(
            f"  family={profile.family or '-'}  mcu={profile.mcu or '-'}"
        )
    if profile.notes:
        lines.append(f"  notes: {profile.notes}")
    if profile.product_face_summary:
        lines.append(f"  product face: {profile.product_face_summary}")
    face = profile.product_face
    if face.get("led_pin") is not None:
        role = face.get("led_role") or "status LED / strip"
        lines.append(f"  LED_PIN candidate: {face['led_pin']} ({role})")
    if face.get("speaker_pin") is not None:
        role = face.get("speaker_role") or "speaker"
        lines.append(
            f"  SPEAKER_PIN candidate: {face['speaker_pin']} ({role})"
        )
    if profile.defaults_candidates:
        lines.append("  defaults.py candidates (seed with board-profile seed):")
        for k, v in profile.defaults_candidates.items():
            lines.append(f"    {k} = {v!r}")
    if profile.pointers:
        lines.append("  pointers:")
        for k, v in profile.pointers.items():
            lines.append(f"    {k}: {v}")
    lines.append(
        "  These are **candidates**. Confirm the product face on metal "
        "(operator see/hear) before first-ship metal done."
    )
    return lines


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return repr(value)
    return repr(value)


def seed_defaults_candidates(
    root: Path | None = None,
    *,
    profile_id: str | None = None,
    yes: bool = False,
    defaults_path: Path | None = None,
) -> tuple[list[str], bool]:
    """Seed firmware/defaults.py from a board profile's defaults_candidates.

    Default is dry-run (yes=False). Returns (lines, changed).
    """
    root = (root or Path.cwd()).resolve()
    lines: list[str] = []
    pid = (profile_id or resolve_profile_id(root) or "").strip()
    if not pid:
        lines.append(
            "FAIL: no board profile id. Pass an id (e.g. m5go) or set "
            "profile = \"…\" on a role=board part in parts.toml."
        )
        return lines, False

    try:
        profile = load_profile(pid)
    except FileNotFoundError as e:
        lines.append(f"FAIL: {e}")
        return lines, False

    cands = profile.defaults_candidates
    if not cands:
        lines.append(f"FAIL: profile {pid!r} has no [defaults_candidates].")
        return lines, False

    path = defaults_path or (root / "firmware" / "defaults.py")
    if not path.is_file():
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        lines.append(f"FAIL: {rel} missing — scaffold plate first.")
        return lines, False

    lines.extend(show_profile_lines(profile))
    text = path.read_text(encoding="utf-8")
    original = text
    plan: list[str] = []
    out_lines = text.splitlines(keepends=True)
    if out_lines and not out_lines[-1].endswith("\n"):
        out_lines[-1] = out_lines[-1] + "\n"

    for key, value in cands.items():
        new_rhs = _format_value(value)
        found = False
        for i, line in enumerate(out_lines):
            m = _ASSIGN_RE.match(line.rstrip("\n\r"))
            if not m or m.group(1) != key:
                continue
            found = True
            old_rhs = m.group(2).strip()
            comment = m.group(3) or ""
            if old_rhs == new_rhs:
                plan.append(f"unchanged: {key} = {new_rhs}")
            else:
                plan.append(f"change: {key}: {old_rhs} -> {new_rhs}")
                out_lines[i] = f"{key} = {new_rhs}{comment}\n"
            break
        if not found:
            plan.append(f"add: {key} = {new_rhs}")
            out_lines.append(
                f"\n# From board profile {pid} (candidate — confirm product face)\n"
            )
            out_lines.append(f"{key} = {new_rhs}\n")

    text = "".join(out_lines)
    lines.append(f"Target: {path}")
    lines.extend(f"  {p}" for p in plan)

    if original == text:
        lines.append("OK: defaults already match profile candidates.")
        lines.append(
            "Still confirm product face on metal with the operator "
            "(see/hear), not only pin numbers."
        )
        return lines, False

    if not yes:
        lines.append(
            "dry-run: no write. Re-run with --yes after operator confirms "
            "this board profile is the right first-ship face map."
        )
        lines.append(
            "Would update firmware/defaults.py; host gate + redeploy still required."
        )
        return lines, False

    path.write_text(text, encoding="utf-8")
    lines.append(f"wrote: {path.name} from board profile {pid}")
    lines.append(
        "Next: host gate (pytest -q), then operator-confirmed deploy; "
        "confirm they can see/hear the product face before first-ship metal done."
    )
    return lines, True


def report_for_parts(root: Path | None = None) -> list[str]:
    """Extra lines for ``silico parts`` when a board profile is linked."""
    root = (root or Path.cwd()).resolve()
    pid = resolve_profile_id(root)
    if not pid:
        return [
            "INFO: no board profile on parts.toml — set profile = \"m5go\" "
            "(or other id) on the role=board part for first-ship face pin packs. "
            "List: silico board-profile"
        ]
    try:
        profile = load_profile(pid)
    except FileNotFoundError as e:
        return [f"WARN: parts.toml profile {pid!r}: {e}"]
    lines = [f"board profile from parts.toml: {pid}"]
    lines.extend(show_profile_lines(profile)[1:])  # skip duplicate header
    lines.append(
        "Seed defaults candidates: silico board-profile seed "
        f"{pid}   (dry-run; add --yes after operator confirm)"
    )
    return lines
