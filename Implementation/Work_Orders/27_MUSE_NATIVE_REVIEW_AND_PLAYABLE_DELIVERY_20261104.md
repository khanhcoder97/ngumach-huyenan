# Muse: quyết định sau review native và gói hoàn thiện alpha

Ngày04/11/2026. Theo yêu cầu chủ dự án review hoàn chỉnh bàn giao Muse và quyết định bước tiếp. Đọc `Implementation/Reports/Muse_Complete_Handoff_Review_20261104_vi.md` và evidence kèm helper. **Nhận source prototype M-A, CHANGES_REQUIRED cho PR111/112 trước approve merge; không gọi alpha/fullgame/native10/10 hoàn tất.** Tiếp work26, không thay thế thiết kế đã duyệt.

Giữ PR111/branch `muse/ben-mua-playable-alpha-20261103`; docs PR112/`muse/engine-dec-024` riêng. Baselines765a0d6/bf75cc7. Giữ đúng phạm vi Godot/runtime/art/tools asset; server/wire Qoder, portable core OpenCode. Codex review/tích hợp/merge. Nhận cả R1..R6, push checkpoint thật, chờ review một phần thì làm phần độc lập.

## R1 — sửa regression đã tái hiện và test có exitcode thật

- F1: release joystick phải trả keyboard ownership, không giữ injectedZero. Xử lý cả focuslost/multitouch/release; kiểm controller thật với keyboard sau release, không chỉ test gọi SetMoveInput. Producer log đã tái hiện0px trước clear/21,33px sau clear.
- F4: bỏ assumptions timing cố định cho quãng đường. Test tick/intents/authoritative snapshot và hình học né nước/slide, timeout có lý do; giữ rawlog của mọi lần fail. Không chỉ tăng ngưỡng6,6→7 hoặc0,9→1,2 để pass trên một máy. Sau sửa chạy đủ offline/online và regression fail case; source/server/gates/toolchain ghi rõ.
- F5: bỏ fuser-k/process theoport; port config, startup+health có instance/source identity, cleanup ownchildPID+trap. Capture process exit và RESULT độc lập, fail khi timeout/zeroassertions/buildfailure. Có modeoffline và online-required, missing server ở modeonline-required không exit0. Không dùng server đang chạy của owner để lấy PASS.
- F6: checkout LFS đúng, feed kiểm ZIP/checksum thay tên file, restore lock, không nuốt importerror. Phân loại engine EditorSettings shutdown warning riêng với lỗi missingasset/script, không hide bằng grep. Không tự viết rawtestoutput hoặc sửa bằng chứng cũ.

Checkpoint R1: commit fixes+tests, updated runner, exact commands/rawlogs trên clone sạch, native Windows; phần không có Windows VM thì dùng Linux và gửi gói Windows cho Codex review, không gọi Linux là Windows device QA.

## R2 — một entry gameplay thật và Shared adapter

- Chọn entry sản phẩm menu→session→Bến Mưa có TileMapLayer/collision. Main ảnh nền cũ được giữ làm scene diagnostic riêng; không để chỉ healthpoll khiến người dùng tưởng đã vào fullonline. Server URL/profile cấu hình, lỗi connect có nút retry/back, default loopback private.
- Nối Shared public API thật từ OpenCode; được pin exact SHA trong branch tích hợp thử và gửi dependency manifest, không cần chờ merge109/106 mới code UI. Nếu contract đang thiếu, dùng fixtures gắn DRAFT/OFFLINE rõ và tiếp phần độc lập; không giả route success. Không copy một client protocol cạnh tranh hoặc yêu cầu server theo DTO tự tạo.
- Class gate từ deployment capability, không chỉ hard-code client support. Bốn class chưa mở giữ preview disabled/lý do, không ép request thành MinhKiếm. Một owner identity/session đúng, không dùng một characterId hard-code cho mọi người chơi khi giao alpha multiplayer.
- Nối P00-01 accept→collect→turnin, journal, túi/tooltip, NPC dialog, basicattack/skill/cooldown, target và error/uncertain receipt. Animation có thể anticipatory theo policy, nhưng sát thương/MP/cooldown/reward theo server; rejected/uncertain không auto grant. Hoàn inventoryv2/encounter/death-return/unlock khi Qoder route lên.
- HUD arc đã được giữ, không redraw cảboard. Quest/EXP/HPMP numeric/túi phải bindstate, không sampletext hoặc BagPresses counter. Modal/focus/ESC/touch/safe-area không để input xuyên UI. Giữ tầm nhìn world theo camera chuẩn; không làm map nhỏ lại.

Checkpoint R2a: video/log thực Mainonline P00-01 từ build pin SHA. Tiếp R2b boss/deathreturn/equip/portal, không dừng vì R2a đã gửi.

## R3 — map/collision/animation và gói art có provenance

