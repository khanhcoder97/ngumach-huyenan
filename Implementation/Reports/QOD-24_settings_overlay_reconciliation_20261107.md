# QOD-24 — Đối chiếu Modal Cài đặt / Settings overlay (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Settings_Overlay_Spec_vi.md` (195 dòng) dưới
góc độ server. Phần lớn spec là client UI (pixel art, responsive, focus trap, slider,
preview); báo cáo chỉ pin những điểm chạm server. Báo cáo-only: không mở route/gate/wire,
không sửa nguồn.

## 1. Trạng thái runtime đo được

- Không có preferences/settings store nào. Vocabulary §7/§10 (`preferences`/`deviceScope`/
  `playerVisibility`/`fpsCap`/`colorMode`/`textScale`/`input.mode`/`graphics.quality`) grep =
  **0 file** trong Server/Health. (`schemaVersion` có 17 file nhưng là schema content khác,
  không phải preference schema.) Không route lưu/đọc cài đặt, không migration preference.
- Không có account service (liên kết email/đăng xuất/xóa tài khoản §4.2) — `account` grep
  trong ngữ cảnh service = 0; đây là lane account/session riêng, chưa wire.
- Teleport service hiện có (`ITeleportService.Teleport`) chỉ nhận 4 reason: `QUEST`,
  `DEATH_RETURN`, `CITY_RETURN`, `ADMIN` (`TeleportCommand.cs:5-8`). **Không có reason
  `UNSTUCK`/`SAFE_POINT`** cho "Thoát kẹt" §6.

## 2. Điểm chạm server — đối chiếu

### 2.1 Preferences persistence (§7, §10 dòng 179)

Spec: cài đặt cá nhân lưu theo **account + thiết bị**; keybind/d-pad/FPS cap ưu tiên
per-device; schema lưu có `value`, `deviceScope`, `updatedAt`, `schemaVersion`; migration
**không được reset keybind/layout** khi thêm setting mới; save lỗi giữ local pending + retry,
không báo thành công giả. Server-authoritative gameplay state không bị UI settings ghi.
Đo: không field/route/store nào chở các key này. Đây là persistence lane (Remote #79) +
preference service chưa duyệt; preference keys machine-safe (`input.mode`, `visual.theme`,
`camera.viewScale`, `graphics.*`, `audio.master`, `accessibility.*`) chưa có schema.

### 2.2 Thoát kẹt / unstuck (§6 dòng 119, 122)

Spec: gửi request server kiểm tra vị trí + trạng thái; **chỉ teleport tới safe point gần
nhất nếu** ngoài combat/boss/raid/siege, không giao dịch/quest escort khóa vị trí, và server
chấp thuận; có confirm, **cooldown**, thông báo đích, không mất item/quest. Nếu không hợp lệ
trả lý do cụ thể (ví dụ "Không dùng được trong raid đang diễn ra"). Client không tự dịch
chuyển khi mất kết nối/chưa nhận xác nhận.

Đo: `TeleportReasons` không có UNSTUCK; `TeleportErrorCodes` chỉ `invalid_map/out_of_bounds/
invalid_reason/invalid_condition` — không có cooldown/combat-lock/raid-lock error riêng cho
unstuck. Safe-point gần nhất + cooldown + tập điều kiện loại trừ (combat/boss/raid/siege/
escort-lock) chưa có service nào. Cần reason mới + guard + cooldown ledger; **không tự thêm
vào frozen wire** khi chưa duyệt.

### 2.3 Player visibility giao AOI audience (§5.3 dòng 84)

Spec "Hiển thị người chơi: Tất cả / Bang hội + party / Ẩn người chơi khác" — chỉ giảm actor
không thuộc party; **đồng đội, NPC quest, boss, telegraph, vùng tương tác luôn hiện**; tắt
người chơi khác không ẩn chat lời mời/raid member. Đây là client render filter, nhưng nếu
server áp dụng phải khớp AOI audience projection (40/48 hysteresis) đã ship — không được ẩn
boss/telegraph/NPC quest. Đo: không có preference `playerVisibility` nên hiện chỉ là ý định
client; pin ràng buộc "không ẩn actor gameplay quan trọng" để packet sau không phá audience.

### 2.4 Camera view scale (§5.2 dòng 75)

Spec "Khung nhìn Chuẩn/Rộng/Siêu rộng: 32 WU ở 16:9, tối đa ~40 WU ở 20:9; phần dư trên 20:9
dùng parallax/biên UI, không mở thêm tầm nhìn gameplay; PvP/raid chuẩn hóa camera". Khớp
quyết định wide-camera đã reconcile (task #116) — camera là client, không tạo lợi thế PvP;
server không cần field mới, chỉ pin lại giới hạn tầm nhìn gameplay không đổi theo setting.

## 3. Phần thuần client (không chạm server, ghi nhận phạm vi)

§2–§5/§8–§9: khung modal responsive, header/CTA, thẻ hồ sơ (che email/ID), lưới tile cài
đặt, slider/segmented control, preview đồ họa 15s, component states, visual tokens, HTML/CSS
tham chiếu — là client UI. §1 "mở modal không dừng mô phỏng thế giới; nhân vật dừng nhận
lệnh nhưng server vẫn chạy combat" là ràng buộc thiết kế: server **không** pause simulation
khi settings mở (khớp server authoritative hiện tại). Không có gì để enforce phía server
ngoài §2.1–§2.4 đã pin.

## 4. Câu hỏi owner

1. Preferences store (account+device, `deviceScope/schemaVersion/updatedAt`, migration không
   reset keybind) thuộc lane persistence Remote #79 hay preference service riêng? Ai duyệt
   schema preference keys §10?
2. "Thoát kẹt" có được thêm reason `UNSTUCK` vào teleport wire (hiện frozen 4 reason) +
   cooldown ledger + guard combat/boss/raid/siege/escort-lock không? Safe point gần nhất lấy
   nguồn nào (manifest anchor hay registry)?
3. Account service (link email/logout/delete) có packet riêng không? Hiện chưa wire.
4. `playerVisibility` nếu áp server-side có phải đi qua AOI audience (không ẩn boss/telegraph/
   NPC quest) hay thuần client render filter?

## 5. Kiểm chứng lượt này

```bash
# Server preferences/deviceScope/playerVisibility/fpsCap/colorMode/textScale grep = 0
# TeleportReasons = QUEST/DEATH_RETURN/CITY_RETURN/ADMIN (TeleportCommand.cs:5-8); no UNSTUCK
# TeleportErrorCodes = invalid_map/out_of_bounds/invalid_reason/invalid_condition; no cooldown/raid-lock
# schemaVersion 17 file = content schemas, not preference store
```

Báo cáo-only, không đổi code/runtime/bundle; kết quả công bố trên #87/#41/PR106. Không mở
route/gate/wire, không sửa `docs/production/**`, không merge.