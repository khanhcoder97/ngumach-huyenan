# Luật triển khai bổ sung v1 — Ngũ Mạch: Huyền Ấn

Ngày 2026-10-28. Gói này bổ sung chỗ trống theo audit, áp dụng top-down DEC-016. Đây là thiết kế baseline có thể triển khai và chỉnh qua bundle version; chưa là kết quả cân bằng/playtest. Giá trị số đã tồn tại trong bảng item, skill, activity và passive vẫn lấy từ bảng chuyên ngành; các quyết định xử lý mâu thuẫn ở cuối tài liệu được ưu tiên hơn văn bản cũ.

## 1. Cấp độ, chỉ số và phân bổ

Data cấu hình mới tại `Implementation/Content/DesignBaselines/completion_v1.json`; chưa bật tự động trong server P1. Bảng cấp 1–100 tại `level_progression_v1.json` là đầu vào exporter, không thay file state nhân vật đã lưu.

- Mỗi class khởi đầu STR/INT/AGI/VIT/LUK=5; mỗi lần lên cấp +5 điểm tự phân bổ. Budget đến cấp L là 5×(L−1); tổng giá trị đã cộng không vượt budget. Không auto cộng thêm stat khi tăng cấp. Default build chia điểm theo trọng số nguyên trong config bằng largest remainder, tie-break STR→INT→AGI→VIT→LUK.
- HP nền=100, MP nền=50; HP=100+28L+14VIT+gearHP; MP=50+12L+8INT+gearMP. Các HP100/MP50 trong phiên demo hiện tại là fixture, migration sang profile mới phải refill đầy một lần và ghi migrationId.
- PhysicalAttack=weaponPhysical+3STR+AGI+flatGearAttack; MagicAttack=weaponMagic+3INT+LUK+flatGearAttack. Weapon damage type theo template; không cộng cả hai attack vào cùng hit.
- Armor=gearArmor+2VIT. Accuracy bonus=0,0005×AGI+gearAccuracy; dodge=min(cap,0,0003×AGI+gearDodge); crit=min(cap,0,05+0,0005×LUK+gearCrit); cap PvE50%, PvP25%; crit resist=gearCritResist. Các tỷ lệ là số thập phân (0,01=1%).
- EXP để L→L+1: ceil(100+50L+25L²), L=1..99. Cấp 100 không cộng thêm điểm/EXP; không tạo currency thay EXP. Quest thường=25%, boss chương=55%, quest phụ=12% XP-to-next ở cấp nhận quest, floor số nguyên; snapshot reward XP khi accept. Reward đã có số tuyệt đối giữ số đó.
- Quái cùng cấp cho floor(10+2×mobLevel) EXP; chênh cấp người chơi trên quái >10 thì ×0,25, >20 thì ×0,1; quest/first-clear không giảm. Mob XP elite ×3, quest boss ×10; world/raid dùng bảng reward activity, không cộng thêm boss XP generic.
- Lên nhiều cấp trong cùng transaction xử lý lần lượt từng ngưỡng. Không mất EXP khi chết. Reset điểm miễn phí trước cấp 20; từ cấp 20 phí 100×L Đồng, chỉ hub ngoài combat, không đang queue/trade; refund toàn điểm đã phân bổ, không đổi base stats.
- Skill rank 1–5, mở tại level skillUnlock+[0,10,20,30,40]. Phí rank r>1 là 100×r² Đồng; mỗi skill chọn nhánh DAMAGE hoặc COST: DAMAGE tăng 2%×(r−1), COST giảm 1%×(r−1). Không đồng thời hưởng cả hai; đổi nhánh cùng luật respec, phí 100×L Đồng. Không tăng range/hitbox theo rank.
- Chọn class tại tạo nhân vật; cảnh P00-05 xác nhận môn phái đã chọn, không đổi class tự do. Hai preset chỉ đổi skill/passive/gear loadout, không đổi class.

## 2. Thứ tự tính chiến đấu

Simulation 20Hz, tick=50ms; cooldown/duration nội bộ integer ticks, làm tròn thời lượng lên tick. Aim/input hữu hạn, normalize diagonal; tọa độ không lấy từ sprite frame. Lệnh dùng chung sequence actor cho move/combat; kinh tế dùng revision/idempotency riêng.

