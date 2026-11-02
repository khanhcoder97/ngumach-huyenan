# Các gói thực thi tiếp sau review — 03/11/2026

Nguồn review: `Implementation/Reports/Agent_Review_20261103_vi.md`. Quyết định gỡ blocker: `docs/production/Ben_Mua_Alpha_Implementation_Decisions_20261103_vi.md` và JSON `Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json` (DESIGN-BM-ALPHA-20261103). Đây là thiết kế mới alpha, không giả đã có trong canonical cũ hoặc đã playtest cân bằng. Antigravity **không được phục hồi**. Nhận cả gói của mình; commit/push từng checkpoint nhưng không dừng sau ACK/plan/1fix, chờ review thì làm phần độc lập.

## 1. Qoder LOCAL — QOD-21: chuỗi Bến Mưa chơi được và trang bị12slot

**Đã nhận:** PR91 ae21088 domain/HTTP checkpoint,392self-check/151two-client/2producerprobes PASS; chưa tự merge stack hoặc mở production. Scope Server/Health, P1 contracts/schemas/runtime exporter/data mới có provenance, tests/workflow server. Persistence library vẫn Remote; client/art/compiler cũ không sửa.

**Nhánh tiếp:** `qoder/qod-21-ben-mua-playable-alpha-20261103` từ ae21088, PR stacked target `qoder/qod-18-ben-mua-completion-20261030` (91), Refs87/41 và packet này. Giữ rootWIP/userfiles, không reset/clean; dùng worktree riêng khi cần. Không tự merge91/96/main.

### Q1 — ingest profile alpha và bổ sung graph có nguồn

Đọc JSON quyết định đầy đủ, không hỏi lại4câu Q-F hoặc bag100/12slots. Tạo exporter/validator cho overlayalpha/version/provenance trong phạm vi Qoder (không tạo ContentPipeline cạnh tranh). Cho phép dữ liệu nguồn mới này với guard, không sửa349placementCSV hoặc tự gắn REVIEWED cho topology. Validate bounds/collision/LOS và record/reference trước kích hoạt. Default gates OFF, private `ben-mua-alpha-20261103` profile mới explicit, profileversion ghi tronglog.

P00-02..05 implement đủ bước JSON:3ripples+4kills;2villagers+3rootkills+trainingwave dodge; escort cùngLyAn actor ownerinstance qua80/120 và đúng3+3wavegroup; questboss→fragment→classTalk→turnin. TurnInNpcId/circular TrialNPC condition và phaseanchoroverride đã được chốt. Kill/collect/talk phải kiểm actor/quest/step/map/floor/range/instance/attempt/life/death; oldlife/death hoặc loài bất kỳ không thay wavecredit. Giữ checkpoint đã commit qua retry, không nhânLyAn trong cùnginstance. Chỉ bỏ blockedSteps khi handler/data/validation đã thực sự có; không bỏ objective để activationACTIVE.

### Q2 — boss encounter thật, không chỉ domain fixture

Dùng quest recordATLAS_BOSS, tắtworldeventboss trong questinstance. HP1200/ATK24/armor6 là hồ sơ tutorialalpha mới; phase/move/ring/safepads/interrupt/reset/credit đều trong JSON. Nối same20Hz tick/cast/guard/damage/lifecycle hiện có; telegraph→impact→recover, C→B→A, không overlap, snapshot aim, phaseguard1s và generation token bảo vệ latework. Thực hiện snapshot encounter endpoint schema1, giữ closed CombatEventV2 không thêmtype lạ. Wipe resetphase1/fullHP sau10s khôngtarget sống, no loot/unlock, lifeId mới chỉ ởattemptmới. Bossdeath credit đúngowner, fragment/trial/turnin riêng, không reward từcinema.

### Q3 — progression/economy/12slots qua contract version mới

Bag100, noautoswap, inventoryrevision, giữ currentHP/MP rồiclamp. V2 routes/schema trong JSON,12slot có1-1mappingcanonical; v1five-slot giữ compatibility qua đườngcũ, không đổi closedenum tại chỗ. Publish examples/errorcases/migration packet cho Codex/OpenCode tại85/41. Typed armor/weaponpower thắng alias trùng primary, secondary khác tính1lần. Upgrade/set/hidden chỉ áp khi có source+unlock, không hiển thị nghĩa là tự cộng.

