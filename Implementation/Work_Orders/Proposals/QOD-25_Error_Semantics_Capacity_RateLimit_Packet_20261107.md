# QOD-25 — Ngữ nghĩa lỗi, dung lượng/retention và biên rate-limit

Gói 31 Q5, head `ce93db6`, ngày 07/11/2026. **Không sửa code, không đổi wire vocabulary,
không bật gate, không tự đặt số quota.** Toàn bộ số liệu dưới đây đo lại từ nguồn ở head này
bằng chính các lệnh ghi ở mục 6.

## 1. 13 mã canonical của `Production_Technical_Contracts_vi.md` so với 62 mã server khai báo

`DEC-TUTORIAL-TRANSPORT-20261106` giữ wire error hiện hành: **không rename 62 mã sang 13 mã
chung**, không đồng nhất `session_not_found` với `CHARACTER_NOT_FOUND`. Vì vậy bảng này là
*ánh ngữ nghĩa*, không phải kế hoạch đổi tên.

| Canonical | Trạng thái đo được | Nơi khai báo | Đề xuất xử lý |
| --- | --- | --- | --- |
| `REVISION_CONFLICT` | có, trùng tên | `Equipment.cs` (`revision_conflict`) | giữ nguyên |
| `PREREQUISITE_NOT_MET` | có, trùng tên | `QuestAcceptOutcome.cs` | giữ nguyên |
| `INSUFFICIENT_CURRENCY` | có, trùng tên | `InventoryOutcome.cs` | giữ nguyên |
| `INSUFFICIENT_ITEMS` | có, trùng tên | `InventoryOutcome.cs` | giữ nguyên |
| `COOLDOWN_ACTIVE` | có, trùng tên | `CombatOutcome.cs` | giữ nguyên |
| `INVALID_STATE` | không có tên này; server đã nói cùng ý bằng `invalid_transition` | transition từ chối trong quest/combat | chỉ ghi ánh xạ vào tài liệu; **không** thêm mã thứ hai nói cùng một điều |
| `CHARACTER_NOT_FOUND` | không có tên này; server nói `session_not_found` vì danh tính được giải ở biên session | `P1Endpoints.cs` | giữ `session_not_found`; khi có registry nhân vật độc lập (xem dòng dưới) mới cân nhắc `CHARACTER_NOT_FOUND` như mã **mới**, không phải rename |
| `AUTH_EXPIRED` | không có subsystem | Health P1 không có auth edge (quyết định ghi rõ "OAuth/auth edge ngoài Health P1 hiện tại") | chờ packet auth riêng; server không tự phát hành token |
| `CAP_REACHED` | không có enforcement | bảng currency/life-sim chỉ **loaded as data** (task #112, #113) | cần chủ dự án chốt quota tài khoản/đợt reset, sau đó mới có mã |
| `ZONE_UNAVAILABLE` | không có subsystem | chưa có instance/zone registry | packet riêng khi có nội dung instance |
| `MATCH_RULES_MISMATCH` | không có subsystem | PvP queue là service token (`SERVICE_PVP_QUEUE`), chưa có luật ghép trận | packet riêng |
| `RATE_LIMITED` | không có middleware | xem mục 3 | xem mục 3 |
| `INTERNAL_RETRYABLE` | không có phân loại | server hiện trả lỗi có `retryable` cho từng mã đã biết, nhưng không có "lỗi trong nước ngoài dự kiến" | cần quyết định: trả `retryable: true` với mã nào khi chưa có taxonomy; **không** tự chế |

Ranh giới trung thực: 5 mã là **đã khớp tên**, 2 mã là **đã có ngữ nghĩa dưới tên khác**,
6 mã còn lại ứng với subsystem chưa tồn tại. Không mã nào được "bật" bằng cách thêm một
hằng số cho đẹp bảng.

## 2. Dung lượng, retention và audit — số đo, không phải tuyên bố

Chín bounded store trong server, đọc từ hằng số khai báo (không gõ tay):

| Capacity | Store |
| --- | --- |
| 128 | `NarrativeNodes.cs:341` |
| 256 | `DeathReturn.cs:122`, `PlayerLifeLedger.cs:41`, `ConsumableCatalog.cs:210`, `Equipment.cs:87`, `EquipmentV2.cs:72`, `AlphaChapterUnlocks.cs:33` |
| 512 | `CombatDash.cs:44`, `LootGrant.cs:28` |

Tất cả đều **in-memory**, mất khi restart. Doc yêu cầu `idempotencyKey + actorId + operation`
**≥ 30 ngày** và **"không trùng item/currency sau 10.000 lệnh replay"**. Hiện không máy chủ nào
đáp ứng được, và theo quyết định thì **không được** sửa tài liệu thành 256 hay tăng cache để
tuyên bố đạt.

Chính sách tôi đã ship ở gói 30 item 1 và siết lại ở gói 31 Q1 là: **không evict một nghĩa vụ
chưa chứng minh được là hết hạn**. Hệ quả đo được: `PlayerLifeLedger` vượt bound và báo
`CapacityExceededBy` (test: `exceeded=1` ở churn 257 nhân vật, `exceeded=47` ở 303) thay vì
quên một cái chết còn nợ.

Lựa chọn cho chủ dự án và Qoder Remote:

* **A. Durability thực sự** (R-series của Remote): ledger/`outbox`/`receipt` có expiry và
  tombstone. Khi đó `CapacityExceededBy` mới có thể về 0 một cách trung thực.
* **B. Giới hạn công khai cho private alpha**: giữ in-memory, ghi rõ trong handoff rằng replay
  chỉ được bảo đảm trong hàng đợi hiện hành, và client phải fresh-read sau restart (E2E
  `restart-after` 24 checks đã chứng minh "không có gì sống qua restart").

Không có lựa chọn thứ ba: tăng bound chỉ đổi chỗ mà ký tự bị mất.

## 3. Rate limit — biên nằm ở đâu, danh tính lấy từ đâu, và vì sao chưa có số

Quyết định: rate limit economy/chat cần **packet riêng thuộc server API boundary**, auth edge
cung cấp danh tính, "chưa chốt số quota thì chưa bật route economy/chat production, không dùng
con số ngẫu nhiên". Phần tôi giao được ở đây là *biên và đầu vào*, không phải số:

1. **Vị trí**: sau khi phân giải envelope hợp lệ và session, trước khi chạm domain. Đặt ở
   middleware thì không phân biệt được route class; đặt trong từng service thì vi phạm nguyên
   tắc "server-owned decision". Vì vậy: một tầng guard giữa endpoint và service.
2. **Danh tính**: hiện server chỉ có `sessionId → characterId`. `per-account` và `per-IP` cần
   thứ mà Health P1 chưa có: một auth edge. Không có nó, mọi chính sách "theo tài khoản" sẽ
   thực chất là "theo session", đổi lại bằng cách tạo session — tức là không phải rate limit.
3. **Đầu vào chủ dự án phải chốt** (tôi để trống, không tự điền): window, số request/window
   theo actor, theo IP, theo route class (đọc/ghi/economy/chat), và cách tính burst; kèm hành
   vi khi vượt: mã nào (`RATE_LIMITED` canonical chưa có subsystem — xem mục 1) và
   `retryable`/`Retry-After` có được phát không.
4. **Route bị ảnh hưởng hôm nay bằng 0**, vì economy/chat production chưa bật; điều này nên
   được đọc là "chưa có gì để chặn", không phải "đã an toàn".

## 4. Chữ ký DTO tôi gửi cho Qoder Remote (không viết persistence thứ hai)

`Server/Persistence*` thuộc Remote (#79); tôi không tạo DB writer thứ hai. Thứ cần từ họ là một
adapter mà Health gọi, và phía Health đã có đúng các kiểu nguồn cho nó:

```csharp
// Phía Remote cung cấp; phía Health chỉ gọi.
public interface ILifeReceiptStore
{
    // identity đến từ PlayerLifeLedger: (characterId, lifeVersion, PDEATH_<sha64>)
    ValueTask RecordDeathAsync(
        string characterId, int lifeVersion, string deathEventId, long revision,
        DateTimeOffset committedUtc, CancellationToken ct);

    // receipt đến từ DeathReturnService: key + kết quả đã áp, để replay không heal lần hai
    ValueTask RecordReturnAsync(
        string characterId, string idempotencyKey, string requestHash,
        int newLifeVersion, long revision, DateTimeOffset committedUtc, CancellationToken ct);

    ValueTask<bool> TryLookupReturnAsync(
        string characterId, string idempotencyKey, CancellationToken ct);
}
```

Ràng buộc tôi đã chứng minh bằng test ở phía mình, và chữ ký trên tôn trọng nó: một receipt cũ
**không** được biến thành lệnh mới hồi sinh đời sau (`lifecycle.an_alive_returned_character_
keeps_its_death_identity_through_churn`), nên store phải khoá theo `(character, key)` **và**
`lifeVersion`, không chỉ key.

## 5. Việc còn lại thuộc phía chủ dự án, nêu rõ để khỏi đoán

* Chốt mục 3 (các con số) — không có chúng thì chưa bật guard.
* Chốt hướng 2A hay 2B trước khi tôi đụng tới bound nào.
* `docs/production`: `NPC_CLASS_TRIAL` chưa có narrative node nào (xem #134) nên TALK của
  P00-05 chưa có `nodeId` để gọi; 5 target TALK trong quest def thì 2 có node (C1-01, vẫn
  LOCKED theo gate cấp 11). Route vì thế chưa thể có nghiệm thu đúng quyết định.
* Sáu câu hỏi pet/mount (#124) và #132 (đối chiếu JSON alpha với doc nguồn).

## 6. Lệnh tái lập mọi số trong tài liệu này

```bash
python Implementation/Tools/validate_contracts.py            # 33 schema / 33 example, OK
python Implementation/Tools/reconcile_technical_contract.py  # 62 mã, 5/13 khớp tên, capacities
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check   # 568 passed, 0 failed, 568 total
```

Bảng capacities cũng in ra từ `reconcile_technical_contract.py`, đọc từ hằng số khai báo chứ
không gõ tay — cùng bài học khiến công cụ đó trước đây sai ("256 entries").
