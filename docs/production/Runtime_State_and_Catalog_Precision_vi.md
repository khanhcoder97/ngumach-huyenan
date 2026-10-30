# Precision trạng thái nhân vật và catalog — 2026-10-30

Owner thiết kế: Codex; DEC-023. Bổ sung `Production_Rules_Complete_v1_vi.md` và `Content_Export_and_Asset_Completion_vi.md`. Đây là luật thiết kế để xuất dữ liệu/viết code, chưa là migration đã chạy. Không thay hệ số cân bằng, API đóng v1, tọa độ hoặc schema do agent khác phụ trách.

## 1. Túi đồ và reward khi túi đầy

Túi thường có đúng 100 slot, bốn trang × 25 slot; layout chuẩn **5 cột × 5 hàng** theo UI_UX §6. Kho nhiệm vụ 30 slot và kho cá nhân 120–200 slot là các container khác. Responsive có thể đổi số cột hiển thị nhưng không sinh thêm slot hoặc đổi item instance. Page/view index không thay authoritative slotId.

Quest turn-in mặc định giữ READY_TO_TURN_IN khi không đủ chỗ, trả inventory_full, không tiêu quest item/ghi COMPLETE/cấp một phần thưởng. Đây là luật đã chốt trong Completion Addendum §2, thắng câu mailbox mặc định trong đặc tả túi cũ. Chỉ được dùng overflow mailbox nếu reward policy versioned của hoạt động khai rõ, cùng transaction và dedupe; hiện không suy ra policy đó từ câu mô tả UI. Quest item chỉ vào kho nhiệm vụ nếu template khai đúng loại và container còn chỗ.

## 2. Giải nghĩa các cột stat item, tránh nhân đôi

Nguồn số là hai CSV item; tên hiển thị tiếng Việt không phải runtime enum. Exporter cần bảng ánh xạ versioned tới stat keys, báo lỗi khi gặp tên chưa biết.

- `weapon_power` và `primary_stat=Công vật lý/Công phép` trên vũ khí đang mô tả **cùng** power nền. Không cộng hai lần vào weapon attack và flatGearAttack. Damage type lấy từ class/template được resolve; không đoán từ icon.
- `armor` và `primary_stat=Giáp` nếu cùng tồn tại mô tả **cùng** armor nền. Nếu một cột trống, dùng giá trị ở cột có nguồn. Nếu hai giá trị khác nhau, fail export với itemId/field/source; không tự cộng, lấy max hoặc bỏ cột tùy tiện. Phi phong có primary Giáp nhưng cột armor trống vẫn phải có armor.
- `secondary_stat/value` là đóng góp khác, cộng đúng một lần trước công thức derived stats; affix/socket/upgrade/hidden/set tách buckets theo Item Bible. Không áp rarity thêm lần nữa lên số đã scale trong rarity-variant CSV.
- `Fixed` không phải phẩm chất gear thứ sáu: fixed item giữ nguyên ID và toàn bộ trường từ master. Mỗi fixed item phải có đúng một dòng tương ứng trong rarity catalog; gear template không tự thành instance chỉ vì có ID trong master.

Oracle cấp1 không gear: STR/INT/AGI/VIT/LUK=5 → HP198, MP102, PhysicalAttack20, Armor10. Chỉ mặc `EQ-MK-WEAPON-T1-R-COMMON` (power12, STR+2) → PhysicalAttack=12+3×7+5=**38**, không phải50. Chỉ mặc `EQ-MK-HAT-T1-R-COMMON` (armor2, VIT+1) → HP212, Armor14, không phải16. Đây là oracle exporter/stat aggregation; không chứng minh starter loadout đã được server trang bị.

## 3. HP/MP khi maximum thay đổi

Chốt baseline mới: thay level, phân điểm/reset điểm, equip/unequip, buff hết hạn hoặc đổi loadout **không tự hồi** HP/MP. Sau khi tính lại maximum, giữ giá trị tuyệt đối hiện tại và clamp vào [0,newMaximum]. Actor chết vẫn HP0, không tự sống vì tăng cấp hoặc mặc đồ.

Việc cấp EXP/điểm, recalculation và cập nhật revision nằm trong cùng transaction reward/stat. EXP vượt ngưỡng xử lý lần lượt theo Rules §1; điểm mới ở trạng thái chưa phân phối trừ thao tác auto-build đã được người chơi chọn. Không tự áp default build khi reward lên cấp. EXP dư ở cấp100 không biến thành tiền; không làm mất tổng EXP lịch sử trong ledger.

