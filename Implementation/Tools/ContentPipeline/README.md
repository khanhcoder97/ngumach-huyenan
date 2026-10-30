# Bến Mưa candidate compiler — Codex tiếp nhận OPC-11

Python3.12+, stdlib, không Unity/.NET. Compiler được hoàn thiện từ WIP OpenCode đã snapshot tại work order15. Input canonical chỉ đọc; output dưới `Implementation/Content/BuildCandidates/BEN_MUA/`. Đây là **ứng viên để review**, không runtime definitions và không chứng nhận đã chơi được5quests.

```sh
python Implementation/Tools/ContentPipeline/cli.py build
python Implementation/Tools/ContentPipeline/cli.py check
python Implementation/Tools/ContentPipeline/cli.py inspect
python Implementation/Tools/ContentPipeline/cli.py validate --require-ready
python Implementation/Tools/ContentPipeline/cli.py diff old.json new.json
python -m unittest discover -s Implementation/Tools/ContentPipeline/tests -v
```

`--root` cho checkout khác; `--bundle` chọn input cho check/validate/inspect; build hỗ trợ `--output` trong BuildCandidates hoặc scratch ngoài repo. Không ghi đè source canonical. Ghi atomically sau validation; build với `--require-ready` không ghi output khi blocked.

Exit0 = candidate structurally valid hoặc diff đã thực hiện;1 = invalid/drift/check mismatch;2 = thiếu/mất môi trường nguồn;3 = structurally valid nhưng còn blocking unresolved khi yêu cầu `--require-ready`. **Build mặc định có thể xuất candidate BLOCKED** cho review; đó không là release pass.

Snapshot đầu tiên:21candidates gồm5quest,5objective maps,1actor profile,3mob profiles,1boss reference và6item references.4ready-for-review/17blocked/56unresolved. Mỗi leaf có sourceRef/version/units/transform; candidate và bundle có digest. `activation.requiresReview=true`, `runtimeActivationAllowed=false` luôn giữ nguyên. Eligible chỉ nghĩa đủ dữ liệu để bước vào review, không được loader dùng như lệnh kích hoạt.

## Nguồn và độ chính xác

- SOURCE_SPECS trỏ Rules/P1Resolution/DEC023/QuestSpec/Atlas/registry/catalog và JSON baselines/examples, không browser save hoặc source dịch ngược.
- Quest graph là transcription có nguồn tách khỏi dialogue CSV. Không regex lời thoại thành progression. ID shorthand rõ trong Atlas như `OBJ_BM_WATER_RIPPLE_01/02/03` được expand riêng; không suy ra entity mới chỉ từ count.
- Fixed item master/rarity phải giống nguyên row cho mọi fixedID, gồm TOOL-ROD-01; duplicate/dangling/cycle/source/units/digest có validator. Những field chưa có số/ref giữ unresolved kèm source, không điền0.
- Digest text chuẩn UTF8-noBOM/LF để clone Windows/Linux cho cùng output. CSV parse giữ quoted multiline; canonical không bị sửa newline trên đĩa.
- `transcription_lock.json` khóa các nguồn đã đối chiếu với manual graph/numeric constants. Nguồn thay đổi phải review/re-transcribe và update lock trong cùng PR; CLI không có auto-approve/update-lock. Chỉ re-hash prose mới mà không kiểm numeric constants sẽ bị chặn.

Khi nguồn thay đổi: đọc diff nguồn → cập nhật transcription nếu cần → reviewer đối chiếu field provenance/units → cập nhật lock bằng cùng normalization → build/check/diff generated bundle → tests. Không cập nhật lock để che thiếu thiết kế. File schemas candidate là draft riêng; không sửa closed P1 contracts hoặc runtime exporter của Qoder.

## Consumer handoff

Qoder có thể đọc definition/fieldProvenance/unresolved để triển khai loader/adapter; phải kiểm digests và nguồn rồi review/migration riêng. Không tự copy một bundle blocked vào runtime, không bỏ required fields do thấy schema suppression dành cho unresolved candidate. Thay schemaVersion/targetSchema/kind hoặc runtime gate bị validator từ chối. Report/source snapshots lịch sử được giữ, không rewrite thành PASS.

P00-03 footwear được tìm đúng trong catalog (5class templates), còn cần class/rarity policy. Macro weapon P00-05 xuất CLASS_CONDITIONAL với5mapping canonical, không tự chọn class người chơi. Gear vectors đã có ở CSV; equipped-profile adapter vẫn là implementation gap, không được báo là thiếu stat source.
