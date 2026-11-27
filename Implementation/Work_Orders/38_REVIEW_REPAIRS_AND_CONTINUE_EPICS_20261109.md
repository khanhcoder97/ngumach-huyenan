# Gói38 — sửa bàn giao và tiếp epic34–37

Chủ dự án yêu cầu kiểm bàn giao, review và tiếp tục giao việc. Baseline integration đã merge PR129 tại `f715436367dc78116505abd1b960ce64e2652060`, gồm work33–37 và inventory/progression approval; tutorial approval từ PR128 vẫn hiệu lực. Không cần hỏi lại các nguồn đã duyệt. Review độc lập và evidence: `Implementation/Reports/Review_20261109/Agent_Handoff_Review_vi.md`.

Đây là chỉ đạo đang giao, không thay epic lớn bằng report mới. Giữ scope owner hiện hành và production OFF. Mỗi checkpoint gửi branch/full SHA, source/contract version, commands/output/CI, actual delta và remaining gaps; tiếp phần độc lập sau push. ACK không thay code. Không reset/clean/force-push worktree khác hoặc xóa file user.

## Qoder local — issue87, đồng bộ41; QOD21/PR106 là nhánh giao chính

1. **Q38-A: hội tụ hai nhánh.** QOD18 `fd046193` và QOD21 `4cada354` cùng tổ tiên ae21088, không phải chuỗi tiếp nối. Lập patch inventory theo commit/file; giữ WIP/history, tiếp trên QOD21 và đưa từng delta đã review qua. Không merge nguyên root37lỗi. Loại temp_rgba.png/test.png khỏi proposed agent diff, giữ nguyên file user. Sửa report completion sai source/branch và cập nhật cả PR91/106.
2. **Q38-B: finale runner và public acceptance.** Pin4cada đã PASS626self-check/build/content, nhưng alpha HTTP fail ở assertion đọc `quests` trước TALK. Fetch state sau mutation rồi kiểm credited/READY; không kết luận server lỗi từ old state. Sửa portal runner đúng `TP_BM_THANH_LAC`348→8 và `TP_TL_BEN_MUA`20→348; parse snapshot đúng, replay cùng key/body thực, conflict khác body, refusal ngoài map/range. Giao run P00-01→boss→fragment→classconfirm→READY→turn-in→chapter→portal→return; low-levelC1 vẫnLOCKED. CI e2e-alpha phải xanh cùng head.
3. **Q38-C: MAP_VIEWED/escort đúng source.** Giữ explicit POST map-viewed, tuyệt đối không credit do map-enter/GET/portal. Schema/example/negative fixture và validator trước handler. Alpha C1 giữ2TALK cũ, append objective được duyệt, migration/attempt1/floor/map checks. Nối call path thật; helper CreditMapEnter/ResolveClassMasterToken đứng riêng chưa đạt. Escort provenance+coords từ một sample/AOI theo approval, không mở frozen world schema.
4. **Q38-D: catalog tương thích.** Sửa37content/schema errors và vocabulary; không nới frozen v1SkillIdPattern bằng regex đa class khi schema/activation chưa hỗ trợ. Canonical ACTIVE/runtime additions phải có approved overlay/provenance, không thay state bằng tay. Model đủ cast range/radius/timing/passive/status và parser/activation gates trước khi gọi30skill hỗ trợ. Không tự chọn balance mới để vượt validator.
5. Sau A–C đủ acceptance, tiếp work35 Q-B/C progression/stat/capacity/consume theo JSON đã duyệt; song song làm typed domain/model đủ nguồn cho Q-D→J. Không dừng cả epic vì chờ review finale. Gửi full DTO cho Remote, không viết Persistence/DB. Không sửa Godot/client/media.

## OpenCode LOCAL — issue85; tiếp PR109 và work34

