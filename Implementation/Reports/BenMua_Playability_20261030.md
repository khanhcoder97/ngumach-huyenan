# Bến Mưa v1.1 — điều khiển và an toàn bản lưu

Codex tiếp tục phần client/local playtest; OpenCode đã nhận gói liên tục qua issue40 comment6509400796: sửa PR43/61/62, kiểm bundle/CI67/69, candidate compiler và adapter asset Bến Mưa. Chưa có xác nhận OpenCode đã chạy gói mới; không gọi việc đăng comment là agent đã bắt đầu.

## Code được hoàn thiện

Khóa/chuyển mục tiêu bằng click/T/nút, target HP/range/ring, ưu tiên target hợp lệ cho đòn đơn; giữ Space/pointer đánh liên tục và áp sát có giới hạn, input tay ưu tiên. Target/death/phase/range được kiểm lại, không lưu target vào save. Xuất/nhập save file, giới hạn64KB/schema, xác nhận trước thay tiến độ, backup bản trước, fallback bản hỏng, bảo toàn committed primary khi write fail và vẫn mở game khi storage bị chặn. Save v1 cũ giữ tương thích.

Sửa scope cleanup khi teleport/respawn, boss reset emit lifecycle để dừng nhạc boss, tutorial wave chỉ ở khu đầm. Không sửa server/contract/canonical item/spawn/topology. File/chỉ số import là local playtest, không quyền nhận thưởng online.

## Đã kiểm tra

- Engine full-run: **68 assertions PASS**, đi đủ5quest/boss/exit bằng các command/movement bình thường; regression có fixture riêng.
- Playability: **38 assertions PASS**: chọn/đổi/loại target, preferred hit có range check, death/phase cleanup, teleport, lesson area, boss reset không reward, v1 compatibility, export/import, invalid type/version/fields/size, corrupted primary/previous, storage/get/write/backup failures.
- HTTP/assets: **4 tests PASS**; JavaScript syntax check PASS. Packer bổ sung save-store.mjs vào ZIP để import trong bản standalone.
- Browser QA có namespace save riêng: mở manager từ title; dùng file **synthetic** quest2/x73, hiện confirmation trước commit; xác nhận rồi tiếp tục, quest2/XY đúng; T khóa Cá Linh, HUD hiển thị116HP và range4,4m. GiữSpace2,2s: nhân vật đi từ73,0 tới77,1/-1,0, target còn59HP, player190HP. Không console error lúc đọc log sau thao tác khóa target. Đây là test combat có fixture, không claim full5quest browser playthrough.
- Lượt thử bổ sung kỹ năng/thuốc/chụp ảnh sau đó bị browser-control timeout/reset, chưa có ảnh mới hoặc kết quả đủ cho lượt đó. Không coi timeout là PASS của pointer/touch/skill combo; ảnh gameplay bản trước vẫn là evidence bản trước.

Server local đã dừng trước đợt này, nên được mở lại bằng Python process nền riêng ở127.0.0.1:8090; API info đọc lại đúng LOCAL_SINGLE_PLAYER_PLAYTEST. Không tạo startup task/service hoặc mở port public; log/PID chỉ ở export local, không là cấu hình production. Không reload/sửa save phiên người dùng trong QA.
