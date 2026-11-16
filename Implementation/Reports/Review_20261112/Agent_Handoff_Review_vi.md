# Kiểm bàn giao — 12/11/2026 JST

Đọc issue85/87/79/116/4/41 có pagination đầy đủ, so với gói38 đã merge ở integration9ac73dc. Review trên worktree riêng theo exactSHA; giữ root workspace QOD18 với commit local e9fd532, P00-05 sửa dở và .qoderignore untracked. Không sửa, reset hay đồng bộ ngược workspace đó.

| Owner | Head GitHub được kiểm | Kết quả / disposition |
|---|---|---|
| OpenCode PR109 | `85719a7ecdaa10d3ad2d20d32077a78cea88b92b` | 324/324unitPASS; repro owner cũ đóng; hai presenter còn gap provenance/media boundary |
| Qoder PR106 | `4cada354fc9efc1f1f4fff9c1d8acf9bccba6731` | Không đổi từ review09/11; finale runner còn lỗi, portal domain DTO sai wire schema |
| Qoder PR91 | `fc86916f21510e40fac0fd8a1c936cbb27a165a0` | Delta từfd04619 chỉ2report; chạy lại content vẫn FAIL37; không chấp nhận “all WO32 completed” |
| Muse PR119 | `b1472f2bb356852f49bbb127dd40dc4f99a79df2` | Có candidate/ingest/continuity/720review/hold/SFXproposal; runtime byte/hash PASS783audio+107cinematicrefs; nhận draft checkpoint có giới hạn |
| Qoder Remote PR98 | `5371a4675fbd8fc4b41b4748f2b1732ef2d81824` | Không source/ACK mới; R1 project/test/harness chưa có |

Snapshot CI: PR109 có17success,119 có11success,106 có29success/1failure,91 có6failure/2success,98 có6success. Check-run count khác run count và không thay domain/native/media acceptance. Gói39 giao tiếp việc thật cùng disposition8leg OpenCode hỏi; JSON mới duyệt draft SFX cho Muse, không merge executable gameplay/media.

## OpenCode: đóng owner repro, giữ review cho các presenter mới

Unit command SDK8 trên pin85719a7 kết thúc324passed/0failed/0skipped. Build có CS1998 warnings, không gọi toàn build0warning. Probe từ review09/11 chạy lại qua public API với worldCHR_TEST + foreign encounterCHR_FOREIGN:

```text
explicitRequestedIdentity=False ... accepted=False outcome=Error deliveries=0
explicitRequestedIdentity=True ... accepted=False outcome=Error deliveries=0
```

Đóng finding cụ thể O38-A default server-assigned character. Field mới capture identity tại Connect và clear relogin đã sửa repro. Không suy hai case này thành mọi epoch/relogin/queued owner đã đủ; work39 giữ các regression đó. Owner test/probe là fixture transport, không là phát hiện server leak.

### [P1] Escort ghép row v1 cũ vào map/tick v2 mới

`Client/Assets/Scripts/Online/Presentation/EscortPresenter.cs:85` fallbackworldv1 khi v2 không có NPC chứaLYAN; map/tick vẫn lấyv2 ở phía dưới. Presenter cũng nhận generic/static NPC bằng substring và suy IsOnRoad từx42..120, thiếu owner/attempt/life/instance/floor của escort packet đã duyệt.

Probe public presenter: v2mapThanhLac/tick500 khôngentities, v1mapBếnMưa/tick10 cóENT_NPC_LYAN_STATICx90. Output:

```text
escort v2AbsentButV1OldNpc inAudience=True entity=ENT_NPC_LYAN_STATIC map=MAP_THANH_LAC tick=500 x=90 onRoad=True
```

Như vậy published view biểu diễn NPC cũ dưới map/tick mới và gọi đang hộ tống. Không phải bằng chứng vị trí server sai; đây là consumer projection sai. Cần một snapshot/epoch nhất quán, không fallback xuyên version, generic NPC không được coi owner escort. Route/provenance chưa bàn giao thì unsupported/not-served, không đoán. Test hiện có chỉ syntheticENT_NPC_LYAN_ESCORT một snapshot, chưa bắt hybrid case này.

### [P2] Media boundary chưa validate metadata/path/audio role thực

