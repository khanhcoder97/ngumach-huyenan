# Phân xử thiết kế P1 để tích hợp — 2026-10-29

Owner thiết kế: Codex. Đọc cùng DEC-016/017 và work order QOD-11→15. Văn bản này chốt cách dùng nguồn đã có và semantic presentation, không sửa server/contract/data examples thay Qoder. Không tuyên bố đã content-lock/cân bằng toàn game.

## 1. Có nguồn số liệu, còn thiếu bản export

| Miền | Nguồn chuẩn cần dùng | Ý nghĩa triển khai |
|---|---|---|
| Actor HP/MP/stat/damage | `Production_Rules_Complete_v1_vi.md` §1–3; `Implementation/Content/DesignBaselines/completion_v1.json` | Baseline tuning v1 có version, design-only. Qoder được chuẩn bị proposal/export/implementation có gate, không phải tiếp tục ghi “không có công thức” |
| Mob HP/ATK/DEF/archetype | `Art_Entity_Weather_UI_Visual_Bible_vi.md` §12 | Đã có base và multipliers; thiếu executable record được review không đồng nghĩa chưa ai thiết kế số |
| Level/spawn/respawn | `World_Spawn_Gathering_Manifest_vi.csv`, atlas và spawn definition cụ thể | Dùng level của spawn, không lấy level nhân vật thay thế hoặc đoán level từ sprite; interval chưa xác định vẫn blocked |
| Skill coefficient/cost/CD | 3 `SkillDefinition` examples hiện tại + Combat Spec | Hệ số mode thay thế nhau; PvP0,65 là coefficient trực tiếp của subset, không nhân thêm1,8/1,5/1,9 |
| MK03 range | completion_v1 `combat.skillRangeMigrationWu.SK-MK-03=4.4` và Rules §2 | Được làm migration example/schema/loader riêng: CONE range4,4WU, angle100°, cap5. Không sửa client để bù một `rangeWu` đang thiếu |
| Mãng Cốt ba đòn | Rules §4 | A cone120°/8WU/0,9s; B radius4WU/1,2s; C annulus3..7WU/1s. Thắng hai đòn/báo0,8s trong hồ sơ art cũ |

Khóa policy: baseline này được dùng làm **đầu vào thiết kế versioned để xây dựng prototype**. Muốn chạy runtime phải có PR export/schema/loader/tests và flags thích hợp; không copy thẳng vào production config. Những trường chưa được định nghĩa vẫn cần proposal, không lấp bằng số tùy ý. Không đưa fixture HP100/MP50 vào bảng cân bằng mới.

## 2. Phép tính tham chiếu, không phải runtime config

Actor cấp1 không gear, STR/INT/AGI/VIT/LUK=5: maxHP198, maxMP102, PhysicalAttack20, MagicAttack20, Armor10. Đây là profile không gear; starter gear chưa có stat trong ItemDefinition example nên không thể gọi đây là profile đã trang bị.

Mob base ở cấp5: HP240, Attack20, Defense6. Áp multiplier archetype đúng **một lần**:

| Archetype cấp5 | HP trước quyết định làm tròn/export | Attack | Defense |
|---|---:|---:|---:|
| MOB_CARPLING |192|15|4,2|
| MOB_WATERROOT |264|20|6,6|
| MOB_SHORE_STALKER |216|23|4,8|
| Cá Linh elite (override, không ID mới) |1152|24|7,56|

Các giá trị ATK/DEF giữ phần thập phân trong công thức, không tự làm tròn ở mỗi bước. Nếu runtime HP là integer, proposal exporter phải chốt quantization cho trường hợp HP không nguyên; bảng trên chọn số nguyên để không âm thầm đặt luật mới.