XP acceptance snapshot25%/55% theoRules, mobXP vàthresholdsourced, transactionlevel+inventory+questrollback cùngnhau. Lootalpha band/rarityvector mới đã cấp, recipechance/group semantics giữ nguồn, snapshotroll once per death/character/group; lootquest vàquestturnin không grant cùng mục hai lần. Không hứa durable khi Remote chưa tích hợp. Newstateprofile chỉ cho newalphasession/migrationID rõ, không tựheal session cũ.

### Q4 — hành trình kết thúc tutorial và tests không né phần khó

Nối DeathReturnService/domain vào explicitreturnintent route theo JSON deathReturn mới: spawn18/0 nguồnhiệncó,50% effectiveMaxHP, noXP/currency/durabilitypenaltyalpha, no clientcoordinates, casts/counter/guardcancel, replayđúngdeath/life/key. Chỉ gateprivatealpha, publishcontractchoCodex/OpenCode để UIcóđườngthửlại; khôngđểactorDOWNEDvĩnhviễn trongdemo.

P00-05 unlock flag/portal MAP_THANH_LAC và runtimeC1-01 theoJSON min11, không bypass cấp hoặc đánh dấuChươngI đã hoàn tất. Portal kiểmunlock/target/coordinates tại commit, không cho requestdirectteleport vượtgate. Test default gatesOFF, fulltutorial privateprofile, wipe/reset/latecast, phase60/30, actualbossfight, trainingwavecredit, escortcheckpoint/waveattribution, fullbag, v2equipment12slots/revision/race/noheal, exactreward once và2client khácinstance/owner. Domain manualclock có thể tăng tốc test, phải ghi nhãn; ít nhất1HTTP flow qua server thật, không bỏboss hoặcmockcompletedquest để gọi fullcampaignPASS. Report measuredTTK/deaths/completiontime/drops, không tự nói đã cân bằng.

Tiếp cảQ1→Q4, cung cấp endpoint/event/timing mẫu ngay khi contract checkpoint xong. Một phần blocked thật thì nêuexactfield và tiếp phầnđộc lập, không dừng cảgói. Native/collision proof chưa có giữUNVERIFIED, không chặn domain/contract/HTTP test đúngscope.

## 2. OpenCode LOCAL — OPC-14 runtime release gate, không thêm wrapper thay consumer

**Baseline:** PR103 a90277f,167testsPASS/15HTTP assertions có chạy nhưng chưa chứng minh reward; report chỉ rõ callsites còn thiếu. Tiếp **cùng branch/PR103** trong `D:/Project/NGUMACHHUYENAN-opencode-player-ui-20261101`, không rootQoder/D:/opc05b-wt. Scope20/21/22 giữ, gồm minimalasmdefs/TestFramework; Corelogic/server/compiler/art không sửa. Không tự merge101/103/96/main.

### O1 — sửa đúng các file đang sử dụng UI

Checkpoint đầu bắt buộc có diff và callsite trong **PlayerUIRoot/SettingsPanel/CinemaOverlay/PlayerUIButtonBar** và **InventoryPanel/CharacterPanel hoặc presenterconsumer tương ứng**, không chỉ thêm class Presentation và test wrapper.

- Root giữ1SettingsConsumerBinder theo document/session, tạo sauSettingsPresenter, register **actual components implement IUiAccessibilityConsumer**, dispose trướcteardown. Cinema/hotkey labels/owned UI transitions/highlights phải đổi hành vi khi settings đổi; cùngnội dung reopen/reset/rebind/twodoc không leak. WorldVFX ngoài scope không giả đã có.
- Nối FocusNavigationPolicy vào actualUIElements KeyDown/focusController topmodal, xử lýfocusedchild củaTextField/Slider, Tab/ShiftTab/restorefocus khônglọtxuốngcinema/gameplay. Overflowpolicy phải có nút/menu thật và mở đủ5panel ởviewportchật, no total access loss. Không lấy bool policy unit test làm nativeproof.
- Load `Resources/PlayerUI/ui_item_catalog` thành typed catalog và inject per-session/document resolver vào bag/character; **ItemMetadataResolver embeddedsubset chỉfallback**, không là đườngchính khi resourcehợp lệ. Sharedimmutabledata được cache, viewstate khôngglobal. Test itemngoàisubset qua actualformatter/viewbinding.
- Digest phải recompute và so meaningful content/hash, không chỉ check chuỗi có tồn tại. Generator `--check` phải read-only, fail khi stale, không ghi output và xanh.136identicalsharedrows cho phép với provenance, conflictingdup fail. .meta đầy đủ.