1. Check session/owner, alive/state, class/loadout/rank, target/floor/team/range/LOS, MP/resource và cooldown. Rejected không trừ cost/tăng revision/tiêu sequence. Accepted ghi cost, cooldown, castId, tick và bộ thông số snapshot của cast.
2. Hit thời điểm server; target sống/cùng tầng/LOS/invulnerability được kiểm lại. Target ra khỏi vùng thì miss, không refund MP/CD. Aim khóa từ cast start trừ kỹ năng ghi rõ tracking.
3. Hit probability=clamp(0,90+accuracy−dodge,0,05,0,98). Crit probability=clamp(crit−critResist,0,critCap). Roll RNG server theo castId/targetId/hitIndex; lưu seed version phục vụ audit.
4. Raw=(attack+flatSkill)×skillCoefficient×rankMultiplier×(1+sumDamageBonus). PvP dùng coefficient PvP thay PvE; boss dùng boss coefficient thay PvE, không nhân hai lần.
5. Mitigation=100/(100+max(0,armor)); armor normalization v1 là chính armor đã tổng hợp, không có hệ số cấp ẩn. Element multiplier=1−clamp(resist,0,0,5) PvE, cap PvP=0,3. Crit×1,5. Damage reduction cộng trong bucket và cap 0,8; miễn nhiễm là trạng thái riêng.
6. Final=max(1,floor(raw×mitigation×element×crit×(1−reduction))) cho hit gây damage; miss/immunity=0. Shield hấp thụ trước HP, chọn expiry sớm trước; HP clamp 0..maxHP. Lưu event damage hấp thụ và HP damage riêng.
7. Death chỉ phát một lần cho entityLifeId; loot/quest event tham chiếu deathEventId. Heal không crit, không vượt maxHP, không tạo threat từ overheal. Lifesteal tính HP damage thực sau shield, không từ số damage hiển thị.

Các modifier phần trăm cùng bucket cộng; bucket attack/skill/damage/resist/DR nhân theo thứ tự trên. Làm tròn một lần cuối, item upgrade dùng round_half_up theo spec item. Multi-hit dùng coefficient từng hit đã có; không áp tổng 190% ba lần cho Kiếm Trận.

Đánh thường 3 nhát mỗi nhát 100% attack, windup 0,15s, hit 0,10s, recovery 0,25s; combo timeout 1,5s sau recovery. Cận chiến range 4 WU, quạt 90°, tối đa 1 target; Huyền Bút/Linh Cung đạn range 10/14 WU, tốc độ 20 WU/s, tối đa 1 target. Tốc đánh chỉ giảm recovery, minimum 0,15s. Đây là dữ liệu bổ sung basic attack, không thay active skills.

Né chung: CD7s, distance11 WU, startup0,08s/avoid0,18s/recovery0,20s theo Combat Spec; thời lượng tránh được ceil theo tick. Quãng đường bị cắt bởi terrain sweep, không xuyên tường. Dodge không gây damage; bypass chỉ các đòn ghi UNDODGEABLE. Kiếm Trận bổ sung range 4,4 WU; Tầm Long range11 WU; Phản Quang vùng phía trước4,4 WU. Giữ proposal migration Qoder riêng trước khi runtime dùng.

## 3. Status registry

Mỗi application gồm statusId/sourceId/castId/startTick/endTick/stacks/strength/category/cleanseTags. Tính theo simulation time; reconnect không kéo dài buff. Buff consumable hết hạn theo UTC kể cả offline, không đồng thời chạy hai đồng hồ.

| Status | Stack/refresh | Boss/PvP | Cleanse |
|---|---|---|---|
| slow | mạnh nhất, lấy expiry của application mạnh nhất; cap50% | boss miễn chậm, PvP cap30% | slow |
| poison/bleed/burn | cùng source refresh, khác source tối đa3; tick1s | coefficient skill/mode, không crit | poison/burn; bleed chỉ cleanse chuyên dụng |
| stun/root | không cộng duration; thay khi expiry mới dài hơn | boss chuyển stagger; PvP 50% duration | hard-control chuyên dụng |
| shield | cùng skill giữ lớn nhất; source khác được tồn tại, tổng cap30% maxHP | PvP cap20% | không dispel mặc định |
| mark | cùng skill không cộng strength, giữ expiry dài nhất | dùng strongest group bonus | dispel nếu skill khai báo |
| guard | cửa theo skill; thành công một lần/cửa | phản công kiểm hướng, không tự damage bản thân | tự hết |

PvP hard-control diminishing theo target: lần1 100%, lần2 50%, lần3 25%, lần4 miễn; reset sau15s không nhận hard-control. Boss stagger bar100, stun/root hợp lệ cộng10, ICD1s/source; đầy thì stagger2s, reset0, miễn tích5s. Không ngắt cast UNDODGEABLE/phase transition. Resource lớp cap5; chết/đổi map về0, đổi target chỉ reset Mộc Tiêu như Combat Spec.

## 4. AI, vòng đời và boss

