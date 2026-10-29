# Tích hợp âm thanh vào client P1 — đợt đầu

Codex sở hữu module này. Trạng thái: **CODE_ADAPTER_CREATED / UNITY_ENGINE_UNVERIFIED**. Nguồn audio là pack195cue/541clip trên main qua #55; code nằm cùng client draft #51. Không sửa art/Animator/builder của Muse, server/contracts của Qoder hoặc DSP/media/manifest gốc.

## Phần đã triển khai trong code

| Phần | Hành vi |
|---|---|
| Core policy C# độc lập Unity | Parse195cue; kiểm key/path/finite/duplicate/voice caps, semantic/audience/scope, vị tríXY, budget per-cue/per-group và priority stealing |
| Replay và biến thể | Dedupe tuple(scope,eventId,cueKey,hitIndex), cửa8192event; minGap; round-robin không lặp ngay; MK03 chọn0/1/2 theo hitIndex |
| Mixer | Master/Music/Ambience/SFX/UI, gain0..1; mute giữ gain cũ; one-shot nhận khi mute bị tiêu thụ để không phát muộn lúc unmute |
| Cảnh báo | Duck Music/Ambience theo thông số manifest, không vượt mute; spatial attenuation/pan dựaXY, không dùng worldZ |
| Unity player | Resources theo từng cue, nguồn AudioSource riêng; không gọi Resources.LoadAll cho541clip; giữ tối đa48cue handle, giải phóng voice khi hết/đổi scope/đóng panel |
| Bảng âm lượng | Nút Âm thanh trên HUD, mute và5slider, lưu setting PlayerPrefs; panel cuộn, dừng movement/keyboard cast khi đang chỉnh |
| Dịch vụ nhận quest | Chỉ xếp notice sau response accept thành công/ACTIVE đã được client validate; retry không chắc kết quả giữ cùng key, không phát thành công sớm |

Core policy dùng bởi một presentation thread; inbox notice của P1Client có lock riêng. Mọi request/state vẫn do client lane/server quyết định. Audio không cấp HP/MP/vật phẩm/quest progress.

## Mapping hiện nối thật trong source

| Cue | Nguồn kích hoạt |
|---|---|
| SFX/UI/confirm | Nút lệnh và input cast được UI chấp nhận; tiếng nhấn nút, không tuyên bố cast/hit thành công |
| SFX/UI/error | Kết quả lỗi của lệnh người chơi; polling mất mạng không liên tục phát beep |
| SFX/UI/panel_open | Mở nhật ký/túi/âm thanh |
| SFX/UI/panel_close | Đóng các panel trên |
| SFX/QUEST/accepted | Notice một lần sau accept200/ACTIVE hợp lệ, gồm retry của command mất phản hồi |

Focus chưa nối vào navigation focus của UI. Nhận thưởng/nhặt đồ/forge/kill/status/hit/counter/footstep/music/ambience **chưa nối gameplay** trong đợt này. Policy đã có support để kiểm budget/duck/loop/spatial bằng tests; điều đó không đồng nghĩa event adapter hoặc nhạc vùng đã hoạt động trong game.

`combat.effect` hiện hành không được đổi thành COUNTER_CONFIRMED/HIT/HEAL. UI chưa gọi Play cho skill hay warning theo event cũ. Item/buff cue ghi LOCAL_PRESENTATION trong pack vẫn cần committed semantic; policy không tin nhãn đó để cho phép một click UI tạo âm giao dịch thành công.

Notice accepted dùng idempotency key của **command đã được xác nhận**, không tạo event wire mới. Scope hiện là namespace UI local tạo lại khi session/map thay đổi, không được gọi là mapInstanceId authoritative. Chưa có API phát world combat trong P1AudioPlayer; muốn nối cần Qoder giao lifecycle/audience/instance/floor đã review. Snapshot/reconnect initial readback giữ im lặng, không phát lại reward hoặc lịch sử combat.

## Tạo catalog Resources trong Unity

File gốc ở `Client/Assets/Audio/PackV1` không nằm trong Resources. Loader không giả dùng Resources.Load trên đường dẫn Assets/Audio. Cầu nối Editor nằm riêng tại `Scripts/Online/Editor/P1AudioCatalogBuilder.cs`:

