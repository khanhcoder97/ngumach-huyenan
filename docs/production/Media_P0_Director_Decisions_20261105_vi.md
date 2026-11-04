# Chốt MEDIA-P0 — 05/11/2026
ID: DEC-MEDIA-P0-20261105. Dùng VOICE_GUIDE và skill ngumach-narrative để xử lý lời thoại trong hành động; giữ plot, reward, trigger và thời lượng. Nguồn máy đọc: media_p0_decisions_20261105.json.

- **Q1: chọn B làm canonical.** Ly An: “Đầu kia! Giữ giúp tôi đầu kia!” ở CIN_001_S05, VO 24.8–28.5s. Cô đang ghì kiện và nhìn dây, nói gấp trong động tác. Pack canonical và Directors Pack được đồng bộ.
- **Q2: Ly An là voice off-screen trong CIN004.** characters=[BOSS_MANG_COT] tiếp tục là danh sách on-screen; không thêm world spawn hoặc đặt cô vào giữa đòn trùm. “Nó cứ tránh chỗ nước ấy.” chỉ là nhận xét hành vi đã nhìn thấy.
- **Q3: alternate CIN006 không thay canon.** “Tới đây ta theo được. Chỗ trống này giữ nguyên.” có takeId/version riêng. Canon vẫn là “Ba thứ cùng đi qua một tuyến. Chưa có thứ nào bảo người bán biết mình đang chở gì.”
- **Q4: cho cinematic-only staging.** Dùng identity NPC_HA_MAC và NPC_SAM_CHU_QUY, chỉ actor instance trong video. Không nhân đôi persistent ID hoặc dời default spawn MAP_THANH_LAC/MAP_SA_HOA sang Thăng Long. Binding world là migration khác, không chặn audio/timing/edit.
- **Q5: đã đối chiếu Git.** Work 28/policy có ở 7a85494; integration 8bab575 có hình Bến Mưa mới. Ba nguồn pack/directors/MUSE direction không đổi từ 3557959 tới 8bab575. Quyết định lần này mới đổi Q1, thêm chỉ đạo off-screen và reference owner Codex. Inventory hiện tại: 20 scene/63 shot/378s; P0 CIN001/002/004: 12 shot/72s.
- Git proxy lỗi: dùng đầy đủ decision/work order post ở #116 để tiếp VO/SRT/timing/music/SFX và shot không cần character lock. Không báo đã fetch. Khi mạng phục hồi, merge integration bình thường, giữ WIP.

Environment Bến Mưa mới là reference cho storyboard/animatic. Thiếu named-character keyframe chỉ chặn final picture của shot đó; tiếp các shot nước/dây/kiện và media độc lập. Muse không làm gameplay graphics/UI/VFX; Codex cung cấp character reference.
