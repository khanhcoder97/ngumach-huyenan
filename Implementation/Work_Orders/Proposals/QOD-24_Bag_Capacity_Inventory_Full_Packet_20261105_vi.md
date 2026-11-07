# Packet QOD-24 Q5 — túi 100 slot, `inventory_full`, và hai container DEC-023 §1 nêu — **CHỜ DUYỆT — chưa code, chưa thêm error code**

Gửi owner (#87, #41) + Codex (review) + OpenCode #85 (client sẽ nhận mã lỗi mới).
Lệnh: work order 29 Q5 — *"…Transaction/revision/**capacity**/receipt chống âm và double grant. DEC-023 hoặc công thức thiếu cần packet nguồn rõ, không tự bịa số và không dừng cả gói."*

Tôi viết packet này thay vì code, vì lý do ở §3: thực thi capacity **thêm một error code lên wire**, và error code là thứ đã đóng băng.

## 1. Nguồn đã có, số đã có

`Production_Decision_Register_vi.md:66` (DEC-023, duyệt 2026-10-30) và tài liệu nguồn `docs/production/Runtime_State_and_Catalog_Precision_vi.md` §1 — **lưu ý: file này có trên `origin/main`, branch `qoder/qod-21-…` chưa có** (branch thụt 10 file docs; tôi không tự merge main vì đổi diff PR #106).

§1 nói thẳng, không cần suy:

| cái gì | con số |
|---|---|
| Túi thường | **đúng 100 slot**, 4 trang × 25, layout chuẩn **5 cột × 5 hàng** |
| Kho nhiệm vụ | **30 slot** — "các container khác" |
| Kho cá nhân | **120–200 slot** — dải, chưa chốt một số |
| Page/view index | "không thay **authoritative slotId**" |
| Turn-in khi túi đầy | **giữ `READY_TO_TURN_IN`**, trả **`inventory_full`**, "không tiêu quest item / ghi COMPLETE / cấp **một phần thưởng**" |
| Overflow mailbox | chỉ khi reward policy versioned khai rõ, cùng transaction + dedupe; "hiện **không** suy ra policy đó từ câu mô tả UI" |
| Quest item | chỉ vào kho nhiệm vụ nếu template khai đúng loại **và container còn chỗ** |

## 2. Server hiện tại, đo bằng grep chứ không bằng trí nhớ

| kiểm | kết quả |
|---|---|
| `grep -rn "inventory_full" Server/Health Implementation/Contracts` | **0 kết quả** — mã lỗi này chưa tồn tại ở đâu cả |
| Capacity của túi trong domain | **không có**. `bagSlots: 100` chỉ là **metadata** mà snapshot v2 báo ra (`EquipmentV2.cs:372`, `_rules.BagSlots` từ design); không có chỗ nào chặn grant vượt 100 |
| Hệ quả đo được | nhân vật alpha tích được bao nhiêu item cũng được; turn-in **luôn** cấp thưởng, không có nhánh "túi đầy" |
| Container trên wire | `InventoryLocations` = `BAG`/`EQUIPPED`/`BANK` (`Contracts/InventoryMessages.cs:7-9`). **Không có** location nào cho "kho nhiệm vụ" |
| Stack | `stack_limit` trong hai catalog: **2643** hàng = 1, **96** hàng = 99, **50** hàng = 50, **2** hàng = 3 ⇒ 148 định nghĩa stack được, nên "1 stack chiếm bao nhiêu slot" là câu hỏi thật, không phải câu hỏi lý thuyết |

Nói cách khác: DEC-023 §1 là một luật đã duyệt mà server **chưa cài đặt**. Tôi báo đúng tình trạng đó thay vì im.

## 3. Vì sao phải xin duyệt trước khi code

Capacity không phải luật nội tại: nó biến một request hôm nay thành 201/200 thành một **refusal mới**, và refusal đó phải có tên trên wire.

- Thêm `inventory_full` vào error enum của `TurnInResponse`/grant path = **mở rộng hợp đồng đã đóng băng** ⇒ cần owner/Codex duyệt, không phải việc tôi tự quyết.
- Thêm container "quest stash" = thêm giá trị mới vào enum `InventoryLocations` đã đóng băng ⇒ **lớn hơn** một bậc, và kéo theo `wrong_location` hiện hành đổi nghĩa.
- Nếu làm sai cái này thì sai theo hướng chặn người chơi: turn-in hợp lệ bỗng `inventory_full` là bug phía server, không phía client.

## 4. Đề xuất (phạm vi nhỏ nhất khớp nguồn) — chỉ làm khi được duyệt

**Chỉ túi 100 slot, chỉ error code, không thêm field nào vào snapshot.**

1. `inventory_full` là error code mới, **`retryable: true`** (client giải phóng chỗ rồi retry cùng `idempotencyKey` là hợp lệ), `messageKey` theo mẫu `^P1\.ERROR\.[A-Z_]+$` (`P1.ERROR.INVENTORY_FULL`).
2. **Không** thêm `capacity` object vào snapshot: client đã có `bagSlots: 100` (v2) và `items[]`, nên số chỗ trống tính được phía client mà không đổi schema. Đây là điểm tôi chọn để giảm diện tích hợp đồng.
3. Semantics của một grant nhiều item: **all-or-nothing**, đúng như §1 ("không tiêu quest item / ghi COMPLETE / cấp một phần thưởng"). Nghĩa là không tồn tại trạng thái "cấp 2 trong 3 món rồi fail".
4. Đường nào phải kiểm capacity: grant của turn-in, grant của gather claim, grant loot (kể cả path alpha). Equip/unequip **không** đổi số item trong túi ⇒ không đụng.
5. Refusal phải **không ghi ledger** và **không bump revision** — cùng property tôi đã đo cho các refusal khác (`rejections leaving the snapshot untouched`).
6. Replay cùng key khi đang đầy phải trả **cùng** một refusal, không thành công ở lần replay (đây là chỗ dễ sai nhất: nếu "đầy" được tính lại theo thời gian, replay có thể đổi kết quả ⇒ tôi sẽ ràng buộc refusal vào snapshot tại thời điểm commit, và đó là một quyết định cần owner xác nhận — xem §5 câu 3).
7. Không bật gate mới: `inventory_full` áp dụng cho cả grant hiện hành, nên nó **đổi hành vi production-default**. Đây chính xác là lý do packet này tồn tại.

## 5. Câu hỏi tôi không tự trả lời (mặc định = không code)

1. **"1 stack chiếm mấy slot"** khi `stack_limit = 99`? Sources không nói. Options: (a) một stack = một slot (nghĩa thông thường của "slot"), (b) mỗi item = một slot (khi đó `stack_limit` chỉ là giới hạn số đếm, và túi 100 chỉ chứa ~100 item dù có stack). Chọn sai là đổi số turn-in thành công của người chơi.
2. **Kho nhiệm vụ 30 slot**: có đưa vào phase này không? Nó cần `InventoryLocations` mới (wire enum), nên mặc định tôi **để ngoài**, và ghi vào `unsupported[]` của packet capability.
3. **Refusal có được cache theo idempotency key không**? §1 không nói. Mặc định của tôi: refusal được ghi như một kết quả đã commit (replay trả y nguyên), vì mọi refusal khác trong hệ này đều vậy.
4. **`stack_limit = 3`** trên hai dòng: đó là stack limit hay stack **size** tối đa khi nhận? Hai hàng này cần đọc lại theo ngữ cảnh catalog.
5. **Kho cá nhân 120–200**: dải chưa chốt ⇒ không cài; ai chọn số thì ghi vào packet riêng theo đúng tinh thần Q5.
6. **Reward policy có được dùng overflow mailbox không?** §1 cấm suy ra từ mô tả UI ⇒ mặc định: **không**, và turn-in đầy túi luôn giữ `READY_TO_TURN_IN`.

## 6. Nếu được duyệt, tôi làm gì (và không làm gì)

Làm: error code + enum trong schema `TurnIn*`/grant responses; capacity check **một chỗ** trong transaction grant (không rải khắp nơi); self-check cho 100 ok / 101 refusal / không ledger / không revision / replay; một nhánh e2e qua HTTP thật; README + báo cáo SHA/CI.

Không làm: không thêm snapshot field, không tạo container mới, không đổi `InventoryLocations`, không bật gate, không tự chọn quy tắc stack khi chưa trả lời câu 1.
