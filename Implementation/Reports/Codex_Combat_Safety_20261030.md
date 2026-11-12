# Combat P1 — sửa correctness trước tích hợp client

Baseline Qoder: `32d57bcc4ad76e7a8cc1545bb73240fa454402ae` (PR75). Codex sửa trong worktree riêng `NGUMACHHUYENAN-server-review`; không chỉnh checkout root của Qoder. Đây là fix trên stack đang chờ review, không chứng nhận P1 online/production.

## Vấn đề và thay đổi

- **Replay sau END:** HTTP đã tái hiện cast mới phát CAST_START cursor1, END cursor2; replay nguyên body/key sau khi kết thúc trả cùng castId nhưng sinh thêm END cursor3. Scheduler đã xóa cast active nên cơ chế ContainsKey không còn chặn được replay. Domain outcome nay có `Replayed` nội bộ; endpoint trả receipt cũ và không gọi Schedule lại. Không thêm field vào wire.
- **Concurrent idempotency:** lookup/hash decision, validation, MP/CD/sequence và cache write nằm trong cùng actor critical section. Hai request cùng key/payload nhận cùng receipt, chỉ một fresh operation; cùng key/khác payload chỉ một operation accepted, request còn lại idempotency_conflict. Scope là một canonical PlayerSession; auth/single-owner durable identity và transaction DB vẫn chưa có.
- **Source invalidated:** tick phát CANCEL+END một lần và bỏ cast khi nguồn HP0 hoặc đã đổi map/floor trước impact; không gây damage hay kill credit từ cast bị hủy. Cast mới từ nguồn chết bị reject `actor_not_alive`409, không tiêu MP/CD/sequence hoặc tạo event. Đây không phải kiểm chứng LOS/multi-instance hay toàn bộ ordering guard/counter sau này.
- **Sequence:** chỉ bổ sung description cho `nextInputSequence`: tên wire v2 cũ trả last accepted sequence. Giữ nguyên giá trị/schema shape; client gửi sequence lớn hơn, không sửa thành seq+1 âm thầm.
- **Smoke:** kiểm completed replay sau END qua HTTP, chấp nhận END thật xen giữa CAST_START và kiểm cursor/order/correlation. Không phụ thuộc giả định mọi request đều xong trước tick kế.
- **Log:** startup ghi đúng tick subset đã nối; giữ nhãn DEV, REFERENCE_L5, synthetic topology và in-memory/XP-unapplied.

## Kiểm chứng

Lệnh chạy từ root worktree (SDK10.x; local dùng SDK portable10.0.403 đã kiểm SHA512, không cài Unity):

```text
dotnet build Server/Health/Health.csproj -c Release
dotnet run --no-build --project Server/Health/Health.csproj -c Release -- --self-check
python Implementation/Tools/validate_contracts.py
python Implementation/Tools/validate_content.py
python Server/Health/Smoke/smoke_p1.py http://127.0.0.1:15085
python Server/Health/Smoke/e2e_p1.py http://127.0.0.1:15085 dev
python Server/Health/Smoke/e2e_p1.py http://127.0.0.1:15084 default
```

DEV server: QuestAccept/Interact/QuestTurnIn/CombatV2/CombatDamage bật rõ; default server tắt các flag. Cả hai chỉ bind loopback, chạy từ `Server/Health`. Smoke/e2e có fixed fixture IDs, dùng server sạch cho một lượt smoke; không tái chạy trên state cũ rồi diễn giải cache fixture thành kết quả production.

Bằng chứng đợt trước guard-at-accept bổ sung:257self-check,448HTTPsmoke (số lần polling có thể thay đổi),176DEV E2E,9default E2E; client thật PR51 qua108assertions với tick damage/death và late replay. Lượt build cuối thêm guard-at-accept đạt258/258self-check,0errors; ba nullable warnings ở self-check kế thừa từ baseline. MK03/HTTP và fingerprints lượt tích hợp cuối được ghi ở report client; không lấy số đợt trước thay lượt cuối.

Race tests ép hai request bắt đầu khi actor đang khóa; khác skill/cùng key kiểm không double charge và conflict, không chỉ gọi retry tuần tự. Cancel tests có quái sống trong hình hit, lần lượt giết nguồn/đổi map/đổi floor trước tick hit, yêu cầu không impact/death/reward. Test marker không thay kiểm completed replay HTTP.

## Các giới hạn giữ nguyên

Chưa merge toàn stack53→75/main, chưa nội dung P00-02..05/boss/guard runtime/dash/group respawn đầy đủ; chưa durable auth/DB/restart recovery, loot/XP/equip HTTP đủ luồng; topology reviewed=0. Không đổi stat baseline198/102 thành fixture100/50, không mở public server, không gọi đây là full MMORPG. CI/core/HTTP không thay Unity compile/import/device evidence.