`MediaPlaybackPresenter.cs:132` chỉ so requestedPath với AllowedPaths do caller tự cấp và chặn substringvo_/standalone khi EmbeddedSoundtrackOnly. Không có parser PLAYBACK_METADATA_v1, path containment/canonical root hoặc typed audio ownership; hai test dùng Assets/Media giả. Probe:

```text
media traversalInAllowedList accepted=True phase=Playing
media externalMixUnderEmbeddedPolicy accepted=True phase=Playing
```

Case1 đưa../../private.mp4 vào allowlist rồi load cùngpath. Case2 đưa pathWAVmixP0v3 thực vào allowlist, EmbeddedSoundtrackOnly=true vẫnPlaying. Đây là boundary validation gap so với claim “approved content root/embedded-soundtrack enforcement”; presenter chưa đọc filesystem hay có player nên không kết luận đã exploit/truy cập file hoặc đã phát đôi âm. Cần loader từ actual21entry Muse với path/role/codec/SRT và mutual exclusion theo metadata, thay vì substring. Seen/skip/rewatch vẫn presentation-only. Native/player/widget thuộc Codex, không giao ngược OpenCode làm scene.

### Paired acceptance: phân biệt route/domain, typed success và runtime pin

OpenCode có tiến bộ runner full tutorial268assertion, receipt behavioral, contract70file, trace fixtures/buffer bound/package/sample. Các số trong handoff không tự là owner verification. Trace source vẫn fixture; buffer caps không là benchmark allocation/low-device performance. License game vẫn UNSPECIFIED, không tự gán license.

Portal-positive ở4cada35 có defect thật nhìn được từ source: P1Results.PortalSuccess serialize PortalResult trực tiếp; propertyDestinationMapId/DestinationXWu/DestinationYWu thành destinationMapId/... trong JSON, trong khi frozenPortalResponse yêu cầumapId/xWu/yWu vàadditionalProperties=false. Qoder phải map wireDTO đúng; Core strict rejection vẫn đúng. “behavioral receipt/arrival pass + typedLastPortalnull/pendingUncertain” không là alpha typed portal hoàn tất.

Nhưng encounter404 đã bị diễn giải quá rộng trong tổng kết.4cada35 cóMapGet/p1/encounters/current và/{encounterId}; handler trả domainencounter_not_found nếu không active snapshot owned. Read sau death/portalcleanup có thể trả404 đúng. Cần probe trong active encounter trước death, observer/foreign404 là negative; không tạo route trùng hoặc yêu cầu Qoder viết endpoint đã có. Consume/map-viewed/escort/current chưa có ởpin này tiếp unsupported rõ.

Review đã chạy paired client85719a7→server4cada35 bằng process riêng. Lượt đầu tôi truyền content-root=Implementation/Content; server discovery có thể tìm lên parent nhưng runner fingerprint join lạiImplementation/Content nên trả{}. Probe cùng helper ở checkoutroot trả6hash, nestedroot trả0; runner vẫn đi đến healthy server/HTTP. Đây là giới hạn evidence pin, không phải proof dùng source runtime khác. Giao O39-C fail closed với missing/zero runtime fingerprint và record actual discovered paths. Không gọi lượt này là đầy đủ content-pinned acceptance. Kết quả HTTP/cleanup cuối được ghi ở `Paired_Result_vi.md` sau khi process kết thúc; không nhập PASS từ log lịch sử vào lượt đang chạy.

## Qoder: công việc P0 chưa tiến ở nhánh giao chính

PR106 vẫn4cada35, chưa có code sau gói38. PR91fd04619→fc86916 chỉ thêm/sửa2report, không sửa37content errors hoặc call paths. Chạy lại `Implementation/Tools/validate_content.py` ởfc86916 vẫn37FAIL (role/weapon/targeting enums, C1schema/objectives/unlocks/token/gaps). CI6fail cũng còn. Report “all WO32 items1–6 completed” không đáp ứng work38, đặc biệt helperCreditMapEnter không là explicit MAP_VIEWEDack đã duyệt.

