# Kế hoạch hoàn thiện mỹ thuật từ concept v1

Chủ dự án yêu cầu Codex thiết kế mẫu để Muse bám theo. Năm board ở Art_Concept_References/v1 là hướng tạo hình mới; quy định chức năng/canon/DEC-015/016 vẫn thắng sai lệch ảnh sinh. Không tuyên bố đã hoàn thành asset cả game từ năm ảnh này.

| Ưu tiên | Gói | Đầu ra đủ để nghiệm thu |
|---|---|---|
| P0 | Minh Kiếm sửa chất lượng | 3pose S/SE/N native→8pose→walk→attack; gem/hair/cape đồng nhất, defects checklist, không full-sheet trước gate |
| P0 | Bến Mưa scene kit | ground/water/shore16px, pier/house/reeds/lantern, Ly An và Cá Linh; mockup640×360, không thay nav geometry bằng ảnh |
| P0 | Cinema opening | keyframes CIN_001 theo board Bến Mưa/Ly An và Directors Pack; storyboard trước video, giấu avatar mặt/class |
| P1 | UI core | HUD/skill/inventory/equipment/settings frame và icon states, font tiếng Việt; neutral gameplay screenshot, safe area và native readability |
| P1 | Quái/boss slice | Cá Linh/Rễ Nước/Mãng Cốt idle/move/telegraph/attack/hurt/death,3đòn đúng spec, collider guide riêng |
| P1 | Thăng Long kit | phố chợ/forge/guild/canal/cổng/arena, tileset16px và prop modular; density/collision map cần reviewed topology |
| P2 | 4class tiếp | Anh Đao/Huyền Bút/Thạch Chùy/Linh Cung variants; dùng board05 để phân vai, không khóa giới tính |
| P2 | roster và thế giới | NPC/quái/mount/pet/gear/46map/environment/VFX/UI còn lại theo catalogue; mỗi asset có alias/reuse rõ, không giả đủ vì có ID |

Muse phụ trách art/source/video; OpenCode tạo contact sheets, palette/frame/meta checks nhẹ, không tự đánh giá đẹp bằng validator; Qoder giữ topology/collision/server authority. Codex review milestone bằng hình thực và đưa một vòng sửa cụ thể, tránh nhiều lời nhắc chung chung.

Mọi gói có trạng thái REQUESTED/DRAFT/ART_REVIEW/ART_APPROVED/ENGINE_IMPORTED/DEVICE_QA trong sidecar khi schema sprite chưa hỗ trợ. Board nằm docs; runtime sprite mới mới nằm Client/Assets/Art và đi qua validator. PNG board không đưa vào manifest runtime.
