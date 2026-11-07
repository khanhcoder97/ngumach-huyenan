# QOD-24 — Đối chiếu mạng dịch vụ NPC / ngoại trang / buff (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Appearance_Buff_NPC_Service_Overlay_Spec_vi.md`
(242 dòng) dưới góc độ server — spec này là nguồn chuẩn định nghĩa 14 service token mà
README:428 ghi "none of them has a route", và là mẫu số chung của các báo cáo forge/economy/
guild trước. Đối chiếu `npc_anchors.json`, `Item_Master_Catalog_vi.csv`, `Server/Health`.
Báo cáo-only: không tool/server nào tham chiếu file này (grep = 0), không sửa nguồn,
không mở route/gate/wire.

## 1. Trạng thái runtime đo được

- `Server/Health/README.md:428`: 19 NPC mang **14 service token** (`SERVICE_TRAVEL` ×4,
  `SERVICE_FORGE` ×2, `SERVICE_SHOP` ×2, `SERVICE_SHOP_POTION`, `SERVICE_MARKET`,
  `SERVICE_BANK`, `SERVICE_GUILD`, `SERVICE_PVP_QUEUE`, `SERVICE_REWARD_CLAIM`,
  `SERVICE_CLASS_SELECTION`, `SERVICE_ACTIVITY_CALENDAR`, `SERVICE_ACTIVITY_QUEUE`,
  `SERVICE_SIEGE_ROSTER`, `SERVICE_PET_MOUNT`) — token có trong data, **không token nào
  có route**. grep `MapGet/MapPost` với service/shop/market/guild/auction/bank/appearance/
  dye trong `Server/` = 0 route.
- Toàn bộ vocabulary routing §6.1 vắng mặt trong `Server/` (grep = 0 file):
  `cosmeticUnlockLedger`, `serviceInventory`, `npcOfferSetId`, `contentVersion`,
  `actorInstanceId`. Nghĩa là request shape
  `{npcId, mapId, serviceId, actorInstanceId, characterId, contentVersion}` chưa tồn tại.
- 18 item mỹ phẩm trong `Item_Master_Catalog_vi.csv` (grep `COS-…` unique = 18) khớp đúng
  §3.1 dòng 38 "Catalog hiện có 18 item mỹ phẩm". Data cosmetic có; ledger unlock/equip
  và service nhuộm/salon thì không.

## 2. Cặp đối chiếu KHỚP (đo bằng script, không ước lượng)

**Tọa độ NPC dịch vụ:** bảng §6 (dòng 159–176) cho 23 cặp (npcId, mapId, x). Đối chiếu
`npc_anchors.json` (104 anchor): **23/23 khớp chính xác** cả x lẫn y=0, 0 mismatch,
0 missing. Các NPC nhiều điểm cùng canonical ID đều đúng cả hai anchor:
- `NPC_VAN_NHU` Thăng Long (455,0) + Thanh Lạc (124,0)
- `NPC_BLACKSMITH` (409,0) + (102,0); `NPC_TRADER` (237,0) + (72,0)
- `NPC_GUILD_CLERK` (636,0) + (309,0) — khớp báo cáo guild
- `NPC_RELIC_MERCHANT` (366,0) + Bạch Uyên (42,0)
- `NPC_HA_MAC` (723,0) + (155,0); `NPC_RAID_KEEPER` Thăng Long (566,0) + Vực Nghịch Mạch (329,0)
- `NPC_TL_AUCTION_CLERK` (316,0), `NPC_TL_BANKER` (322,0), `NPC_ARENA_STEWARD` (587,0),
  `NPC_ARENA_REWARD_CLERK` (599,0), `NPC_ACTIVITY_STEWARD` (548,0), `NPC_TL_APOTHECARY` (181,0),
  `NPC_MEDIC_BEN` Bến Mưa (30,0), `NPC_MEDIC_SA_HOA` (82,0), `NPC_WATER_SELLER` (110,0).

Kết luận: spec overlay ↔ manifest ↔ anchor catalogue nhất quán về placement dịch vụ;
không có mâu thuẫn tọa độ để pin. Khoảng trống là **service routing**, không phải placement.

## 3. Contract dịch vụ chưa có runtime

### 3.1 Routing §6.1 (dòng 182)

Server phải xác thực: actor đúng map, khoảng cách tương tác **≤2,5m**, NPC active/time
window, quest/level/class/guild permission, offer revision; `serviceInventory` merge từ
base catalog + `npcOfferSetId` + region + rotation time + eligibility. Không gì trong số
này có service/route. Gửi tọa độ không đủ để gọi cửa hàng ngoài vùng — nhưng vì chưa có
route nên chưa có gì để enforce.