Giữ ưu tiên hội tụ QOD21 bằng reviewed patches, bảo toàn WIP/userimages/history; sửa finale runner oldquest read, approvedportalIDs/348→8 và20→348, replaykey; thêm wireDTO mapping defect mới. Không sửa schema theo domainDTO sai. Tiếp MAP_VIEWED/escort schema-handler-consumer có provenance, rồi inventorycapacity/consume/effective-stat theoapproval có sẵn. Domain/contracts phần sau work35 có thể làm song song. Giao actual downed/fullbag privatefixtures cho paired client, không productionseed/grantfake. Rootlocal có sửa P00-04 chưa push và P00-05 sửa dở, không lấy các file này làm source củaPR91 hoặc âm thầm nhận vào integration.

## Muse: nhận source draft mới và trả lời quyết định đang chờ

GitHubheadb1472f2 đã có thêm subtitle720, motionholdCP3b/3c và SFXcoverageCP2a, nhưng issue116 mới nhất vẫnc0caf22. Yêu cầu một handoffdelta/fullSHA cập nhật, không bắt dựng lại pack hoặc report-onlycheckpoint. Từ14b588c đếnb1472f2 runtime ClientGodot chỉ đổi9JSON timing/manifest; audio/video runtimebytes vẫn baseline. Continuityv2 ghi offscreen/placeholder có nguồn, không đồng nghĩa casting/finalpicture đã được duyệt.

Audit độc lập sau hydrate:783audio/107cinematicreferences size/hash đúng,0mismatch;21playbackentries có audio stream và decode50ms đầu PASS. Policy cuốiPASS28realOGV/0pointer,408JSON-SRT0CR,29rules khớpintegration. Ba standard720OGV và candidatefolder được fetch có giới hạn; không claim toàn bộsource masters/fsck/newclone/networkrecovery. Lượt audit đầu chạy trước LFScheckout hoàn tất nên mismatch; chỉ dùng lượt sau hydration. Policy ban đầu còn3OGV720pointer do chưa fetch; hydrate3file rồiPASS. Các lỗi setup/hydration này không phải byte defect của Muse.

Đã xem trực tiếp contact sheet P0candidate12shot: có scene/shotlabels, người/thư/bến/mặt nước/boss theo draftboard. Việc này xác nhận có reviewartifact; không đủ đánh giá motion timing, character continuity toànclip hoặc âm thanh. Candidate proceduralpose/storyboard,26holdslice và720nearest-neighbourupscale giữ DRAFT;720review không phải nguồnnative720 mới. Không có ear audition/nativeplayback/export/fullstreamdecode/loudnessremeasure trong lượt này; NOT_AUDITIONED giữ nguyên.

Muse CP2a chỉ audit/proposal, không audio mới. Đã đọc đề xuất P-GUARD/P-WEAPON/P-GRASS và Q-PHASES. Codex trả lời bằng `Implementation/Content/DesignBaselines/media_sfx_draft_execution_20261112.json`: cho sáng tác18draftvariants (guardexpiry,4weapon,grass ×3), provenance/manifest/playlist/measuredpeaks; chưa cấp runtimekey/wireevent/binding/finalaudibleapproval. Giữ1cue/skill+sharedmiss/impact theo catalog, không bịa60phasekeys. Guardexpiry không giảmetalparry/counterconfirmed. Giữ voiceoriginal, alternatecasting chỉ level-matchedreview; giữ640runtimecandidate và720MP4/3OGVsamples, fullupscaledOGV deferred. SFX độc lập không còn chờ voice/characterlock.

## Remote và tích hợp

PR98 vẫn5371a46, không ACK/source mới; chưa tracked library/test/harnessprojects. SáuCIcheck của repo không chứng minh persistence module build/test. Giữ trạng thái chờ bàn giao R1, không báo đang chạy. Khối đầu phải sourcecsproj/dependencies/cleanclone tests>0/TRX; sau đó fullwork36 transaction/outbox/fencing/crash-recovery/adapters. Không tạo DBwriter thứ hai bằng Qoderlocal.

Gói39 chốt owner cho8UNVERIFIED màOpenCode hỏi. Codex nhận subset sau sửa provenance/media boundary và typedserverwire, giữ native/graphics/UI/UX/VFX/camera. First-partylicense không tự cấp, production OFF. Review/approval/workorder chỉ được gọi đã giao sau comment thành công trên85/87/41/79/116/4; ACK/push/test/acceptance ghi riêng theo artifact.
