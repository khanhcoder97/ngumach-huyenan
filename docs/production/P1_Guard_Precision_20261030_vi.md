# Phản Quang — quyết định triển khai và nghiệm thu P1

Ngày 2026-10-30, Asia/Tokyo. Owner thiết kế: Codex. **DEC-022** bổ sung precision còn thiếu của SK-MK-01; đây là tuning baseline để Qoder triển khai có version, chưa là cân bằng qua playtest hoặc bằng chứng runtime đã chạy. Bundle máy đọc: `Implementation/Content/DesignBaselines/p1_guard_precision_v1.json`. Không bật gate, không thay wire/SkillDefinition hiện hành bằng tài liệu này.

## 1. Nguồn và phạm vi quyết định

Giữ Combat Spec/SkillDefinition: CD 10 giây, 12 MP, cửa đỡ 0,4 giây, giảm 70%, vùng trước 120°/4,4 WU, phản công hệ số PvE/boss 1,8 và PvP 0,65, +2 Kiếm Ý, tối đa một lần/cửa. Resource cap 5, DR bucket cap 80% và thứ tự shield→HP theo Production_Rules §2–3. Không nhân thêm hệ số 1,8 vào coefficient đã resolved.

Các mục **mới được chốt**: 70% áp cho direct damage từ vùng trước; 20% hụt là buff phòng thủ 1 giây sau cửa đỡ hết tự nhiên; phản công ở tick kế tiếp; thứ tự sống/chết và quyền nhận resource dưới đây. Các giá trị này trước đây chưa đủ precision, không mô tả như luật runtime đã có. Phạm vi rollout đầu tiên là Minh Kiếm/P1 PvE. PvP/gear proc/party/threat tương tác cần kiểm riêng; không báo đã hỗ trợ chúng từ một coefficient PvP có sẵn.

## 2. Cửa đỡ và hướng

Với cast accepted tại tick T, guard active trong **[T,T+8)** ở 20 Hz. Một hit tại T+7 có thể đỡ; hit tại T+8 không thuộc guard. MP và cooldown commit một lần khi accepted, không hoàn khi hụt/cancel. TelegraphSeconds=0,4 trong example cũ là thời lượng thế thủ của skill này, không được thêm một windup 0,4 giây trước khi bật guard.

Facing normalize từ aim snapshot khi accepted. Vùng guard gắn với **chân người phòng thủ hiện tại**, dùng facing đã khóa: đây là self-attached status, không phải cone tấn công để lại trên đất tại vị trí cũ. Đi bộ không tự reset/refresh cửa và không xoay cone theo aim mới. Khoảng cách đo từ chân defender tới chân nguồn hit, r≤4,4 và dot≥cos60°; mép range/góc tính trong vùng. Hai chân trùng tọa độ tính trong vùng, tránh normalize vector0. Không suy từ hướng vung kiếm trong sprite.

Direct damage có nguồn trong cone hưởng DR 0,70 khi guard active. Damage ngoài cone, DoT, reflected damage và environmental damage không hưởng 70%. Ranged direct từ trong cone có thể được giảm damage nhưng **không** kích phản công. Invulnerability xử lý riêng; miss/immune không trở thành đỡ chuẩn. Không xóa/bẻ hướng đòn UNDODGEABLE: đây không phải dodge immunity; nếu đòn cho phép DR thì DR vẫn tính theo bucket bình thường.

Đòn kích phản công phải là direct melee của nguồn hostile còn sống, cùng instance/floor, đã qua hit roll và LOS tại impact, trong cone. `NO_COUNTER_TRIGGER`, DoT, phản công, đồng minh và tự damage bị loại. Khiên hấp thụ hết vẫn là một đòn được đỡ hợp lệ nếu defender còn sống. Không phát counter chỉ vì cast accepted hoặc HP trong snapshot giảm.

## 3. Xử lý một lần, resource và phản công

Damage gốc resolve trước: DR→floor cuối→shield→HP. Nếu defender chết từ hit đó: death cleanup, resource về0; không counter confirmation, không +2 Kiếm Ý, không phản công từ người chết. Nếu còn sống và đây là hit đầu hợp lệ: commit một confirmation theo guardCastId, cộng min(5,current+2), reserve đúng một counter với hit source; các hit sau vẫn có DR70% tới hết cửa nhưng không nhận resource/counter thêm. Resource không chờ counter gây damage và không cộng lần hai khi counter trúng.

Counter impact tại tick kế tiếp, không recurse ngay trong stack xử lý hit. Mục tiêu duy nhất là nguồn của hit đã confirmation, không chọn người khác khi nguồn chết. Dùng PhysicalAttack resolved của defender **snapshot khi guard accepted**, rank/mode từ cast; hệ số lấy đúng SkillDefinition, không lấy damage vừa nhận làm attack. Roll accuracy/crit server theo counter correlation riêng; shield/mitigation/DR của target áp bình thường. Recheck hai bên sống, instance/floor/hostility, range4,4/cone120°, LOS và invulnerability ở tick counter; mất điều kiện thì MISS/CANCEL có lý do, không retarget và không refund.

Counter mang NO_COUNTER_TRIGGER để hai guard không phản vô hạn, không tốn thêm MP/CD và không thêm resource từ damage. Không hard-control boss. Skill này không tự tạo stun/stagger mới ngoài rule được duyệt; không lấy hiệu ứng art làm quyền CC. Confirmation là sự kiện đỡ thành công và reserve phản công; **không khẳng định counter đã trúng hoặc gây HP damage**.

