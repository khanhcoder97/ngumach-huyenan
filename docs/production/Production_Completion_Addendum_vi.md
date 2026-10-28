# Bổ sung hợp đồng sản xuất — 2026-10-28

Áp dụng cùng DEC-016 và Top_Down_Gameplay_World_Spec_vi.md. Các mục dưới khóa hành vi giữa hệ thống; chưa phải code đã có. Trước khi mở rộng P1, mỗi domain phải xuất schema/data đầy đủ và có bằng chứng runtime. Số lượng dòng CSV/ID không đại diện độ hoàn thiện.

## 1. Đủ nội dung để triển khai là gì

Mỗi feature cần: ID, điều kiện mở, input/output schema, trạng thái và transition, numeric config với đơn vị, quyền server, lỗi/cancel/retry, persistence/idempotency, asset/localization refs và tình huống nghiệm thu. Nội dung thiếu field bắt buộc phải fail export; không tự lấy số 0 hoặc giá trị mẫu.

| Domain | Đầu ra còn cần để khóa toàn game |
|---|---|
| Nhân vật/tiến trình | 5 class definitions; stats cấp 1–100, EXP 1–99, điểm phân phối, rank skill, respec phí/cap; không suy từ nhân vật demo HP100/MP50 |
| Combat | 30 active definitions; attack combo/dodge, damage order, armor normalization, status priority, boss stagger, unit conversion; các hệ số có nguồn |
| Quái/boss | entity definitions, HP/ATK/DEF theo band, footprint, AI states, phase thresholds, attack timelines, spawn ownership, reset và death/reward identity |
| Quest | 76 runtime definitions + step graph có guard/target/count/timeouts/checkpoints, từng objective placement; dialogue rows không thay objective graph |
| Item/forge | item template/variant precedence, affix pool weights, hidden/set stacking, recipe IDs, cost vectors, pity counters, binding/durability và transaction rules |
| Map/node | 46 topology bundles top-down, migration của 349 placements, nav/floor, portal rules, gather quota/yield; NEW_PROPOSED phải được review |
| Social/PvP | role permission table, roster/queue state, disconnect/forfeit, tie-break, scheduling timezone, reward cap và moderation flow |
| UI/assets/audio | screen-state inventory, navigation/focus, error keys, font tiếng Việt, asset manifest, sound event catalogue, device evidence |
| Backend/ops | identity ownership, session expiry, persistence migrations, restore, rollout compatibility, monitoring, load và release sign-off |

Không đặt % hoàn thành chung khi chưa có denominator và evidence theo domain.

## 2. Quest accept, tương tác và thưởng

Chốt hướng triển khai issue #20: POST /p1/quests/accept, X-Session-ID, Envelope hiện hành chứa {questId,npcId}; định nghĩa schema mới ở PR. Response result chứa QuestState hiện hành; inputSequence movement/combat không bị tiêu bởi accept.

Thứ tự guard: session hợp lệ → quest trong catalog → npc đúng startNpcId → actor/NPC cùng map và floor → khoảng cách chân <=5 WU và đường tương tác không bị chắn → prerequisites/level → AVAILABLE. Thành công AVAILABLE→ACTIVE, tăng quest revision đúng một lần; không đổi HP/MP/vị trí hay thưởng. Khi chưa có NPC world registry hoặc level profile, endpoint giữ feature flag off; không bỏ guard để gọi là production.

Lỗi: 400 invalid_payload, 404 session_not_found/quest_not_found, 422 npc_mismatch/out_of_range/prerequisite_not_met, 409 invalid_transition/revision_conflict. Error.data có thể bổ sung currentQuestState sau khi response schema được thống nhất; không trả state vào field chưa định nghĩa.

Idempotency scoped theo actor+operation+key, lưu request hash/result. Retry cùng payload/key trả kết quả đầu; cùng key khác payload trả 409 idempotency_conflict. Quest accept không dùng sequence thay dedupe. Quest objective nhận event server có sourceEventId duy nhất; client không gửi số lượng hoàn thành. Party progress dùng membership/range tại thời điểm event, không nhận bù sau khi vào party.

Turn-in xác thực đúng NPC/READY_TO_TURN_IN, tính reward từ bundle version đã gắn quest. Khóa state và inventory/ledger trong một transaction; ghi reward unique(actor,quest,resetBucket), cấp item/XP/currency và COMPLETE cùng commit. Túi đầy thì trả inventory_full và giữ READY; không tiêu quest item. Retry/disconnect không cấp hai lần. Side choices lưu trước grant, không được đổi lựa chọn bằng transport retry.

