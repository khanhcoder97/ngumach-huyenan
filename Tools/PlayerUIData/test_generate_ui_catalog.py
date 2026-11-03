"""Tests for generate_ui_catalog.py (M2). Run: python Tools/PlayerUIData/test_generate_ui_catalog.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GEN = os.path.join(ROOT, "Tools", "PlayerUIData", "generate_ui_catalog.py")
OUT = os.path.join(ROOT, "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json")


def run_gen():
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    return r


def test_runs_ok():
    r = run_gen()
    assert r.returncode == 0, r.stderr
    assert os.path.isfile(OUT)


def test_deterministic():
    run_gen()
    a = open(OUT, "rb").read()
    run_gen()
    b = open(OUT, "rb").read()
    assert a == b, "generator not deterministic"


def test_count_and_digest():
    run_gen()
    data = json.load(open(OUT, encoding="utf-8"))
    assert data["count"] == len(data["entries"])
    assert data["count"] > 2000
    ids = [e["item_id"] for e in data["entries"]]
    assert ids == sorted(ids)
    assert len(set(ids)) == len(ids)
    for e in data["entries"]:
        assert "digest" in e and len(e["digest"]) == 64
        assert "_source" in e and "file" in e["_source"] and "row" in e["_source"]


def _run_in_tmp(tmp_root, csv_content_variant, csv_content_master):
    docs = os.path.join(tmp_root, "docs", "production")
    os.makedirs(docs, exist_ok=True)
    with open(os.path.join(docs, "Item_Rarity_Variant_Catalog_vi.csv"), "w", encoding="utf-8") as f:
        f.write(csv_content_variant)
    with open(os.path.join(docs, "Item_Master_Catalog_vi.csv"), "w", encoding="utf-8") as f:
        f.write(csv_content_master)
    gen_dir = os.path.join(tmp_root, "Tools", "PlayerUIData")
    os.makedirs(gen_dir, exist_ok=True)
    gen_tmp = os.path.join(gen_dir, "generate_ui_catalog.py")
    shutil.copy(GEN, gen_tmp)
    return subprocess.run([sys.executable, gen_tmp], capture_output=True, text=True)


def test_no_duplicate_keys_fail():
    tmp_root = tempfile.mkdtemp()
    try:
        r = _run_in_tmp(tmp_root, '"item_id","display_name"\n"X","a"\n"X","b"\n', '"item_id","display_name"\n')
        assert r.returncode != 0, "duplicate key did not fail"
        assert "duplicate item_id within file" in (r.stderr + r.stdout)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_empty_input_fails():
    tmp_root = tempfile.mkdtemp()
    try:
        r = _run_in_tmp(tmp_root, '"item_id","display_name"\n', '"item_id","display_name"\n')
        assert r.returncode != 0, "empty input did not fail"
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_missing_field_does_not_crash():
    run_gen()
    data = json.load(open(OUT, encoding="utf-8"))
    for e in data["entries"]:
        for k in ("item_id", "display_name", "binding", "tradeable"):
            assert k in e


def test_identical_shared_row_kept_once_with_provenance():
    """Cross-file identical rows are allowed: one entry, first file's provenance."""
    tmp_root = tempfile.mkdtemp()
    try:
        variant = '"item_id","display_name","category"\n"SHARED","Cung","Vũ khí"\n'
        master = '"item_id","display_name","category"\n"SHARED","Cung","Vũ khí"\n'
        r = _run_in_tmp(tmp_root, variant, master)
        assert r.returncode == 0, r.stderr
        out = os.path.join(tmp_root, "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json")
        data = json.load(open(out, encoding="utf-8"))
        assert data["count"] == 1
        assert data["entries"][0]["_source"]["file"] == "Item_Rarity_Variant_Catalog_vi.csv"
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_conflicting_shared_row_fails():
    """Same item_id but different content across files must fail loudly."""
    tmp_root = tempfile.mkdtemp()
    try:
        variant = '"item_id","display_name","category"\n"SHARED","Cung","Vũ khí"\n'
        master = '"item_id","display_name","category"\n"SHARED","Kiếm","Vũ khí"\n'
        r = _run_in_tmp(tmp_root, variant, master)
        assert r.returncode != 0, "conflicting shared row did not fail"
        assert "conflicting shared item_id" in (r.stderr + r.stdout)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def test_check_detects_stale_without_writing():
    """--check is read-only and exits 1 when the committed catalog drifted."""
    tmp_root = tempfile.mkdtemp()
    try:
        r = _run_in_tmp(tmp_root, '"item_id","display_name"\n"A","a"\n', '"item_id","display_name"\n"B","b"\n')
        assert r.returncode == 0, r.stderr
        out = os.path.join(tmp_root, "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json")
        committed = open(out, "rb").read()
        tampered = committed + b" \n"
        open(out, "wb").write(tampered)

        gen_tmp = os.path.join(tmp_root, "Tools", "PlayerUIData", "generate_ui_catalog.py")
        check = subprocess.run([sys.executable, gen_tmp, "--check"], capture_output=True, text=True)
        assert check.returncode != 0, "stale catalog passed --check"
        assert "STALE" in (check.stderr + check.stdout)
        assert open(out, "rb").read() == tampered, "--check must not rewrite the committed file"
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    tests = [test_runs_ok, test_deterministic, test_count_and_digest,
             test_no_duplicate_keys_fail, test_empty_input_fails, test_missing_field_does_not_crash,
             test_identical_shared_row_kept_once_with_provenance,
             test_conflicting_shared_row_fails,
             test_check_detects_stale_without_writing]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL: {t.__name__}: {e}")
    sys.exit(1 if failed else 0)