AI states: SPAWN→IDLE/PATROL→CHASE→TELEGRAPH→ATTACK→RECOVER; hết leash sang RETURN, HP0 sang DEAD→RESPAWN. Patrol waypoint chọn bằng seed spawnGroup, không chọn ngoài nav. Chạy A* trên nav XY; repath tối đa2Hz khi target đổi ô/vật cản đổi. Không có đường trong3s thì RETURN; không teleport quái vào người chơi.

Leash mặc định20m=40WU hoặc radius arena nếu boss; rời leash3s thì RETURN, miễn damage, fullHP khi đến spawn. Ordinary mất target10s thì RETURN. Respawn bắt đầu sau clear nhóm nếu manifest ghi clear; không hồi từng con trái policy. Spawn mới có entityLifeId mới, quái DEAD không được target. NPC không combat invulnerable, không đưa HP0 của NPC vào pipeline death.

Threat=HPDamage+0,5×effectiveHeal+0,3×shieldAbsorb; healing threat chia đều quái đang combat party, không kéo quái ngoài aggro. Switch melee khi threat mới>110% target hiện, ranged>130%; tie-break entityId. Taunt ordinary giữ4s; boss không cưỡng ép đổi target. Party size scale boss snapshot khi encounter ACTIVE, không giảm HP nếu người rời để exploit.

Mãng Cốt P1 có ba đòn: (A) quét thân cone120°, range8WU, báo0,9s, hit1,2ATK, recovery0,8s, CD4s; (B) lặn/trồi circle radius4WU tại vị trí target đã chốt, báo1,2s, hit1,5ATK, recovery1s, CD9s; (C) vòng bọt annulus radius3..7WU tại boss, báo1s, hit1,3ATK, recovery1s, CD12s. Chọn đòn sẵn sàng C→B→A; không overlap telegraph. Pha2 ở60% HP giảm recovery20%, pha3 ở30% HP tạo hai bệ an toàn có icon ở ngoài vòng bọt; không tăng damage vô hạn. Arena mất toàn target sống10s thì reset attempt/HP, quest checkpoint giữ. Boss không tự chết do timer.

Boss khác giữ phase/đòn từ Activities và Art Bible; dữ liệu numeric phải khai đủ windup/shape/distance/hit/recovery/CD/phaseGuard/interruptible. Trường thiếu làm export fail, không dùng hồ sơ Mãng Cốt thay cho boss khác. World boss lifetime12 phút theo manifest, rút lui không phát death loot.

## 5. Quest graph và hội thoại

Graph phải có OFFER→ACCEPTED→STEP_1..n→READY→TURN_IN→COMPLETED, edge có guard/result. Các loại step TALK/INTERACT/KILL/COLLECT/ESCORT/DEFEND/BOSS_PHASE/INSTANCE_CLEAR giữ spec cũ. Mỗi objective ghi ID, count, source entity/interaction, map/floor, range, sharePolicy, checkpoint và timeout; choice edge ghi flagId/value và nextStepId. Reject cycle trừ repeatable graph có resetBucket riêng.

P00-01: accept Ly An→collect đúng ba package ID (mỗi ID tính tối đa1/character)→turn-in Tạ Vân Khanh. Check distance5WU, world state của package, quest ACTIVE. COLLECT event unique(actor,quest,objective,packageId), không trừ item world cho người khác. XP snapshot theo mục1, 20COIN và áo từ QuestDefinition. READY không tự nhận thưởng từ xa. Đủ túi mới commit, giữ READY nếu đầy. Nói skip không bỏ objective.

Tất cả 76 quest giữ chi tiết narrative trong Quest Production Spec; exporter cần map các câu thành graph records qua review, không dùng regex đếm thoại làm bằng chứng hoàn thiện quest. Đối với token NPC_MASTER_[CLASS], compiler resolve trước runtime và kiểm đủ5 lớp. Thoại đã xem lưu dialogueNodeId, lựa chọn lưu flags; reconnect trả về bước committed gần nhất. Hộ tống có checkpoint actor/waypoint/waveCleared, không tạo bản sao Ly An.

## 6. Gear, nguồn ngẫu nhiên và khóa vật phẩm

Template/variant: variant cụ thể thắng rarity generic; base template không có variant chỉ được instantiate khi rarity khai rõ. Affix roll không trùng effectId trên cùng item, uniform trong pool hợp lệ nếu không khai weights; integer roll inclusive min/max, percent roll bước0,1%. Seed/roll result lưu ở instance, không roll lại khi equip/reconnect.

Một set có 2/4 mảnh bonus độc lập; có thể đồng thời 2+4 của cùng set. Nếu nhiều set đủ điều kiện, chỉ set có nhiều mảnh nhất active; hòa chọn tier cao rồi setId lexical. Hidden cùng effectId chọn strength cao nhất; ICD theo actor+effectId không reset do đổi món. Upgrade không nhân hidden/set. Full inventory không tự phá đồ; action trả inventory_full và rollback.