Mãng Cốt cấp10 minh họa baseHP360 × HPfactor35 =12600 solo. Party2: ×1,65 =20790; không nhân35 hai lần do cả paragraph chung và boss table đều nhắc35. Hệ số boss cụ thể là override của hệ số boss chung; party multiplier áp sau hệ số boss. Các con số này không chứng minh level encounter đã được chọn, TTK hợp lý hoặc defense/attack profile boss đã export đầy đủ.

Oracle kiểm công thức damage: attack20, flat0, coefficient1,5, rank1, damageBonus0, armor10, resist0, không crit/DR → raw30 → floor(30×100/110)=27. Nếu crit thì floor(30×100/110×1,5)=40. Đây là **hit đã được xác nhận**, không bỏ bước accuracy roll. Shield10 hấp thụ10, còn17trừHP ở ví dụ không crit. Multi-hit MK03 dùng0,45/0,55/0,90, không dùng1,90ba lần.

## 3. Trả lời ba câu hỏi cast/VFX của QOD-12

1. **CAST_START cho mọi cast accepted**, kể cả buff/guard/cơ động. Input dự đoán chưa accepted chỉ prep phía client; rejected không phát START/impact giả. START là trạng thái presentation, không tự khóa input đến hết cooldown.
2. **Aim và origin snapshot tại cast start** theo Rules §2; impact dùng kết quả server ở tick hit. Ground-target giữ điểm nhắm đã chốt, còn collision/target alive/range/LOS kiểm lại. DASH không được hiểu `groundXWu/YWu` là endpoint được đảm bảo tới nếu sweep bị tường chặn. CONE cần origin/facing snapshot, không chỉ một điểm đích chung chung. Fields v1 chưa đủ phải có proposal mở rộng/version phù hợp trước emit, không nhét field lạ vào schema đang additionalProperties=false.
3. **Giữ `vfxKey` optional, từ server-owned mapping**. Client dùng skillId + versioned presentation mapping để fallback; không tin đường dẫn arbitrary từ input/remote payload để tải file. Thiếu asset hiển thị fallback đã khai báo hoặc missing, không giả đã có effect.

CAST_END kết thúc thao tác cast, **không mặc nhiên kết thúc buff/mark/trap**. Status/zone có lifetime server riêng; cần state refresh/end hoặc snapshot reconciliation. Cùng cast có nhiều impact cần hitIndex/target/event correlation explicit; schema lifecycle hiện tại chưa chứng minh đủ 30skill/status. Replay cùng command không phát lại audio/impact đã xử lý; cancel không tự refund cost nếu gameplay không quy định.

Aggregate revision phải chỉ rõ thuộc actor hay target; không so một số revision giữa hai aggregate khác nhau. Một event không thể vừa đại diện toàn bộ damage multi-target vừa dùng một revision không xác định owner. Đây là điểm cần Qoder proposal trước transport, không sửa trong gói tài liệu của Codex.

## 4. Các nút còn phải chốt, không được báo đã gỡ hết

- Phản Quang: event counter có điều kiện, cửa0,4s, một thành công/cửa và +2KiếmÝ đã có; nghĩa/thời lượng “giảm sát thương hụt20%”, hướng áp DR và thứ tự counter khi source chết cùng tick còn thiếu precision. Chuẩn bị proposal kèm case trước rollout đầy đủ.
- Attack/collision volumes của dash và multi-hit cần field riêng; range4,4/11 không thay tất cả hit shape.
- Gear examples thiếu stat vector; không được lấy tên kiếm để suy attack. Boss/elite cần resolved stats và attack descriptors trước damage live.
- Reviewed topology và nav/path art evidence còn thiếu; không gắn REVIEWED cho synthetic fixture để bật quest/combat production.
- P1 runtime HP/MP khác baseline: migration cần refill/version note theo Rules, không đổi save hoặc snapshot silently.

Đóng phần “thiếu nguồn” bằng source map trên; phần runtime/export và phần còn thiếu vẫn được theo dõi riêng. Qoder tiếp tục #41, Muse dùng các semantic đã chốt để dựng preview; Codex review proposal cụ thể.