Các impact cùng tick sắp theo (scheduledTick, castStartTick, castId ordinal, hitIndex, targetId ordinal); server tạo castId, không dùng client-selected key làm ưu tiên. Với subset direct melee P1, source phải còn sống khi impact được xử lý; chết trước lượt thì cancel impact còn lại. Không áp luật đó cho projectile/DoT toàn game chưa được thiết kế. Counter của tick sau thấy source đã chết thì cancel; confirmation/resource đã commit trước đó vẫn giữ nếu defender còn sống. Reconnect/replay không sắp lại lịch hoặc phát confirmation lần hai.

## 4. Đỡ hụt, kết thúc và hủy

Hết tự nhiên tại T+8, nếu chưa confirmation và defender còn sống: tạo status WHIFF_GUARD DR0,20 trong **[T+8,T+28)**, tức1 giây. Buff hụt giảm mọi incoming damage thuộc DR bucket bình thường; không thành immunity, không thêm shield, không tạo counter/resource. Không stack 20% với chính nó; application cùng skill refresh theo status rule, không kéo dài qua reconnect. Đây là lựa chọn tuning mới để câu “hụt chỉ giảm20%” có nghĩa executable.

Guard đã thành công không có buff hụt. Death/map change/session end/hard-control hoặc cancel sang dodge kết thúc guard và fallback ngay, không cấp whiff như thưởng khi hủy. Di chuyển thường không phải cancel. Cooldown vẫn giữ; CAST_END không xóa nhầm status whiff còn thời hạn. Không lưu simulation status thành buff UTC để offline rồi bật lại. Giữ cleanup cùng life/scope để callback cũ không gắn status lên đời mới.

DR cộng cùng bucket rồi cap0,80. Guard70% + nguồn DR20% = cap80%, không phải90% hoặc nhân thành76%. WHIFF20% + DR20% khác =40%. Set/hidden/passive chưa được hỗ trợ phải có fixture/proc registry riêng; không cộng set bonus từ tên món đồ.

## 5. Hình ảnh, âm thanh và UI

| Pha | Muse thể hiện | Codex client/audio |
|---|---|---|
| Accepted/start | Viền bạc mảnh, thế kiếm, cone debug riêng khi cần | Prep; không phát parry hoặc số damage |
| Confirmation | Cung lục giác vàng nhạt, chữ “Đỡ chuẩn” nhỏ | `COUNTER_CONFIRMED` semantic→`SFX/SKILL/metal_parry` một lần; ánh sáng không che boss warning |
| Counter hit/miss/cancel | Nhát trả ngắn; impact chỉ theo kết quả riêng | Không dùng tiếng đỡ làm bằng chứng counter gây damage; không flash hit cho MISS |
| Hụt | Viền thủ mờ20% trong1 giây, icon thời hạn | Không phát metal_parry, không +2 resource giả |
| Snapshot/reconnect | Dựng trạng thái còn hiệu lực | Silent reconcile, không replay âm/VFX confirmation |

Tên event wire/correlation thuộc proposal v2 của Qoder; semantic trong bảng không cho phép thêm field vào v1. Cue audio đã có nhưng event adapter chưa nối; tài liệu này không chứng minh Unity playback.

## 6. Ma trận nghiệm thu giao Qoder

| Case | Kết quả bắt buộc |
|---|---|
| Hit front ởT+7 / T+8 | Lần đầu guard70%; lần sau chỉ whiff20% nếu đã hết tự nhiên mà chưa thành công |
| Mép60°/4,4WU, vừa ngoài mép | Mép hợp lệ; ngoài không guard/counter |
| Hai hit melee hợp lệ cùng tick | Thứ tự deterministic; một confirmation, một+2, một counter; cả hai có DR nếu defender sống |
| Ranged trong cone / DoT / sau lưng | Ranged có DR70% không counter; DoT/sau lưng không DR70% |
| Shield hấp thụ hết / miễn nhiễm / miss | Shield vẫn có thể confirmation; immune/miss không confirmation |
| Hit gốc giết defender | Một death, không counter/resource; resource death reset0 |
| Nguồn chết trước/sau confirmation | Chết trước lượt impact direct melee: cancel; chết sau confirmation: counter tick sau cancel, không roll lại credit |
| Counter gặp guard khác | Không kích vòng counter; damage được DR hợp lệ của đối thủ giảm bình thường |
| Counter target rời range/floor/instance hoặc LOS bị chặn | Không gây damage/retarget, không refund hay confirmation mới |
| Hụt tự nhiên / cancel dodge / chết / đổi map | Chỉ hết tự nhiên còn sống mới có whiff20%×20tick; cancel không có |
| Retry idempotency, reconnect, event replay | Cost/CD/resource/confirmation/death một lần, silent history |
| Action end trước whiff expiry | Whiff sống đủ thời hạn riêng, không bị CAST_END xóa |

Oracle hit đã xác nhận, raw30/armor10/không crit: thường27, guard70%→8, hụt20%→21, DRcap80%→5 (floor một lần). Counter attack20×1,8/armor10:32, crit49. Đây chỉ là oracle công thức/timeline, không là simulation hoặc nghiệm thu damage server. Qoder phải chạy thật state machine/concurrency/HTTP tests và dẫn exact SHA trước bật gate.

## 7. Bước triển khai và migration

Qoder cập nhật proposal QOD-16/QOD-17 bằng DEC-022, build resolved status/counter records có version và tests; giữ v1 nguyên, gate mặc địnhOFF, DEV profile rõ nhãn. Không cần hỏi lại hướng/thời lượng DR đã chốt ở đây. Những blocker khác như boss geometry/topology, coin band và gear stats vẫn theo work order08, không tự được phê duyệt từ DEC-022. Codex review code/wire, Muse dựng cue theo bảng; rollout sau bằng chứng, không tự sửa snapshot hoặc save cũ.