1. Checkout exact head client đã review, `git lfs pull`, mở `Client` bằng Editor đã ghi trong ProjectVersion và resolve packages.
2. Đợi import audio/code xong. Chọn menu **Ngu Mach → Audio → Build Runtime Catalog** trước Play.
3. Builder kiểm mọi AudioClip import/reference trước khi ghi; tạo một P1AudioCueAsset mỗi cue, mỗi asset chỉ tham chiếu các biến thể của cue đó; sao metadata JSON vào `Assets/Resources/P1Audio/catalog.json`.
4. Resources sinh ra được gitignore; có thể tái tạo từ manifest/clip cùng commit. BuildPipeline có preprocess hook tạo lại catalog. Muse chạy builder art/animation riêng vẫn cần bước menu này trước audition Play; không sửa BuildAll của Muse.
5. Nếu chưa có catalog, UI báo âm thanh chưa sẵn sàng, gameplay tiếp tục; không suy file bị thiếu là engine đã import thành công.

Không commit runtime Resources generated trong PR art. Không đưa master/preview MP3 vào build. Khi đổi schema hoặc resource mapping phải review code/manifest cùng nhau. Builder chưa dọn asset cũ bị bỏ khỏi catalog; release build nên dùng checkout mới để tránh stale generated resource. GUID nguồn audio hiện có được giữ nguyên; generated cue resources được resolve bằng resource key, không phải save-game GUID.

## Vòng đời và giới hạn

Đổi session/map hoặc hết phiên: dừng voice trước khi cập nhật scope. Close/OnDisable dừng nguồn, bỏ clip refs và lưu setting. Listener được bootstrap camera kiểm/tạo một lần khi thiếu, không tạo rồi hủy theo mỗi panel để tránh mất listener khi vào lại nhanh.

Cache48 là giới hạn handle giữ bởi module, **chưa là số đo RAM Unity**. AudioClip do Resources quản lý và tài nguyên import/streaming còn cần profiler; không tự UnloadAsset clip đang có thể được module khác tham chiếu. Load cue hiện synchronous, cần đo hitch khi dùng lần đầu. Music crossfade/loop fade/cancel scheduling, preload theo vùng, pooling AudioSource và background/device audio-focus chưa hoàn thiện; gameplay loops chưa được nối nên không được báo đạt các gate đó.

Dedupe giới hạn8192event để tránh giữ lịch sử vô hạn; caller phải chặn event lịch sử ngoài stream window ở future world adapter. Audio không tự xác minh payload mạng; chỉ nhận notice từ response đã validate và local UI allowlist. Không dùng API presentation như anti-cheat server.

## Kiểm tra và gate Muse

`Client/Tests/P1CoreChecks` compile chính source Core và chạy fake-transport fault cases, rồi audio policy tests với catalog195cue thật. Có traversal/non-finite/alias/cap checks, semantic/counter false-positive, audience/XY, mute lịch sử, minGap/variation, stealing, hitIndex, ducking, map stop, finite attenuation và hết voice. Core tests thêm initial-readback silent, accept timeout/retry một notice, reject không phát success, combat.effect không phát counter. CI tiếp tục HTTP default-OFF và dev proximity/accept/replay với server thật.

Local không có .NET SDK/Unity nên không ghi local compile PASS. CI core không compile UnityEngine/UI Toolkit/Editor source. Muse cần giao exact SHA, Editor/package version, compile/import log và video có âm: build catalog195cue → vào client → mở/đóng panel/nhận quest đúng gần NPC → mute/unmute/đóng-vào lại. Cast Phản Quang được chấp nhận phải **không** phát parry khi chưa counter. Poll mất mạng không spam beep; retry accepted chỉ một tiếng; restore/readback không replay; kiểm1listener, voice count, Resources memory, lần load đầu và1080p/20:9/720p.

Giữ PR #51 draft đến khi có engine evidence. Pack audio gốc vẫn giữ LISTENING_REVIEW_PENDING/ENGINE_UNVERIFIED; code bridge không tự nâng trạng thái cả195cue thành integrated/final.
