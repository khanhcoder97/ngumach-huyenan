# Bến Mưa: unresolved trong candidate compiler, 2026-10-31

Báo cáo sinh từ `Implementation/Content/BuildCandidates/BEN_MUA/candidates.json`, không là quyết định thiết kế mới. 21candidates:4ready-for-review/17blocked/56unresolved. Ready-for-review vẫn cần review và `runtimeActivationAllowed=false`.

56 dòng là **field-level findings**, có thể cùng một nguyên nhân. Không được hiểu là56 hệ thống chưa tồn tại. Một số là mâu thuẫn nguồn; một số thiếu quyết định số liệu/contract; equipped-profile là công việc adapter vì item stats đã có. Qoder cần đối chiếu runtime hiện hành và canonical definitions trước khi xử lý, không tạo nguồn ID cạnh tranh hoặc điền giá trị0.

P00-03 đã tìm thấy footwear của cả5class trong catalog. P00-05 class-weapon reference đã có5mapping T1/common theo class; consumer còn cần binding nhân vật và quest reward XP. Không chọn class sẵn hoặc thay source ngầm.

| Candidate | JSON path | Trạng thái dữ liệu | Lý do | Nguồn đối chiếu |
|---|---|---|---|---|
| QUEST-P00-02 | /rewards | MISSING | Quest text says XP and a potion but gives no exact XP token/amount and no exact potion item ID. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-02 |
| QUEST-P00-02 | /unlocks | MISSING | Quest text says minimap/targeting unlock but gives no canonical unlock IDs. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-02 |
| QUEST-P00-03 | /objectives/0/type | PRESENT_UNRESOLVED | Quest says destroy three Rễ Nước; the Map Atlas places interactive roots, so KILL versus INTERACT remains unresolved. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-03 |
| QUEST-P00-03 | /objectives/2 | MISSING | The dodge-one-wave step has no canonical QuestDefinition objective type or target ID. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-03 |
| QUEST-P00-03 | /rewards | MISSING | T1 footwear exists in the catalog; the quest still needs class/rarity policy, potion choice and an exact XP rule or amount. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-03 |
| QUEST-P00-04 | /rewards/itemIds | MISSING | Quest text says a potion but gives no exact potion item ID. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-04 |
| QUEST-P00-04 | /rewards/xpRule | MISSING | Quest text says XP but gives no exact XP token/amount for P00-04. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-04 |
| QUEST-P00-05 | /objectives/3 | MISSING | Entering the boss ring has no canonical QuestDefinition objective type or target ID. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-05 |
| QUEST-P00-05 | /rewards | MISSING | Reward token EQ-[CLASS]-WEAPON-T1-R-COMMON needs a class substitution; no XP amount/token is specified. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-05 |
| QUEST-P00-05 | /unlocks | MISSING | Quest text says Thanh Lạc / Chapter I but gives no canonical unlock IDs. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-05 |
| OBJMAP-P00-02 | /mappings/0/rangeWu | MISSING | Map Atlas gives ripple positions but no interaction radius. | docs/production/Map_Production_Atlas_vi.md#Map-01-Ben-Mua |
| OBJMAP-P00-02 | /mappings/0/sharePolicy | MISSING | Rules require a share policy per objective but only P00-01 collect is specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-02 | /mappings/1/sharePolicy | MISSING | Rules require a share policy per objective but P00-02 kill sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-02 | /mappings/2/sharePolicy | MISSING | Rules require a share policy per objective but P00-02 talk sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-03 | /mappings/0/eventType | PRESENT_UNRESOLVED | Map Atlas calls the roots interactive while the quest says destroy them; KILL versus INTERACT is unresolved. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-03 | /mappings/0/rangeWu | MISSING | Map Atlas gives root positions but no interaction radius. | docs/production/Map_Production_Atlas_vi.md#Map-01-Ben-Mua |
| OBJMAP-P00-03 | /mappings/0/sharePolicy | MISSING | Rules require a share policy per objective but P00-03 root sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-03 | /mappings/0/sourceIds | MISSING | Map Atlas places three interactive roots but gives no objective source IDs. | docs/production/Map_Production_Atlas_vi.md#Map-01-Ben-Mua |
| OBJMAP-P00-03 | /mappings/1/availability | PRESENT_UNRESOLVED | The manifest labels the rescue NPCs P00-04 while the quest assigns the rescue to P00-03. | docs/production/World_Spawn_Gathering_Manifest_vi.csv#MAN-BM-NPC_BM_RESCUE_01 |
| OBJMAP-P00-03 | /mappings/1/sharePolicy | MISSING | Rules require a share policy per objective but P00-03 rescue sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-03 | /mappings/2 | MISSING | The dodge-one-wave step has no canonical event type or target record. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-03 |
| OBJMAP-P00-04 | /mappings/0/sharePolicy | MISSING | Rules require a share policy per objective but P00-04 escort sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-04 | /mappings/1/sharePolicy | MISSING | Rules require a share policy per objective but P00-04 wave sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-05 | /mappings/0/sharePolicy | MISSING | Rules require a share policy per objective but P00-05 boss sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-05 | /mappings/1/rangeWu | MISSING | Map Atlas places the seal at x=178 but gives no interaction radius. | docs/production/Map_Production_Atlas_vi.md#Map-01-Ben-Mua |
| OBJMAP-P00-05 | /mappings/1/sharePolicy | MISSING | Rules require a share policy per objective but P00-05 seal sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-05 | /mappings/2/availability | PRESENT_UNRESOLVED | The manifest says NPC_CLASS_TRIAL appears only after P00-05, but P00-05 itself requires confirming the class at that NPC. | docs/production/World_Spawn_Gathering_Manifest_vi.csv#MAN-BM-NPC_CLASS_TRIAL |
| OBJMAP-P00-05 | /mappings/2/sharePolicy | MISSING | Rules require a share policy per objective but P00-05 class-confirm sharing is not specified. | docs/production/Production_Rules_Complete_v1_vi.md#5 |
| OBJMAP-P00-05 | /mappings/3 | MISSING | Entering the boss ring has no canonical event type or source record. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-05 |
| ACTOR-BASE-L1-NO-GEAR | /classCoverage | MISSING | Only CLASS_MINH_KIEM has canonical ClassDefinition and SkillDefinition examples; the other four classes are not compiled. | docs/production/Production_Content_Audit_20261030_vi.md#GAP-01 |
| ACTOR-BASE-L1-NO-GEAR | /equippedProfile | MISSING | Canonical item catalogs contain gear vectors; an equipped profile still needs a reviewed loadout/instance adapter applying DEC-023 aliases without double counting. | docs/production/Runtime_State_and_Catalog_Precision_vi.md#3 |
| MOB-MOB_CARPLING | /attacks/0/telegraphSeconds | MISSING | Art Bible gives no exact basic-bite telegraph; only the general melee minimum. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_CARPLING | /attacks/1/rangeMeters | MISSING | Art Bible gives the leap multiplier and telegraph but no range. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_CARPLING | /attacks/1/telegraphSeconds | PRESENT_UNRESOLVED | Art Bible gives 0.45s for the leap while the general heavy-attack minimum is 0.7s; the conflict is unresolved. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_CARPLING | /quantizationPolicy | MISSING | P1 leaves runtime HP/attack/defense integer quantization undecided. | docs/production/P1_Design_Resolution_20261029_vi.md#2 |
| MOB-MOB_CARPLING | /spawnLevel | MISSING | The manifest gives a level band 1-10, not a chosen spawn level; P1 level 5 is a reference profile only. | docs/production/World_Spawn_Gathering_Manifest_vi.csv#MAN-BM-SPAWN_BM_01 |
| MOB-MOB_SHORE_STALKER | /attacks/0/rangeMeters | MISSING | Art Bible gives the pounce multiplier but no range. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_SHORE_STALKER | /attacks/0/telegraphSeconds | MISSING | Art Bible gives no exact pounce telegraph; only the general melee minimum. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_SHORE_STALKER | /attacks/1/rangeMeters | MISSING | Art Bible gives the charge multiplier and telegraph but no range. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_SHORE_STALKER | /attacks/1/telegraphSeconds | PRESENT_UNRESOLVED | Art Bible gives 0.6s for the charge while the general heavy-attack minimum is 0.7s; the conflict is unresolved. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_SHORE_STALKER | /eliteVariant | MISSING | Spawn group SPAWN_BM_07 also contains MOB_SHORE_STALKER_ELITE; its elite override stats are not part of this base profile. | docs/production/World_Spawn_Gathering_Manifest_vi.csv#MAN-BM-SPAWN_BM_07 |
| MOB-MOB_SHORE_STALKER | /quantizationPolicy | MISSING | P1 leaves runtime HP/attack/defense integer quantization undecided. | docs/production/P1_Design_Resolution_20261029_vi.md#2 |
| MOB-MOB_SHORE_STALKER | /spawnLevel | MISSING | The manifest gives a level band 1-10, not a chosen spawn level; P1 level 5 is a reference profile only. | docs/production/World_Spawn_Gathering_Manifest_vi.csv#MAN-BM-SPAWN_BM_06 |
| MOB-MOB_WATERROOT | /attacks/0/telegraphSeconds | MISSING | Art Bible gives no exact basic root-whip telegraph; only the general melee minimum. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| MOB-MOB_WATERROOT | /quantizationPolicy | MISSING | P1 leaves runtime HP/attack/defense integer quantization undecided. | docs/production/P1_Design_Resolution_20261029_vi.md#2 |
| MOB-MOB_WATERROOT | /spawnLevel | MISSING | The manifest gives a level band 1-10, not a chosen spawn level; P1 level 5 is a reference profile only. | docs/production/World_Spawn_Gathering_Manifest_vi.csv#MAN-BM-SPAWN_BM_03 |
| BOSS-BOSS_MANG_COT | /attackDescriptors | MISSING | Phase guard, interruptible, damage type and exact hit window are not specified per boss attack. | docs/production/Production_Rules_Complete_v1_vi.md#4 |
| BOSS-BOSS_MANG_COT | /baseAttack | MISSING | Art Bible gives the boss attack multiplier but no resolved base attack. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| BOSS-BOSS_MANG_COT | /defense | MISSING | Art Bible gives no boss defense profile. | docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md#12 |
| BOSS-BOSS_MANG_COT | /encounterLevel | MISSING | P1 level 10 is an illustrative calculation, not a chosen encounter level. | docs/production/P1_Design_Resolution_20261029_vi.md#2 |
| BOSS-BOSS_MANG_COT | /partyScalingRounding | MISSING | P1 does not choose rounding for party-scaled HP. | docs/production/P1_Design_Resolution_20261029_vi.md#2 |
| BOSS-BOSS_MANG_COT | /phases/1/safePadPositions | MISSING | Rules require two safe pads outside the bubble ring but give no positions or geometry. | docs/production/Production_Rules_Complete_v1_vi.md#4 |
| ITEM-REF-P00-02-POTION | /resolvedItemId | MISSING | The generic token 'thuốc' matches both POT-HP-01 and POT-MP-01; the quest does not choose one. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-02 |
| ITEM-REF-P00-03-POTION | /resolvedItemId | MISSING | The generic token 'thuốc' matches both POT-HP-01 and POT-MP-01; the quest does not choose one. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-03 |
| ITEM-REF-P00-03-SHOES | /resolvedItemId | MISSING | T1 footwear exists for all five classes; the generic shoes reward still needs an explicit class/rarity resolution policy. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-03 |
| ITEM-REF-P00-04-POTION | /resolvedItemId | MISSING | The generic token 'thuốc' matches both POT-HP-01 and POT-MP-01; the quest does not choose one. | docs/production/Quest_and_Narrative_Production_Spec_vi.md#P00-04 |

Sau khi chốt canonical source: review transcription/lock → build → validate/check → diff bundle → consumer migration/tests. Không xóa unresolved trực tiếp trong generated JSON.