## 3. Item, giao dịch và lưu trữ

Preview forge/shop/trade không giữ giá trị authoritative; commit kiểm lại revision, quyền owner, bind/lock, slot/stack, costs/caps và bundleVersion. Integer currency/quantity; không dùng float để ghi sổ. Lock nhiều character theo thứ tự ID ổn định; lỗi giữa chừng rollback toàn bộ, không chỉ trả đồ bằng best effort.

Mua chợ: reservation listing có expiry, unique sale ID, escrow chuyển item+tiền+thuế cùng transaction. Listing bán rồi trả sold_out. Confirm trade mất hiệu lực khi bất kỳ offer thay revision; hai confirm phải tham chiếu cùng hash offer. Mail attachment chỉ claim một lần, unique(mailId,attachmentId,recipient).

Persistence cần migrations cho account-character ownership, item instance, currency ledger, reward ledger, quest state, quota bucket, idempotency và outbox. Mỗi mutation có expectedRevision; outbox chỉ phát sau commit. Restart phải khôi phục trạng thái đã commit; in-memory P1 không đáp ứng điều kiện này. Backup restore thực tế và schema rollback là gate trước alpha.

Public GitHub chỉ là chia sẻ source. API demo cho phép chọn characterId và giữ session in-memory không được xem là auth production. Server production ràng buộc character với principal; session ID không thay login. Không expose localhost demo ra internet để chơi thật trước auth/rate limits.

## 4. UI và asset nghiệm thu

Mọi panel có CLOSED/LOADING/READY/EMPTY/ERROR/SUBMITTING/STALE. SUBMITTING chặn double-click nhưng vẫn phải dedupe server. Đóng panel không hủy transaction đã commit; mở lại query snapshot. Error hiển thị messageKey và retry khi retryable, không tự resend purchase bằng key mới.

Một modal nhận focus; Esc đóng tầng trên, trả focus nút mở. Chat/text input chặn gameplay hotkeys. Nhãn dài và tiếng Việt có dấu không tràn; màu rarity có icon/text. Joystick không bị panel overlay bắt nhầm input. Settings preview có apply/cancel và rollback nếu profile mới làm viewport không dùng được.

Manifest art cần frameWidth/frameHeight, hướng, frame count, FPS, pivot số hóa, source refs và engine evidence tách riêng. `draft/approved` nói về review asset; không ngầm nghĩa đã DEVICE_QA. VFX/tileset/UI sheet không mặc định cần tám hướng; chỉ directional actor sheet cần 8. Validator chỉ đọc IHDR không chứng minh ảnh không corrupt, palette đúng hoặc các frame khác nhau.

Audio event cần stable ID, trigger, loop/stop, bus, volume, priority, max concurrent, spatial range và license/source. Combat cue mất âm vẫn có telegraph. P1 ưu tiên footsteps, hit, skill cast, warning, quest/UI, ambient mưa; không tự coi đã có audio vì spec mô tả âm thanh.

## 5. Vòng đời hoạt động và vận hành

Instance: CREATED→WAITING→ACTIVE→RESOLVING→CLOSED hoặc CANCELLED. Không phát reward từ cả RESOLVING và CLOSED. World boss mỗi spawn có encounterId mới; wipe giữ encounterId cho cùng attempt policy, reset attempt tăng attemptId; loot dedupe theo reward policy của activity. Quota daily/weekly theo account và bucket giờ Việt Nam, UTC lưu trữ; đổi map/nhân vật không reset.

PvP scoreboard freeze khi kết thúc; kết quả và reward cùng resultRevision. Disconnect áp dụng DEC-004; khi server hủy trận thì hoàn vé và không phạt bỏ trận; thao tác bồi hoàn cần unique compensationId. Công bằng camera theo DEC-016.

Mỗi release lưu commit, content bundle hash, schema version, artifact hash, test run URL, thiết bị, license evidence và known blockers. Thay đổi balancing ghi trước/sau và migration; không tái roll vật phẩm đã sở hữu khi đổi weight. Rollback content chỉ khi schema tương thích, không rollback ledger đã commit.

## 6. Gate thực tế

P1 chỉ đạt khi có Bến Mưa đi/đánh/nhận quest/nhận thưởng/trang bị/lưu và đăng nhập lại, hai client nhất quán, một boss đủ đòn và topo không kẹt. P2–P6 tiếp tục dùng QA release gates; code compile, 63 unit tests hoặc 5 CI xanh chỉ xác nhận phần chúng thực sự bao phủ. Hosting/CCU/store/legal cần owner quyết định trước release, không tự tạo chữ ký nghiệm thu.
