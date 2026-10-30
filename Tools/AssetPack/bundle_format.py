#!/usr/bin/env python3
"""Shared, deterministic helpers for the OPC-09 bundle tools.

The audit, pack and unpack tools must agree on path safety, hashing, JSON
serialisation and the bundle digest. Keeping those rules in one module avoids
the tools drifting apart and makes the on-disk format reproducible.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BUNDLE_FORMAT_VERSION = 1
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
PATH_CHARS_RE = re.compile(r"^[A-Za-z0-9._~/-]+$")

ART_ROOTS = (
    "Client/Assets/Art",
    "Client/Assets/UI/Art",
    "Client/Assets/Tilemaps",
    "Client/Assets/VFX",
    "Client/Assets/Animation",
)


class BundleFormatError(Exception):
    """Raised for malformed manifests or unsafe paths."""


def load_json(path: Path):
    """Read UTF-8 JSON, rejecting Git LFS pointer content explicitly."""
    if not path.is_file():
        raise BundleFormatError(f"file not found: {path}")
    raw = path.read_bytes()
    if raw.startswith(LFS_POINTER_PREFIX):
        raise BundleFormatError(
            f"{path}: Git LFS pointer instead of file content "
            "(fetch the LFS objects; in CI use actions/checkout with lfs: true)"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BundleFormatError(f"{path}: not valid UTF-8 ({exc})") from exc
    try:
        return json.loads(text)
    except ValueError as exc:
        raise BundleFormatError(f"{path}: invalid JSON ({exc})") from exc


def inspect_repo_path(value):
    """Return ``(normalised repo-relative path, problem-or-None)``.

    Only forward-slash ASCII relative paths are accepted; empty, ``.``, ``..``
    and drive/UNC/absolute forms are rejected.
    """
    if not isinstance(value, str) or not value.strip():
        return None, "must be a non-empty string"
    if "\\" in value:
        return None, "must use forward slashes"
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return None, "must be relative to the repository root, not absolute"
    if not PATH_CHARS_RE.match(value):
        return None, "must only use ASCII letters, digits, dot, dash, underscore and slash"
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return None, "must not contain '.', '..' or empty segments"
    return "/".join(parts), None


def resolve_inside_root(root: Path, rel: str):
    """Resolve ``rel`` under ``root`` and reject symlink/reparse escapes."""
    root = Path(root).resolve()
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def resolve_input_path(root: Path, value, label: str = "path"):
    """Resolve a CLI input (relative or absolute) and confine it to ``root``.

    Returns ``(resolved_path, repo_relative_posix)``. Absolute paths are
    accepted only when they remain inside ``root``.
    """
    root = Path(root).resolve()
    raw = str(value)
    candidate = Path(raw)
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            rel = resolved.relative_to(root).as_posix()
        except ValueError as exc:
            raise BundleFormatError(f"{label} must be inside --root") from exc
        return resolved, rel
    rel, problem = inspect_repo_path(raw.replace("\\", "/"))
    if problem:
        raise BundleFormatError(f"invalid {label}: {problem}")
    resolved = resolve_inside_root(root, rel)
    if resolved is None:
        raise BundleFormatError(f"{label} escapes --root")
    return resolved, rel


def under_art_root(rel: str) -> bool:
    return any(rel == root or rel.startswith(root + "/") for root in ART_ROOTS)


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value) -> bytes:
    """Stable UTF-8 JSON: sorted keys, compact separators, trailing newline."""
    text = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return text.encode("utf-8")


def write_json(path: Path, value) -> None:
    """Write deterministic, human-readable JSON with a trailing newline."""
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2)
    Path(path).write_text(text + "\n", encoding="utf-8")


def compute_bundle_digest(entries) -> str:
    """SHA-256 over the sorted, canonical asset identity/hash records.

    Both the audit report and the packed ``bundle-manifest.json`` use this
    function, so their digests are directly comparable.
    """
    records = []
    for entry in entries:
        path = entry.get("path") or entry.get("resolvedPath")
        digest = entry.get("sha256")
        size = entry.get("sizeBytes")
        if not path or not digest or size is None:
            continue
        records.append(
            {
                "assetId": entry.get("assetId"),
                "path": path,
                "sizeBytes": int(size),
                "sha256": digest,
            }
        )
    records.sort(key=lambda item: (item["path"], item["assetId"] or ""))
    return hashlib.sha256(canonical_json_bytes(records)).hexdigest()


def manifest_assets(manifest) -> list:
    """Return the manifest ``assets`` array or raise a format error."""
    if not isinstance(manifest, dict):
        raise BundleFormatError("manifest root must be a JSON object")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise BundleFormatError("manifest 'assets' must be an array")
    return assets


def normalise_allowlist(values):
    """Normalise allowlist lines and reject unsafe/absolute entries."""
    normalised = set()
    for value in values:
        rel, problem = inspect_repo_path(value)
        if problem:
            raise BundleFormatError(f"invalid allowlist entry {value!r}: {problem}")
        normalised.add(rel)
    return normalised
