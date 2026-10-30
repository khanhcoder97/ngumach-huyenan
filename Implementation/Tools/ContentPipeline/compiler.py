#!/usr/bin/env python3
"""Assemble deterministic Bến Mưa candidate bundles (OPC-11).

The compiler reads only canonical documentation, CSV tables, schemas and
examples. It never writes canonical content and never activates runtime data.
Output bytes are canonical JSON (sorted keys, UTF-8, LF, no timestamps), so the
same inputs always produce the same bundle and digest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:  # Direct execution from the tool directory.
    from compiler_candidates import build_candidates
    from compiler_core import (
        BUNDLE_SCHEMA_PATH,
        DEFAULT_ROOT,
        KIND_ORDER,
        OUTPUT_REL,
        Context,
        PipelineError,
        SOURCE_SPECS,
        load_context,
    )
except ImportError:  # Import as part of the ContentPipeline package.
    from .compiler_candidates import build_candidates
    from .compiler_core import (
        BUNDLE_SCHEMA_PATH,
        DEFAULT_ROOT,
        KIND_ORDER,
        OUTPUT_REL,
        Context,
        PipelineError,
        SOURCE_SPECS,
        load_context,
    )

BUNDLE_ID = "BEN_MUA_CANDIDATES_V1"
TARGET_MAP_ID = "MAP_BEN_MUA"


def canonical_bytes(value) -> bytes:
    """Return the canonical UTF-8 bytes used for files and digests."""
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def digest_for(value) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def finalize_candidate(candidate: dict) -> dict:
    payload = {key: value for key, value in candidate.items() if key != "candidateDigest"}
    result = dict(payload)
    result["candidateDigest"] = digest_for(payload)
    return result


def assemble_bundle(ctx: Context, candidates: list[dict]) -> dict:
    finalized = [finalize_candidate(candidate) for candidate in candidates]
    finalized.sort(key=lambda item: (KIND_ORDER[item["kind"]], item["candidateId"]))

    blocked = [
        candidate
        for candidate in finalized
        if candidate["status"] == "BLOCKED_UNRESOLVED"
        or any(entry["blocking"] for entry in candidate["unresolved"])
    ]
    unresolved_count = sum(len(candidate["unresolved"]) for candidate in finalized)
    blocked_count = sum(1 for candidate in finalized if candidate["status"] == "BLOCKED_UNRESOLVED")
    ready_count = sum(1 for candidate in finalized if candidate["status"] == "READY_FOR_REVIEW")
    blocked_by_unresolved = bool(blocked)

    if blocked_by_unresolved:
        activation_reason = (
            f"Blocked by {unresolved_count} unresolved field(s) across {len(blocked)} candidate(s); "
            "the compiler never activates runtime data."
        )
    else:
        activation_reason = (
            "All candidate fields are sourced; Qoder/Codex review and a separate migration are "
            "still required before runtime activation."
        )

    bundle = {
        "schemaVersion": 1,
        "bundleFormat": 1,
        "bundleId": BUNDLE_ID,
        "targetMapId": TARGET_MAP_ID,
        "status": "BLOCKED_UNRESOLVED" if blocked_by_unresolved else "READY_FOR_REVIEW",
        "activation": {
            "eligible": not blocked_by_unresolved,
            "reason": activation_reason,
            "blockedByUnresolved": blocked_by_unresolved,
            "requiresReview": True,
            "runtimeActivationAllowed": False,
        },
        "summary": {
            "candidateCount": len(finalized),
            "readyCount": ready_count,
            "blockedCount": blocked_count,
            "unresolvedCount": unresolved_count,
        },
        "sources": [ctx.sources[source_id] for source_id in sorted(ctx.sources)],
        "candidates": finalized,
    }
    bundle["bundleDigest"] = digest_for(bundle)
    return bundle


def compile_bundle(root=DEFAULT_ROOT) -> tuple[Context, dict]:
    ctx = load_context(root)
    return ctx, assemble_bundle(ctx, build_candidates(ctx))


def output_path(root=DEFAULT_ROOT):
    return Path(root).resolve() / OUTPUT_REL


__all__ = [
    "BUNDLE_ID",
    "BUNDLE_SCHEMA_PATH",
    "DEFAULT_ROOT",
    "OUTPUT_REL",
    "SOURCE_SPECS",
    "TARGET_MAP_ID",
    "assemble_bundle",
    "canonical_bytes",
    "compile_bundle",
    "digest_for",
    "finalize_candidate",
    "output_path",
]