### 3.2 Error code §7 (dòng 190) — 5/7 vắng mặt

| Error code | Trong `Server/`? | Ngữ cảnh hiện có |
| --- | --- | --- |
| `QuoteExpired` | 0 | chưa có |
| `AlreadyOwned` | 0 | chưa có (cosmetic ledger chưa tồn tại) |
| `ServiceClosed` | 0 | chưa có |
| `TicketLimit` | 0 | chưa có (vé có data, service không) |
| `BuffConflict` | 0 | chưa có (buff stacking §4.1 chưa runtime) |
| `InsufficientCurrency` | có | `InMemoryInventoryService.cs`/`InventoryOutcome.cs` — ngữ cảnh inventory/equip, KHÔNG phải service routing |
| `WrongClass` | có | `ServiceSelfCheck.cs` — restrict equipment class, KHÔNG phải service routing |

Hai code tồn tại nhưng ở lane khác; năm code còn lại của service contract chưa có. Thêm
chúng là đổi wire cần duyệt, không tự thêm.

### 3.3 Subsystem có data/anchor nhưng không service

- **Cosmetic ledger** (§7): `cosmeticUnlockLedger` account-bound, equip state theo
  character/slot, preview unowned không ghi ledger. 18 item có data; ledger/service không.
- **Buff stacking** (§4.1): cùng `buffGroupId` thay thế/giữ, `refreshPolicy`, khác group
  song song theo `stackPolicy`, PvE buff suspend khi PvP, `expiresAt` server giữ. Potion
  `POTION_RECOVERY` cooldown chung 8s (PvE) — phân biệt với 12s PvP của Activities §6,
  không mâu thuẫn. Consumable lane (task 118) đã load rule; buff state machine thì chưa.
- **Vé boss** (§5): `TICKET-BOSS-01` cap 3/account/tuần, one/participant,
  consume-at-boss-spawn / refund-before-spawn. Khớp phụ lục economy §7.3 (45201d1): item
  data + `NPC_RAID_KEEPER` anchor có, Server runtime = 0.
- **Salon/nhuộm** (§3.2–3.3): `NPC_VAN_NHU` lưu diện mạo gốc từ lần 2 giá 2.000 Đồng/lần,
  nhuộm 500 Đồng/cosmetic slot, quote từ server; `DyePalette` version, ≤3 kênh, chỉ item
  có `dyeableChannels[]`. Không service/quote route.
- **Auction/bank/forge routing** (§6): `NPC_TL_AUCTION_CLERK` (sàn người chơi),
  `NPC_TL_BANKER` (kho account + mailbox), `NPC_BLACKSMITH` (forge sâu) — đều token
  routeless; forge/economy đã pin ở báo cáo riêng.

## 4. Câu hỏi owner

1. Có duyệt packet service-routing chung (request shape §6.1, distance ≤2,5m, permission/
   offer-revision, `serviceInventory` merge) làm nền cho shop/forge/guild/arena không?
   Wire/schema mới qua cổng duyệt riêng; 14 token đang routeless.
2. Năm error code service (`QuoteExpired`/`AlreadyOwned`/`ServiceClosed`/`TicketLimit`/
   `BuffConflict`) thêm vào wire envelope nào, và ai duyệt? Hai code có sẵn
   (`InsufficientCurrency`/`WrongClass`) có tái dùng được cho service không hay cần bản riêng?
3. Cosmetic ledger + buff stacking + salon/dye quote + ticket consume-at-spawn: packet
   riêng từng hệ hay gộp vào service-routing? Tất cả đều server-authoritative, chưa runtime.
4. Interaction range dịch vụ ≤2,5m (§6.1) có phải chuẩn chung với interact/portal hiện tại
   không, hay mỗi service một range? (không tự đổi range đang chạy)

## 5. Kiểm chứng lượt này

```bash
# 23/23 cặp tọa độ §6 khớp npc_anchors.json (script đối chiếu, 0 mismatch/0 missing)
# 18 COS- unique trong Item_Master_Catalog_vi.csv == §3.1
grep -rl 'cosmeticUnlockLedger\|serviceInventory\|npcOfferSetId\|contentVersion\|actorInstanceId' Server  # 0
grep -rl 'QuoteExpired\|AlreadyOwned\|ServiceClosed\|TicketLimit\|BuffConflict' Server                   # 0
```

Báo cáo-only, không đổi code/runtime/bundle; kết quả công bố trên #87/#41/PR106. Không
mở route/gate/wire, không sửa `docs/production/**`, không merge.