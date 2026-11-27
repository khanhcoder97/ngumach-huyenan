# Owner override: Muse chỉ media, Codex tiếp quản toàn bộ hình ảnh/runtime

Đọc `Visual_Reboot_And_Muse_Scope_20261104_vi.md` và policy agent_scope_v2.json. Lệnh mới của chủ dự án thay mọi scope cũ của Muse trong work24..27; không thực hiện tiếp các phần graphics/runtime vì chúng từng được giao. Codex chịu trách nhiệm asset/map/UIUX/VFX/animation/Godot runtime và làm bộ hình ảnh mới; OpenCode/Qoder/remote giữ scope hiện có.

## Muse — gói MEDIA-01, nhận toàn bộ V1→V4

**Không được làm:** sprite/character animation cho gameplay, map/tile/collision, UI/UX/icon/font, skillVFX/weather game, Godot scene/scripts/shaders, engine/docs ownership, portableCore/server/schema. Không sửa lại111/112/22, không ghi đè file Codex. Giữ WIP/source cũ để bàn giao archive, báo exactSHA/paths/status, không xóa hoặc tự restore graphics vào client.

**Nhánh mới:** muse/media-production-20261104, chỉ các root/extension trong policy. Runtime video/audio code do Codex làm. Media source được giữ ở Art_Source/Cinematics và Art_Source/Audio/Muse; delivery vào ClientGodot/assets/cinematics hoặc assets/audio; SRT/manifest vào Narrative/Deliveries hoặc Audio/Deliveries. Báo cáo MuseMedia riêng. Công cụ media CLI đặt Tools/MediaProduction/Muse, không sửa workflow hoặc code engine.

### V1 — toàn bộ inventory media và lịch sản xuất theo narrative hiện hành

Đọc narrative/DirectorsPack/AudioDirection/cue manifest hiện hành, lập danh sách cinema/shot/VO/cue với canonical IDs thật và dependency. Số lượng phải lấy từ source version, không hard-code con số trong chat cũ. Ưu tiên opening và CIN006, sau đó các bước ngoặt/thám hiểm/các chapter còn lại. Gửi source/timeline/shotlist/format/path/visual reference version rõ ràng. Các hình ảnh mới của Codex là nguồn diện mạo; không dùng art Muse cũ vì file tiện có.

### V2 — video/cinematic có bản xem và delivery thật

Storyboard/animatic/timing từ script đã duyệt, rồi actual takes, edit và sound. Không tự đổi plot/thoại hoặc chỉ render cảnh đánh nhau; giữ nhịp khám phá/không gian/chi tiết câu chuyện. Source/master, MP4 review, OGV runtime + poster, SRT UTF8/NFC, VO/music/ambience/stems và manifest có hash/provenance/license. Giữ30fps/cadence pixel đã chốt, có low640×360 và standard720p; không opticalflow hoặc lẫn art style. Reference chưa khóa thì làm animatic/timing/audio/subtitles, chờ phần hình cụ thể chứ không dừng gói. Final takes gửi Codex review trước tốn toàn bộ render.

### V3 — âm thanh toàn game

Tiếp/improve gói audio theo cue IDs sẵn có: nhạc khám phá/an toàn/nguy hiểm/boss/city, ambience nước/mưa/rừng/chợ/bến/cave, bước chân/weapon/impact/skill/telegraph/UI/item/quest và VO thoại đã được duyệt. Tránh âm tổng hợp chói/gắt, cảnh báo phải đọc rõ giữa combat; không dùng nhạc/sample không license hoặc clone giọng người thật. Character voices hư cấu, phát âm tiếng Việt/tên riêng thống nhất, diễn xuất có chủ đích.

Source WAV/stems và runtime OGG/WAV theo spec, loudness/peak/loop/click/variant/minGap/priority/voiceCaps có kiểm đo và bản nghe thật; không preload master vào client. Playlist audition với cue ID, raw metadata/hash, license/source version, naming/chapter/dialogue mapping. Không coi tone generator hoặc file rỗng là cue final, không báo toàn game xong vì số file đủ. Không sửa cooldown/damage/receipt hoặc đặt logic grant ở audio event.

### V4 — kiểm chứng và bàn giao liên tục

CLI validation đối chiếu actual media bytes, codec/duration/fps/sampleRate/channel/loudness/loop/subtitle timing/hash và source provenance, không tự viết log PASS. Giao opening+audio palette đầu, tiếp cinematic/cue packs lớn và VO còn lại; không dừng sau một clip/ACK. Khi chờ visual reference hãy tiếp sound/music/VO/subtitle/encoding. Báo blocker cụ thể, không quay về làm sprite/UI để lấp thời gian.

Mỗi checkpoint PR media-only có actual files/LFS bytes, metadata, preview nghe/xem, exactSHA/commands/limitations. Codex review, không tự merge hoặc gắn APPROVED. Production OFF. ACK scope mới ở media epic và bàn giao trạng thái dở của gói cũ.

## Codex — tiếp quản và sản xuất mới

1. Đóng/freeze PR graphics/runtime Muse, giữ lịch sử và kiểm diff phạm vi mới; thông báo các đội về đầu mối mới.
2. Dựng art bible/coverage registry và bộ nguồn mới: concept cohesive, sprites độc lập, terrain/props, pixel UI sống và VFX. Lưu prompt/modeloutput/hash/QA state, không cắt concept làm asset. Loại candidate sai grid/hand/pivot, không ship chỉ vì trông đẹp.
3. Godot runtime mới dùng thành phần có metadata/validation rõ và scene thử riêng; sửa input/collision/poll/UI binding đã review. Bản cũ chỉ làm tham chiếu code/data, hình ảnh mới không dùng lại sprite/UI của Muse. Không thay canonical game rules hoặc server contracts khi đổi art.
4. Nối OpenCode portable API và Qoder wire khi có checkpoint đúng; boss/world view owner-scoped, inventory12slot v2 và private alpha gates giữ nguyên. Codex tích hợp video/audio mà Muse giao.
5. Native visual QA trước mở rộng: whole-body frames/cellpadding/8directions/footplant, mapseams/nav/collision, UIarc/safearea/text/focus, VFX readability/timing/LowFX. Báo đúng phạm vi chưa hoàn, không tuyên bố remake toàn game xong từ lô đầu.

## OpenCode/Qoder

Đầu mối gameplay client/art/runtime từ nay là Codex, không Muse. Tiếp work26 và các blocker đã được giải quyết; gửi schema/fixtures/API/contract checkpoint cho Codex. Muse chỉ nhận media cues/script timing cần thiết, không được giao lại patchGodot/UI/VFX. Không reset/stash/clean worktree khác hoặc sửa đồ họa thay Codex.