### O2 — acceptance đúng lời tuyên bố và CI bắt buộc chạy

Dùng HTTPserver riêng từ sourcecùngprofile, không cần càiUnity. Có sẵn referenceprivate runner/NarrativeChecks; currentactual15assertions chưa đủ: firstresponse loss phải fail+pending; RetryPending success cùngbody/key vàclearPending; **quest phảiCOMPLETED**, rereadinventory so20COIN+exactly1chest trước/sau retry/repeatnewkey, không chấp nhậnREADY là complete hoặc invalid_transition thay vì receiptverify. Gọi actualNpcDialoguePresenter/QuestJournalPresenter/adapter vàassert snapshotopen không POSTNPC, pin/update khôngwire; hiện kịchbảnchỉgọiclienttrực tiếp nên noNPCPOST là điều hiển nhiên.

Bổ sung delayedread/rebind/NPCswitch, expiry/disconnect vàfullbag nếucóseedhợpđồng. RequiredCI phải dựngprivate server vàchạyHTTP, không optionalenvskip. Có strictassertioncount vàartifacts, khôngđòi externalmanualURL. Giữ producer/narrative tests cũ; dùng own harness, không sửa report/runner đểxóafinding.

### O3 — actual native graph/tests, không chỉ đổi reference string

Test vẫn `new ModalOrchestration` sai; dùng ModalOrchestrator+namespacePresentation. Roottests phải Initialize(realadapter,doc) rồi assert route/visible tree đã mở trước đếm200cycles. Sửa runtime/testassemblygraph tối thiểu đã được mởscope22: customasmdef **không được reference predefined Assembly-CSharp**. NguồnUnity6000.3 official: https://docs.unity3d.com/6000.3/Documentation/Manual/assembly-definitions-referencing.html . Khai đúngTestFramework/TestAssemblies/NUnit và .meta, khôngfakeUnity. RuntimeCorelogic không sửa; nếu assemblyboundary gặpexternaltype thì cung cấp graph/refactor tối thiểu đượcreview, không đổi engine/packagesngoàicầnthiết.

MuseVM chạy trueUnity6000.3.17f1 khi córuntime, XML/log/screenshot/head rõ. Nếu VM khôngcóUnity thì ghiNO_UNITY_RUNTIME, nativeUNVERIFIED, vẫn hoàn tất source/API/callsite/HTTP. Gửipacket thực tếissue1 saucheckpoint đãsửa, không ghi “Muse nhận” nếuchưađăng. Nativetests không được no-op hoặc repackage purepolicy làm UIproof.

### O4 — checkpoint sản phẩm và handoff

Không báo A-E COMPLETE khi còn POLICY_ONLY/GENERATED_NOT_BOUND. Report consumer→callsite→test bằng filepath/method và actualUIbefore/after. Dùng v2equipmentcontract Qoderpublish làm input/handoff request, chưa cóCoreadapter thì gửiCodex interface, không tạo transportmới. Bàn giao demo setup/failurematrix và sourcehead+exactCI; tiếp cảO1→O4, không dừng sau binderclass/ACK/1fix. Authsẵnđượcphép, khôngextract/insecret/model changes; dùng Read/Write vàscriptfile, tránhquotingloop trongCMD.

## 3. QODER REMOTE — QR1→QR6 thật, mở đầu bằng clone sạch chạy được

**Baseline:** PR98 5cfa358; source vẫnkhôngcsproj dùcommitmessage nóiđãthêm;0DBtests vàworkflowriêngFAIL. Không phátQR02 hoặc gọi xongQR01. Giữbranchremote hiệncó, PR98, Refs79/41. Không sửaHealth/client/contracts/art. Được tạo Server/Persistence, Persistence.Tests, Persistence.Harness và chỉnh **.gitignore whitelist đúng cácproject này**, workflowriêng; khôngtrải implementation raServer/Core/Atomic/Recovery nếuchưaquy hoạchmodule rõ.

### R1 — bắt buộc bằng chứng tracked files trước mọi completion claim