| Ca | Trước | Sau bắt buộc |
|---|---|---|
| L1→L2, không phân điểm | HP100/198, MP80/102 | HP100/226, MP80/114; +5 điểm chưa phân |
| Mặc món +18 maxHP | HP100/198 | HP100/216 |
| Tháo món +18 maxHP | HP210/216 | HP198/198; mặc lại không lấy lại12HP |
| Buff maxHP hết khi chết | HP0 | HP0, không phát revive/heal event |
| Migration fixture demo | HP100/MP50 profile cũ | Refill một lần theo Rules §1, có migrationId; retry migration không refill tiếp |

Heal/potion/respawn có luật riêng; chỉ các operation đó được tạo healing phù hợp. Thay derived stat không xóa cooldown/ICD, không refund cast, không reroll item. Cast đã accepted giữ snapshot của cast theo Rules; hit kiểm lại các guard sống/tầng/LOS/invulnerability. Chưa có dữ liệu đầy đủ cho một modifier thì export báo unsupported, không bịa effect.

## 4. Auto-potion và hai loại đồng hồ

Potion hồi phục được dùng ngay khi command server accepted; không trì hoãn hai giây để chờ Undo và không hoàn item/HP sau commit. Toast có `Tắt tự dùng` áp dụng lần kế tiếp. Nếu muốn hủy request chưa gửi, client chỉ hủy local intent; request đã gửi mà kết quả chưa rõ phải query receipt theo requestId, không coi nút hủy là đã rollback server.

Food/consumable buff dùng expiresAt UTC, hết hạn cả khi offline theo Rules §3. Skill/status dùng tick simulation; serialization/reconnect cần lưu remaining duration/epoch theo policy của status, không chép tick của process trước thành tick của process mới. Export mỗi buff phải khai duration, clock, persistOnDeath, reconnect policy, group/refresh/suspend; thiếu trường làm export fail. UI countdown không phải nguồn quyết định effect còn tác dụng.

## 5. Vé boss và thời điểm ACTIVE

Thống nhất câu “boss đã spawn” của Activities với “tiêu tại ACTIVE” của Rules §6: ready-check chỉ reserve vé; arena/boss được chuẩn bị thành công trước activation nhưng chưa cho đánh/nhận reward. Khi toàn roster đã hợp lệ, commit tiêu vé của từng người và activation record duy nhất, rồi kích hoạt encounter bằng outbox có thể replay. Nếu commit không thành công, không người nào bị tiêu vé và không bắt đầu encounter. Không debit theo từng người trong vòng lặp không transaction.

Crash sau debit nhưng trước materialize ACTIVE phải phục hồi cùng instance/session bằng activationId; không tạo vé/instance thứ hai khi retry. Nếu không thể phục hồi, compensation dùng unique ID và ledger, không hoàn bằng thao tác client. Từ ACTIVE trở đi áp dụng luật session20phút/wipe/disconnect đã có, không auto-refund do người chơi rời trận. Đây là yêu cầu tính nguyên tử; implementation cross-worker cần proposal transaction/outbox cụ thể và failure tests.

## 6. Bổ sung vẫn bắt buộc trước content lock

Các mục dưới **chưa được chốt bởi tài liệu này**. Chúng là hạng mục precision có đầu ra rõ, không dùng số placeholder để đóng:

| Gap | Cần giao | Điều kiện kiểm |
|---|---|---|
| Đồng từ quái theo band | bảng band/min/max/eligibility/cap/source, loot group precedence | grant đúng band, RNG/retry/ledger, faucet-sink simulation |
| Giám định dòng ẩn | bảng phí T1–T7, scope miễn lần đầu/ngày, binding/stock/service guard | không tính phí lại do retry/đổi NPC/nhân vật trái scope |
| Tăng tài nguyên lớp theo % trên gear | rule làm tròn hoặc tích lẻ, thứ tự/cap5, PvP, event proc | +1% vào resource nguyên không tự thành +1 mỗi hit hoặc luôn0 |
| Roll socket/hidden | phân phối số socket theo rarity và lựa chọn hidden nếu pool nhiều entry | xác suất công khai, server RNG version, không reroll khi login |
| Boss ngoài subset | phaseGuard/interruptible/target-lock, geometry, resolved stats và rewards mỗi encounter | graph đi được; telegraph/hit khớp, wipe/phase edge tests |
| Map top-down | nav/collision/floor/portal, review349placements, migration nếu dời anchor | chứng minh route và safe distance; không copy synthetic rectangle |

Qoder thực hiện schema/export/server; OpenCode kiểm candidate/tooling; Muse cung cấp art/layout candidate; Codex review nguồn, UI và bằng chứng tích hợp. Không đánh dấu các hàng trên DONE chỉ vì tài liệu đã liệt kê tên.