- Theo PR113: chặn đúng306watercells, giữ37bankcells và floor/path cầu, nav version/hash đồng bộ Qoder trước activate. Footbox/swept/seams/anchor route từspawn tới348 đều kiểm, không cheat teleport. Không tự move anchor, đổi349canonicalplacements hoặc gắn REVIEWED toàn topology.
- Tilemap data hiện450×60/cell0,8WU =360×48WU; ghi đúng phạm vi đã build. Không dùng ảnh7200×960 làm bằng chứng đã hoàn mọi collision/NPC/servernav. Detail/minimap/boats source và layer/floor nhất quán, không thay hình học để hợp tranh.
- Manifest phân biệt legacy48×64 đã giao và64×64 mới. Duyệt giữ48×64 làm bridge prototype, không gọi đó là64px migration. Bộ mới dùng action/row/frameCount/pivot/timing thật theo manifest; không cắt cell48 lênsheet64 hoặc chơi ôtrong suốt. Giữ footplant/weaponbounds/hướng riêng, frameanimation không thay damage window server.
- Thay4placeholder NPC không license bằng art của dự án đã duyệt hoặc fallback marker có nhãn dev và không gọi GD.Load file thiếu. Runtime không còn8ERROR lặp; không khôi phục thirdparty asset không license để làmtestxanh. Nối NPC/quái/boss/VFX thật dần theo pack đã có, lowFX không xóa telegraph.
- Giữ font fallback có đủ dấu cho alpha, localization keys/không bake chữ. Font pixel/asset chưa duyệt giữDRAFT, không chờ font để dừng gameplay. Giao preview sáng/tối/8hướng và provenance/link owner review, không tự promoteRELEASE/ART_APPROVED.

## R4 — build/rebuild/export trên máy yếu

- Build/test/export/launch `.ps1` cho Windows với profile/SDK/URL config, safe quoting, ownPID cleanup, timeout/log và hướng dẫn ngắn. Không yêu cầu Unity/WSL/Bash để chơi. SDK8.0.404 là toolchain tái lập hiện tại; không tự nâng engine/beta/runtime target.
- Asset converters nhận args hoặc repo-relative paths; input Art_Source manifest+hash, output path bounded; không hard-code~/workspace/your_files/godot-prototype. Source chưa phát hành phải ghi thiếu riêng, không gọi pipeline fully reproducible vì binaries có sẵn.
- Xuất Windows portable artifact có SHA256/sourceSHA/dependency/licensing/README; kiểm máy khôngSDK, native OpenGL/input/fonts/audio và một luồng quest. Debug editor launch trên máy cóSDK không thay exported app test. Gửi link artifact thực, không chỉ kích thước exe trong comment.
- Android sửa bootstrap/LFS/fail-fast, có APK thật trong CI và install/launch/gameplay proof riêng. Nếu hạ tầng OOM thì tiếp Windows/art/cinema, ghi blocker chính xác; không làm giả PASS.
- Profile thấp đo FPS/frame-time/RAM/startup ở map/scene/sốactor cụ thể. Native review đã chạy GPU820M, chưa đo tảiMMO; không hứa CCU/FPS vì một ảnh idle. Mục tiêu30FPS vẫn cần chứng minh.

## R5 — PR112 sửa đủ normative docs và codec cinema

- Xác nhận phân vai: Muse Godot scene/runtime/art, OpenCode portableCore/transport/presenters/tests, Qoder server/contracts, Codex review/tíchhợp/design/editorial. Client/Unity presentation là lịch sử; portableCore/Presentation cũ đangSharedlink vẫn đượcOpenCodebảo trì khi migration.
- Sửa P0 URP17.3/PixelPerfectCamera và prompt “GiữUnity6.3” trong AI_Agent_Implementation_Plan; audio import Godot không bắt .meta/GUID/UnityloadType. Giữ ID/assetkeys/source/GUID lịch sử làm provenance, không đổi closed schemas hàngloạt. Chỉ thay quy định hiện hành, không search-replace mọi lịch sửUnity.
- Godot version/features/import metadata pin4.7.2; ghi normalizations khi import sạch. PACKAGES.md phải nói đúng16nupkg LFS tracked hoặc thật sự chuyển sang downloader đượcverify; đừng để mô tả đối lập source.
- **Chốt đường cinema ngay:** runtime `ClientGodot/assets/cinematics/<cinemaId>/` với `.ogv`+posterPNG, metadata/SRT/audio stems theo Narrative/Deliveries và Art_Source đã có. MP4H.264 là bản review/master, không mặc định engine core phátMP4. Không thêm extension video để né quyết định này. Godot core hỗ trợ OggTheora: https://docs.godotengine.org/en/stable/tutorials/animation/playing_videos.html .
- Giữ cadence30fps của pack đã chốt; Low preset có bản640×360/30fps và standard1280×720/30fps, test CPUdecode trên máy yếu. Giữ nearest/pixel cadence/no opticalflow, audio/stems/SRT/Vietnamese. Encoding không được thay shot/nội dung đã duyệt.

## R6 — cinema/story và bằng chứng cuối

Tiếp opening/CIN006 theo DirectorsPack/narrative đã duyệt: storyboard→animatic→actualtake→runtimeOGV. Nguồn chưa có video ghiREQUESTED/ANIMATIC đúng, không đường dẫn giả. Player có skip/seen/subtitle/audio/fallback; event kết thúc chỉ báo view, không tự hoàn quest/grant thưởng. Shared server không pause vì video; chỉ vào cinematic ở trạng thái game cho phép, handle disconnect/skip/replay không nhânreward. Gửi Codex review take trước final render.

Gói cuối gồm source pin, lock/feed/license, manifests, actualart/video, rawtestlogs+exitcounts, Windowsartifact và deviceproof. Checkpoint source/runner, mainP00-01, boss/map migration, cinema được gửi riêng trong cùnggói để review sớm; **không dừng saucheckpointđầutiên**. Một upstream chờ thì tiếp phầnđộclập. ACK #1/#111 với branch/SHA/Rđangcode, docs tại112, dependencies báo #85/#41. Không tự merge hoặc tự đánh APPROVED/REVIEWED; productionOFF.