Kiểm `git check-ignore -v` cho *.csproj, `git ls-files --error-unmatch` và `git show HEAD:path` xác nhậnmodule/test/harness/lock/dependencies vào commit. Được add-f đúngprojecthoặcwhitelistlocalpath .gitignore, không sửa globalignore. Build từ bản `git archive`/clone sạch của exactHEAD, fileSQLite thật, tests>0 vàTRX. ThêmCI riêng restore/build/test đúng.NET10project, `needs` khôngthamchiếujobđãxóa(deploy-preview), khôngsummary tựxưngsuccess khijobtestFAIL. Cleanup biếnrỗng/wildcard phải bỏ, tempdir boundedđãresolve; khôngruntestxóaDBngườikhác.

### R2→R4 — thư viện/provider hoạt động, không placeholder

Migrations version/checksum/idempotent/futureversionreject. Mộtunitofwork gom expectedrevision+typedstatechanges+rewardledger+receiptfullpayloadhash/result+outbox trongDBtransaction; khôngcallback mutate ngoàiSQLtransaction, khôngreflection lấyprivateconnection, khôngseparatereceiptinsertlần2. Identityprincipal→characterownership thật, DBlease/fencing/rotation/grace120s, accountA khôngđọc/sửaB. Haiindependentprocesses/connection cùngkey chỉmộtgrant; replayquarerestart exactresult, differentpayload conflict.

Outboxclaim/order/retry/ackcrash vàconsumerdedupe; migrations/state/receipt/lease/schema ởfileDB. Crashharnesskill trước/saucommit vàlostresponse khônghalfwrite/doublegrant. Backup dùngSQLiteAPI hoặcquiesce/WAL đượcverify, integrity/schema/digest/count/owner/ledger/outbox so khớp, restoregiữbảngốc. Không “all” query rồichọncommitted từuncommitted, khôngSimulatebatch/integrityreturntrue. CảQR1→6vẫnphảiđủ; SQLitegiữsinglehostalpha, khônghứaMMOexactlyonceproduction.

### R5/R6 — interface và nối với Qoder sau review

Gửicontractcheckpoint/harnesscalls/errorcodescho41/87 đểQoderchuẩnbịadapter, Healthintegration vàproductionflagsOFF tớireview. Nói rõlibraryTESTED khôngđồngnghĩaHealthpersistent. Bàn giaoexactSHA/provider/version/license/commands/CI/recoveryevidence; khôngmetricướcđoán hoặc reportproduction-ready. Chờreviewphầntransactionthìtiếpoutbox/tests/restoređộc lập, khôngngừngcảepic.

## 4. Muse — MUSE-BM-PLAYABLE: asset Bến Mưa + combat + cinematic + native packet

LatestPR22 497702e vẫnmanifestdraftv0.2.0/16sheet8hướng, chưacóbàn giao mới đượcxácminh. Nhậntrọngtâmlớnđểverticalslice nhìn/chơiđược: **finish character+NPC+quái+boss+map+HUD+VFX+opening**, tiếp backlog1/29/39. Nhánhart riêng `muse/ben-mua-playable-alpha-20261103`, PR asset tớiintegration96, ghi dependencieschocherry-picksourceart22 đãreview; khôngreset/xóaWIP hoặc rebaseđèhistory. KhôngsửaCore/server/UIlogic củaOpenCode; editor artsetup/animatormetadata đượcgiữ trongscopeart nhưngruntimecontroller thayđổi phảiproposal riêng.

### M1 — actor pack và animation đọc rõ ở gameplay scale

HoànMinhKiếm16action×8hướng từmanifesthiệnhành, giữ frame48×64/PPU20/Point/no-mipmap/pivotbottom-center trừkhi cóversionedframeSize migration rõ. Reviewactualattack1sheet240×512 cho thấymộtvàiposeweaponchạm mép; kiểm từngcrop/frame vàgif8hướng, khôngcắtkiếm hoặc bleed framekhácđểnhét. Giữfootplant/pivot/scale/outlines/palette, recovery khôngteleportthân. Đủavatar/portrait vàactorLyAn/TạVânKhanh/ClassTrial,2dânđượcgiải cứu; cácNPC cóidentityrõ, khôngsamefaceđổimàu. Gửicontactsheet+previewGIF/video idle/walk/run/combo/skill/hurt/dodge/death dướiactualzoompixel.