1. **O38-A: authoritative owner guard P1.** Probe pin9d4d811 cho default server-assigned character nhận encounter CHR_FOREIGN và emit event, trong khi explicit character chặn. Capture identity server cấp cùng epoch, validate owner ở cả đường default/explicit; relogin/queued stale/mismatch không đổi view/cache/event. Không dùng constructor preference làm authority. Thêm tests default/explicit/relogin/queued, positive cùng owner và negative foreign; giữ suite317baseline và full build/pack xanh. Probe source nằm trong report Harness.
2. **O38-B: adoption/paired.** Sửa trước khi Codex nhận ClientSession. Giữ các wire/conformance/LF pin/transport fixes đã đóng, không làm lại report lỗi cũ. Paired với Qoder head mới sau khi Q38-B qua, ghi client/server/content pins, gates-off và private-alpha có assertions>0. Approval MAP_VIEWED đã có; ghi chính xác đang chờ server schema/handler nếu chưa bàn giao. Contract mới phải version/parser/fixtures rõ.
3. Viết lại handoff UTF-8 từ source/log vì comment hiện có dấu `?` mất nội dung. Tiếp work34 lifecycle/presenters/services/media bridge/package/CI theo capability thật. Portable Core/Presentation/runner thuộc OpenCode; Godot scene/NativeOnlineSession/UI/UX/VFX/camera thuộc Codex; compiler pipeline cũ không được giao lại.

## Muse — issue116; tiếp work37, media-only

1. Nhận tiến bộ783runtimeaudio/21embeddedentries/campaignmix đầy đủ và Windows runtime-byte/policy checkpoint. Giữ NOT_AUDITIONED tới khi có nghe thực; không gọi codec/hash là final picture/mix. Không cần thêm clone/hash checkpoint cùng783bytes. QA mới chỉ khi binary/policy/tool đổi hoặc lỗi; xuất exact delta từ baseline14b588.
2. **M38-A: P0 candidate để review thực.** Từ motion A/B hiện có, giao một candidate P0 có cut/clip/contactsheet, timing/camera/pose notes, candidate selection rationale, audio routing và subset manifest/hash. Giữ DRAFT, không tự thay runtime gói lớn trước review. Giao source closure đủ để Codex xem/nghe/ghép Godot; không bắt Muse viết native scene. Không coi procedural multi-pose là final diễn xuất nếu chưa xem.
3. **M38-B: selective runtime ingest.** Giao manifest cho subset P0 và hướng dẫn embedded vs external đúng một đường audio, cues/subtitles/seams/fallback, license/provenance. Ear pack196items/7playlists dùng cho audition thực; chưa nghe thì gửi đúng trạng thái, không tự chấm PASS. Windows runtime subset đã audit không là full-source/network QA. Có device thật thì ghi thiết bị/output và issue; thiếu device tiếp asset production độc lập của work37.
4. Tiếp motion/continuity, score/stems/transitions/intensity/SFX/VO/ambience còn lại bằng thay đổi asset thật; không tăng số report lặp. Chỉ cinematic/video/audio và tool media được phép. Gameplay art, Godot graphics/UI/UX/VFX/camera không thuộc Muse.

## Qoder Remote — issue79; tiếp work36

R1 vẫn là deliverable đầu tiên, chưa có head/ACK mới: tracked library csproj, test/harness csproj, dependency lock/config cần thiết, clean clone build/test với test count>0 và TRX. Push source và exact head thay vì báo interface-only hoặc server CI chung. Sau R1 tiếp full work36 atomic transactions/receipts/outbox/fencing/two-process crash-recovery/backup/adapters; không nối Health writer trước module review. Local Qoder DTO là đầu vào, không là ACK của Remote. Chưa có source thì trạng thái là chờ bàn giao.

## Codex — review/integration

Nhận từng subset với dependency closure đã kiểm. Chờ O38-A và Q38-B trước native session/gameplay adoption; P0media candidate có thể review song song. Giữ graphics/UI/UX/VFX/camera/input/native, không merge toàn PR91/106/109/119 qua màu CI. Hai approval inventory/tutorial tiếp tục hiệu lực; không phát hành production hoặc tự cấp level11. Cập nhật issue4 bằng kết quả thực, phân biệt giao việc, ACK, push, test và acceptance.
