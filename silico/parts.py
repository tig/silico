"""Part truth: pointers and parsers, not documents.

A GCU's ``parts.toml`` names the parts the product is built from and points at
where the truth about each one lives: the manufacturer datasheet, the SVD, the
devicetree binding, a reference driver. Silico never redistributes any of
those documents (they are free to download, not free to republish); it ships
the pointers and the parser, and ``silico parts --fetch`` pulls copies into a
git-ignored local cache for agent grounding. The licensing problem evaporates
because the user's own tools fetch the user's own copies.

Prefer machine-readable truth over PDFs when a part has it: an SVD or a
devicetree binding grounds an agent better than a 400-page datasheet, and the
community-patched ones carry errata the vendor PDFs do not.
"""

from __future__ import annotations

import re
import tomllib
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

# Pointer fields, in the order we report them. Each is a URL to truth we do
# not own and never commit.
POINTER_FIELDS = ("datasheet", "svd", "dt_binding", "docs", "driver", "errata")

CACHE_DIR = Path(".silico") / "parts"

# Part ids become cache path components and protocol keys: safe slugs only.
# Anything else (.., separators, spaces) is a path-traversal hole -- an id of
# "../../firmware" would write fetched documents into the repo tree.
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass
class Part:
    id: str
    name: str
    role: str = ""
    notes: str = ""
    # Optional silico board profile id (Day-1 product-face pin pack). See board_profile.
    profile: str = ""
    pointers: dict[str, str] = field(default_factory=dict)


@dataclass
class PartsReport:
    ok: bool
    parts: list[Part] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)


def _valid_url(value: str) -> bool:
    try:
        u = urlparse(value)
    except ValueError:
        return False
    return u.scheme in ("http", "https") and bool(u.netloc)


def load_parts(root: Path | None = None) -> PartsReport:
    """Parse and validate parts.toml. Offline; never touches the network."""
    root = (root or Path.cwd()).resolve()
    path = root / "parts.toml"
    lines: list[str] = []

    if not path.is_file():
        lines.append(
            "INFO: no parts.toml — add one so agents know where part truth "
            "lives (see silico AGENTS, Part truth)."
        )
        return PartsReport(True, [], lines)

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as e:
        return PartsReport(False, [], [f"FAIL: parts.toml unreadable: {e}"])

    raw_parts = data.get("part")
    if not isinstance(raw_parts, list) or not raw_parts:
        return PartsReport(
            False, [], ["FAIL: parts.toml has no [[part]] entries."]
        )

    ok = True
    parts: list[Part] = []
    seen: set[str] = set()
    for n, entry in enumerate(raw_parts, 1):
        pid = str(entry.get("id", "")).strip()
        name = str(entry.get("name", "")).strip()
        if not pid or not name:
            ok = False
            lines.append(f"FAIL: [[part]] #{n}: `id` and `name` are required.")
            continue
        if not _ID_RE.match(pid):
            ok = False
            lines.append(
                f"FAIL: [[part]] #{n}: id {pid!r} is not a safe slug "
                "(lowercase letters, digits, `-`, `_`; ids become cache paths)."
            )
            continue
        if pid in seen:
            ok = False
            lines.append(f"FAIL: duplicate part id `{pid}`.")
            continue
        seen.add(pid)

        pointers: dict[str, str] = {}
        for fieldname in POINTER_FIELDS:
            value = entry.get(fieldname)
            if value is None:
                continue
            value = str(value).strip()
            if not _valid_url(value):
                ok = False
                lines.append(
                    f"FAIL: {pid}.{fieldname} is not an http(s) URL: {value!r}"
                )
                continue
            pointers[fieldname] = value

        if not pointers:
            ok = False
            lines.append(
                f"FAIL: {pid} has no pointer fields "
                f"({', '.join(POINTER_FIELDS)}) — a part with no truth "
                "pointer cannot ground anything."
            )
            continue

        profile = str(entry.get("profile", "")).strip()
        if profile and not _ID_RE.match(profile):
            ok = False
            lines.append(
                f"FAIL: {pid}.profile {profile!r} is not a safe board-profile id "
                "(lowercase letters, digits, `-`, `_`)."
            )
            profile = ""

        parts.append(
            Part(
                id=pid,
                name=name,
                role=str(entry.get("role", "")).strip(),
                notes=str(entry.get("notes", "")).strip(),
                profile=profile,
                pointers=pointers,
            )
        )
        if profile:
            lines.append(
                f"  {pid}: board profile = {profile} "
                f"(silico board-profile show {profile})"
            )

    lines.append(f"parts.toml: {len(parts)} part(s) valid" + ("" if ok else ", with failures"))
    if ok:
        try:
            from silico.board_profile import report_for_parts

            lines.extend(report_for_parts(root))
        except Exception:
            pass
    return PartsReport(ok, parts, lines)


def _cache_name(fieldname: str, url: str) -> str:
    suffix = Path(urlparse(url).path).suffix
    return f"{fieldname}{suffix}" if suffix else fieldname


def fetch_parts(
    root: Path | None = None,
    *,
    fetcher=None,
    force: bool = False,
) -> PartsReport:
    """Fetch each pointer into .silico/parts/<id>/ (git-ignored, local-only).

    The cache exists so an agent can ground in the actual documents without
    silico ever redistributing them. It is per-checkout and disposable.
    """
    root = (root or Path.cwd()).resolve()
    report = load_parts(root)
    if not report.ok or not report.parts:
        return report

    if fetcher is None:
        def fetcher(url: str) -> bytes:  # pragma: no cover - network
            with urllib.request.urlopen(url, timeout=30) as resp:
                return resp.read()

    cache = root / CACHE_DIR
    # The cache ignores itself (the .pytest_cache trick): a dir-local
    # .gitignore of "*" keeps fetched documents uncommittable on every repo,
    # including GCUs scaffolded before this file existed, without touching
    # the user's own .gitignore.
    cache.mkdir(parents=True, exist_ok=True)
    keep_out = cache / ".gitignore"
    if not keep_out.exists():
        keep_out.write_text("*\n", encoding="utf-8")
    for part in report.parts:
        pdir = cache / part.id
        for fieldname, url in part.pointers.items():
            target = pdir / _cache_name(fieldname, url)
            if target.exists() and not force:
                report.lines.append(f"cached: {part.id}/{target.name}")
                continue
            try:
                blob = fetcher(url)
            except Exception as e:  # noqa: BLE001 — report, don't crash
                report.ok = False
                report.lines.append(f"FAIL: {part.id}.{fieldname}: fetch failed ({e})")
                continue
            pdir.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            report.lines.append(
                f"fetched: {part.id}/{target.name} ({len(blob)} bytes)"
            )
    report.lines.append(
        f"Cache: {cache} (git-ignored; local grounding copies, never committed)"
    )
    return report
