# Bàn giao asset tooling OpenCode → Codex

Codex nhận owner và tích hợp6heads đã liệt kê tại work order15 trong worktree riêng. Merge conflicts ở workflow được giải quyết bằng giữ cả coverage, migration, PNG import và full pack checks; README giữ các giới hạn mới thay phần mô tả v1 cũ. Không thay Muse art/.meta hoặc source canonical.

## Kiểm chứng thực tế

- `python Tools/AssetPack/run_all_checks.py`: **28/28logical checks đạt**, gọi **142validator +29preview/HTTP +37pack/unpack tests**. Windows có3symlink cases skipped do không có quyền tạo symlink; Linux CI vẫn cần chạy chúng.
- Pipeline đi qua audit hai lần/byte equality, pack hai lần/hash equality, unpack/reverify, bad manifests/draft gating/root confinement và HTTP layout6columns×8rows. Negative commands trả lỗi dự kiến không phải pipeline failure.
- Lượt đầu sparse checkout chưa include ArtManifests gây missing-input failures; đã bổ sung đúng tracked inputs và chạy lại toàn pipeline đạt. Không xóa input bắt buộc hoặc giảm assertion để xanh.
- `coverage_audit.py --check` tìm report2235variants cũ; regenerate ra2236 theo canonical main, sau đó check đạt với38evidence files. SHA/evidence digest trong regenerated report, Bilinear/static findings và engine-unverified vẫn giữ nguyên theo source.
- Headless Chrome thật chạy `browser_smoke.py` hai lần: fixture có nhãn và Muse `CHR_MINH_KIEM_WALK`. Cả hai render6×8/48×64, directionSE, animationwalk/currentFrame1; screenshot actor thật đính kèm `OpenCode_Takeover_Muse_Preview_20261031.png`.

Lệnh browser thực:

```sh
python Tools/AssetPreview/browser_smoke.py --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json --asset-id CHR_MINH_KIEM_WALK --path Client/Assets/Art/Characters/MinhKiem/minh_kiem_walk.png --direction SE --screenshot <output.png>
```

Đây là browser preview/structural acceptance, không là native Unity import/playback, full artwork approval hoặc full game. Asset hiện draft, pack release không có `--allow-draft` vẫn bị chặn. OPC11 WIP được bảo toàn và đang hoàn CLI/validation; OPC12 đang triển khai mới, được bàn giao ở PR kế tiếp có tests riêng.