### M2 — quái/boss và VFX khớp server timing

CáLinh/RễNước/shorestalker vàquestMãngCốt: silhouette khácnhau, idle/move/windup/impact/recover/hurt/death đủhướngtheomanifest. VFX skillsMinhKiếm3skill vàbossA/B/C/phaseguard/wave/safepad theoDESIGN-BM-ALPHA JSON (windup0.9/1.2/1s,cone120°r8,circler4,annulus3..7). Artphải chođọcđượcvùngnguyhiểm/hướng/va-chạm; particlekhôngtrùmtelegraph. Hiệuứngđẹpnhưngdamage/hitbox do server, khôngđổiFPS/timingđểauto-hit. Mỗiasset cóanchor/pivot/lifetime/loop/direction/atlas/frameSize/PPU vàpreview nền sáng/tối/transparent.

### M3 — tilemap Bến Mưa thật và HUD pixel có thể giao vào game

Dùng MapAtlas/manifest hiệncó +7overlaynode mớitrongalphaJSON; không gom cảmapthành một sânnhỏ hoặc redrawThăngLong nhỏlại. BếnMưa gồm bến/kho/thủytriều/rễ/khuescort80/120/ĐầmChuông178; có cọc/cây/đá/nước/nhà/roof layers vàcollision/occlusion/floor metadata theohợpđồng đã có. Mapchiachunk/tile/layer, khôngmộtbackgroundPNGkhổnglồ thaytilemap. BossringØ22vàsafe-pads theoJSON; artwalkability phảifeedback các điểmva-chạm, khôngtựgắn topologyREVIEWED hoặc đổitọađộcanonical.

HUDskin/iconfont/icons/túi12slot/tooltip/questtracker/menuoverflow củaOpenCode, ôskillvòngcungquanhattack vàgiữtầmnhìnworldrộng. KhôngbakeVietnamesetextvàoảnhnút, labels vẫnlocalization. Palettepixelcrisp, khôngupscale mờ hoặc lẫnvectorHD; giữlogicalrender chuẩn vàscreenshotsactualviewport. Giao atlas+metadata+9slice nếuápdụng+touchstates, khôngchỉconceptảnh.

### M4 — cinema và bằng chứng bàn giao

Tiếp opening/CIN006 storyboard đãchốt trongnarrativepacket, canonicalshotIDs/durations, rồi actualvideotake cóSRT/VO/stems/stillfallback/skip/end semantics; khônggrantquesttừvideo. Khôngphátminhplot/thoạimới hoặc revealtrướccheckpoint; gửiCodexreviewtake trướcfinalrender. Có thời tiếtmưa/fog/watersplashUI-safe theoassetbudgethiệnhành vàpreviewreducedflash.

Mỗi checkpoint commit/push actualLFSbytes +manifest/meta/previewsourceoriginal, assetvalidator/PNG/meta checks trênbaseline currentpipeline; checkallfilestracked/hydrated, khônggọiLFS pointer làảnh. NativeUnityVM cóthìchạy packetOpenCode đúngHEADsaucodefix, XML/log/screenshotsvideo; khôngcóUnity phảiACKNO_UNITY_RUNTIME vàtiếpassets/cinema, khôngreportPASS hoặc làm giảlog. Ownershipnativeimplementationtests làOpenCode, Musechạy/capture khiVMđủcôngcụ. Khôngchỉnhcodeđểbỏqua type/importerrors. KhôngdừngsauACK/onePNG; nhậncảM1→M4, bàn giao theo assetpack lớncópreviewchạyđược.

## Điều phối và nghiệm thu chung

ACKissue đúngowner vớibranch/currentSHA/toolchain/milestone đangcode. Qoder87/41, Remote79, OpenCode85/80, Muse1/29/39. Bàn giaoactualfiles/commands/output/CI vàlimitations. Sourceoftruth làsource/data/verifiedevidence, không phải reporttựxưngcomplete hoặc tổngCI khôngchạypartsđượcnóiđến. Thiếu mộtcapability thì nêu lỗi cụthể vàtiếp phầnđộc lập đãgiao; khôngbáoall-done vìtaskđãđónggói. Codexreview/merge, productiongatesOFF, Antigravityvẫnthu hồi.