Forge pity v1: không thêm pity nếu recipe/upgrade table không định nghĩa; UI ghi đúng tỷ lệ per-attempt. Batch là chuỗi transaction đơn, mỗi success/fail commit riêng; cancel ngăn attempt kế tiếp, không hoàn attempt đã roll. Mat bảo hộ trừ cả khi success/fail nếu attempt đã accepted. Preview hết hiệu lực khi inventory revision hoặc bundle đổi.

Vé boss reserve khi ready-check, commit tiêu tại ACTIVE; instance lỗi trước ACTIVE hoàn reserve, lỗi do server sau ACTIVE cấp compensationId một lần. Quit/wipe sau ACTIVE không refund. Loại vé, cap và quota loot vẫn theo Appearance/Activity spec; vé không bỏ qua loot cap. Cosmetic không cộng chỉ số, kể cả item mô tả mẫu cũ có +luck/HP.

## 7. Hoạt động xã hội, PvP, nghề

Invite TTL60s, ready-check30s. Party loot policy khóa khi vào instance; kick không chuyển quyền sở hữu loot đã earned. Contribution hỗ trợ dùng effective heal/shield/interrupt, không overheal tự farm. Đứng trong35m=70WU cùng tầng và đã tham gia encounter mới share progress; vào party sau death không nhận bù.

Guild permissions theo spec; sửa role kiểm lại revision và actor authority ở commit. Người không được tự approve lệnh rút HI_VALUE của mình; cần hai approver khác nhau có quyền. Giải tán không chia quỹ tùy ý: hoàn item theo deposit ledger còn trace được; quỹ còn lại chia đều active members đăng nhập trong30ngày, floor mỗi phần, phần dư không phát và ghi audit. Chỉ bồi hoàn một lần/disbandId; sản phẩm phải review policy trước mở guild thật.

Arena MMR v1: K24, expected=1/(1+10^((enemyRating−teamRating)/400)); delta=round_half_up(24×(score−expected)), score1/0,5/0; teamRating là mean rating roster lock. Start1000, floor0, season8tuần; reset1000+floor((old−1000)×0,5). BG10/siege không dùng arena MMR. Các tie/void ở activity spec thắng công thức rating; void không đổi rating.

Farm chốt5 luống theo DEC-013; cap12 output/account/ngày. Fishing cap20 catches/account/ngày, không reset theo nhân vật. Timers UTC; node interrupt damage cancel trước grant, tool không bị tiêu nếu chưa success. Mount không combat và +10% từ spec, dismount ngay khi vào combat/instance/PvP. Pet collision off, một active pet, gear slots không phải4 pet cùng triệu hồi.

## 8. UI, localization, âm thanh và input states

Mỗi screen có routeId, open/close guard, focusOwner, data source/revision, LOADING/EMPTY/READY/ERROR/STALE/SUBMITTING. SUBMITTING chặn double click, client retry giữ idempotency key. Offline chặn mutation, giữ nội dung đang đọc kèm stale badge; world vẫn chạy khi mở modal. Esc đóng tầng trên, trả focus nút mở; không tự cancel purchase đã commit.

Text catalogue locale vi-VN gồm key/context/variables/maxLines/fallback; biến ICU có type, không nối chuỗi hardcoded. Đủ ă â đ ê ô ơ ư và dấu kết hợp; normalize NFC. Bitmap font không hiển thị được ký tự thì fallback glyph rõ, không dấu trống. Text overflow ưu tiên wrap rồi scroll, không scale fractional font. Item links dùng ID đã sanitize, không HTML từ chat.

Audio buses Master/Music/Ambience/SFX/UI, gain0..1; muted state không xóa setting gain. Footstep tối đa8 voices, hit16, skill12, UI4, ambience4, music2; priority bossWarning100, skill70, hit60, footstep20. Voice stealing thấp nhất/cũ nhất. Boss cue luôn có visual. Event gồm cueId, source/license, clip, loop, bus, gain, priority, maxInstances, min/maxDistanceWU. Không có clip hợp lệ thì silent placeholder được ghi thiếu asset, không tự tải âm thanh không rõ quyền.

## 9. Gate hoàn tất

Bảng luật này và dữ liệu đi kèm cho phép tiếp tục implementation có quy tắc rõ. Mọi quest/boss/map/asset phải có record thực, import/check và gameplay evidence trước khi gọi là hoàn chỉnh. Đặc tả map XY cần polygon/placement review thực tế; không thể sinh nav chính xác từ mô tả chữ rồi coi đã nghiệm thu. Checklist release trong tài liệu vận hành bổ sung là bắt buộc.
