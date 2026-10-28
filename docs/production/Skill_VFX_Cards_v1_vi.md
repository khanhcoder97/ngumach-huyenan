# Thẻ thiết kế30kỹ năng — VFX art v1
Dữ liệu chuẩn cùng nội dung: Implementation/Content/DesignBaselines/skill_vfx_art_v1.json. Đây là handoff art, không thay loader SkillDefinition. Source mechanics giữ nguyên văn để truy vết; số mới trong các decision có ưu tiên khi runtime migration.

## SK-MK-01 — Phản Quang
- HUD slot1 · CLASS_MINH_KIEM · ACTIVE
- Chuẩn bị: Hai góc lục giác bạc trước mũi kiếm
- Tác động: Phản kích một cung vàng trắng CHỈ khi đỡ thành công
- Tan biến: Hai mảnh kim loại ngắn tắt
- Attach: CASTER_FRONT; shape COUNTER_CONE; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: COUNTER_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/metal_parry.
- Icon: kiếm trước khiên. LowFX: giữ viền guard và một cung, bỏ spark.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-MK-02 — Tầm Long
- HUD slot2 · CLASS_MINH_KIEM · ACTIVE
- Chuẩn bị: Mũi thoi tại đầu kiếm chỉ hướng lao
- Tác động: Vệt đâm thẳng mảnh theo đường server, actor luôn thấy
- Tan biến: Bụi nhỏ điểm dừng
- Attach: CASTER_TRAIL; shape DASH_LINE; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: DASH_PATH_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/metal_thrust.
- Icon: mũi kiếm và mũi tên. LowFX: giữ đầu vệt/điểm dừng, bỏ fragment giữa.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-MK-03 — Kiếm Trận
- HUD slot3 · CLASS_MINH_KIEM · ACTIVE
- Chuẩn bị: Một cung kiếm ngắn đầu nhịp
- Tác động: Ba cung lệch45/55/90 theo hit timeline, cung ba dày nhất
- Tan biến: Từng cung vỡ ngắn, không nổ
- Attach: CASTER_FRONT; shape TRIPLE_FAN; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: MULTI_HIT_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/metal_three_cuts.
- Icon: ba cung kiếm. LowFX: giữ đủ ba nhịp, giảm mảnh phụ.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-MK-04 — Thiết Y
- HUD slot4 · CLASS_MINH_KIEM · ACTIVE
- Chuẩn bị: Ba góc lục giác dựng viền nhỏ
- Tác động: Viền khiên cạnh vai/HP, không khối kín che thân
- Tan biến: Nứt khi hấp thụ rồi tan khi hết buff
- Attach: CASTER_BODY; shape SHIELD_RIM; module tối đa96px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: SHIELD_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/metal_shield.
- Icon: lục giác có tấm chắn. LowFX: chỉ viền và status, bỏ orbiting pieces.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-MK-05 — Bạch Hồng (cơ động)
- HUD slot5 · CLASS_MINH_KIEM · MOBILITY
- Chuẩn bị: Một nét trắng xanh sau gót
- Tác động: Trail lướt mảnh theo vector server, KHÔNG hit spark
- Tan biến: Hai vạch gió tắt
- Attach: CASTER_TRAIL; shape MOVE_ONLY; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: DASH_PATH_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/air_step.
- Icon: hai vệt gió. LowFX: giữ điểm đầu/cuối, không nổ.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-MK-06 — Vạn Tượng Quy Nhất (tuyệt kỹ)
- HUD slot6 · CLASS_MINH_KIEM · ULTIMATE
- Chuẩn bị: Năm vạch Kiếm Ý hội về đầu kiếm
- Tác động: Một đường kiếm vàng trắng dài, không laser phủ màn
- Tan biến: Sáu đoạn thẳng vỡ rồi tắt
- Attach: CASTER_FRONT; shape ULTIMATE_LINE; module tối đa512px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: ULTIMATE_RELEASE_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/metal_resonance.
- Icon: năm vạch hội vào kiếm. LowFX: giữ line outline và số tầng, bỏ bụi dọc.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-AD-01 — Huyết Nguyệt
- HUD slot1 · CLASS_ANH_DAO · ACTIVE
- Chuẩn bị: Mép đao đỏ than hiện một nét
- Tác động: Cung chém đỏ cam đơn mục tiêu
- Tan biến: Ba vệt status tại TARGET, không máu
- Attach: CASTER_FRONT; shape CUT_AND_BLEED; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: HIT_AND_STATUS_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ember_cut.
- Icon: lưỡi liềm ba vạch. LowFX: giữ cung/status, bỏ ember rơi.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-AD-02 — Tàn Hỏa
- HUD slot2 · CLASS_ANH_DAO · ACTIVE
- Chuẩn bị: Dấu than năm khe đặt ở TARGET, không caster
- Tác động: Nổ gọn chỉ khi server xác nhận đòn kế kích dấu
- Tan biến: Hết hạn không kích thì âm thầm tắt
- Attach: TARGET_FOOT; shape DELAYED_MARK; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: MARK_TRIGGER_OR_EXPIRE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ember_pop.
- Icon: vòng than có chốt. LowFX: giữ dấu và pulse trigger, bỏ debris.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-AD-03 — Xích Ảnh
- HUD slot3 · CLASS_ANH_DAO · ACTIVE
- Chuẩn bị: Cung thấp đầu nhịp và trọng tâm chéo
- Tác động: Hai slash thuận/ngược tách nhịp, không actor clone
- Tan biến: Hai vệt đứt tắt
- Attach: CASTER_FRONT; shape TWO_CUTS; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: MULTI_HIT_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ember_double_cut.
- Icon: hai cung ngược. LowFX: giữ hai hit, không ghost.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-AD-04 — Tước Mạch
- HUD slot4 · CLASS_ANH_DAO · ACTIVE
- Chuẩn bị: Một nét đao dọc mảnh
- Tác động: Ba dấu xích tại chân target sau hit
- Tan biến: Status mờ theo expiry
- Attach: TARGET_FOOT; shape SLOW_MARK; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: HIT_AND_STATUS_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ember_chain.
- Icon: đao cắt ba vạch. LowFX: giữ dấu chậm, bỏ sparks.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-AD-05 — Ảnh Bộ (cơ động)
- HUD slot5 · CLASS_ANH_DAO · MOBILITY
- Chuẩn bị: Khói than thấp ở gót
- Tác động: Viền cam mỏng giữ silhouette, KHÔNG impact
- Tan biến: Khói rách hai đoạn tắt
- Attach: CASTER_TRAIL; shape MOVE_ONLY; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: DASH_PATH_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ember_step.
- Icon: bước chân khói. LowFX: chỉ đường viền/đầu cuối.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-AD-06 — Tử Diệm (tuyệt kỹ)
- HUD slot6 · CLASS_ANH_DAO · ULTIMATE
- Chuẩn bị: Than hội vào sống đao, số tầng lấy resource
- Tác động: Một quét vòng thấp đỏ cam, giữa trống
- Tan biến: Tối đa năm cánh than theo Nhiệt đã tiêu
- Attach: CASTER_FOOT; shape EMBER_SWEEP; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: ULTIMATE_RELEASE_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ember_low_burst.
- Icon: vòng đao năm khe. LowFX: giữ cung ngoài, số tầng bằng HUD.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-HB-01 — Mực Triều
- HUD slot1 · CLASS_HUYEN_BUT · ACTIVE
- Chuẩn bị: Nét bút ngang xanh mực
- Tác động: Sóng mực dẹt có rìa giấy, không cầu sáng
- Tan biến: Ba giọt mực tách
- Attach: PROJECTILE; shape INK_WAVE; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: PROJECTILE_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ink_wave.
- Icon: nét bút và sóng. LowFX: giữ đầu sóng, bỏ splash phụ.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-HB-02 — Hàn Châm
- HUD slot2 · CLASS_HUYEN_BUT · ACTIVE
- Chuẩn bị: Ba chấm cyan ở đầu bút
- Tác động: Kim băng mảnh, cánh băng tại chân target
- Tan biến: Cánh băng gãy nhỏ
- Attach: PROJECTILE_AND_TARGET; shape ICE_NEEDLE; module tối đa96px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: PROJECTILE_HIT_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/ice_tick.
- Icon: kim băng ba chấm. LowFX: giữ needle/status, bỏ vỡ vụn.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-HB-03 — Thủy Kính
- HUD slot3 · CLASS_HUYEN_BUT · ACTIVE
- Chuẩn bị: Vòng nước khép quanh chân ĐỒNG MINH
- Tác động: Hai mép kính mỏng, mặt và thân mở
- Tan biến: Vòng tách hai giọt khi shield hết
- Attach: ALLY_BODY; shape ALLY_SHIELD; module tối đa96px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: SHIELD_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/water_glass.
- Icon: kính nước bao khiên. LowFX: giữ mép kính và status.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-HB-04 — Mưa Tinh
- HUD slot4 · CLASS_HUYEN_BUT · ACTIVE
- Chuẩn bị: Vòng đứt cyan báo vùng trên đất
- Tác động: Mưa thưa trong vùng, tick heal chỉ từ server
- Tan biến: Ngừng mưa, gợn cuối tan
- Attach: GROUND_ZONE; shape HEAL_RAIN; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: HEAL_ZONE_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/water_rain_soft.
- Icon: mưa trên vòng. LowFX: giữ biên/tick icon, giảm giọt50%.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-HB-05 — Lưu Thủy Bộ (cơ động)
- HUD slot5 · CLASS_HUYEN_BUT · MOBILITY
- Chuẩn bị: Hai nét nước dưới chân
- Tác động: Lùi ngược facing theo server, không projectile
- Tan biến: Hai dấu bước tan trong0,3s
- Attach: CASTER_TRAIL; shape MOVE_ONLY; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: DASH_PATH_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/water_step.
- Icon: hai vệt nước ngược. LowFX: giữ foot trail, bỏ crest.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-HB-06 — Long Mạch Hồi Nguyên (tuyệt kỹ)
- HUD slot6 · CLASS_HUYEN_BUT · ULTIMATE
- Chuẩn bị: Ấn hình học hư cấu dưới caster, không chữ giả
- Tác động: Sóng đất thấp đến ally, heal/cleanse từ state
- Tan biến: Vòng đứt và giọt tắt
- Attach: GROUND_ZONE_AND_ALLIES; shape GROUP_RESTORE; module tối đa512px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: GROUP_HEAL_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/water_chime.
- Icon: vòng nước ba dấu. LowFX: giữ wave outline và ally indicator.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-TC-01 — Trấn Sơn
- HUD slot1 · CLASS_THACH_CHUY · ACTIVE
- Chuẩn bị: Chùy qua vai, wedge đất ngắn
- Tác động: Nứt góc cạnh nhỏ trước target, không terrain mới
- Tan biến: Bụi đá lắng
- Attach: CASTER_FRONT; shape HAMMER_IMPACT; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: HIT_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/stone_hit.
- Icon: chùy nứt đá. LowFX: giữ crack/tick, giảm debris.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-TC-02 — Chấn Địa
- HUD slot2 · CLASS_THACH_CHUY · ACTIVE
- Chuẩn bị: Vòng bụi mỏng quanh caster
- Tác động: Sóng đá thấp lan từ tâm
- Tan biến: Mảnh nhỏ lắng, không platform
- Attach: CASTER_FOOT; shape RADIAL_SHOCK; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: SHOCKWAVE_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/stone_ring.
- Icon: chùy hai vòng. LowFX: giữ vòng ngoài, bỏ đá cao.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-TC-03 — Thiết Bích
- HUD slot3 · CLASS_THACH_CHUY · ACTIVE
- Chuẩn bị: Ba phiến nhỏ vai/lưng/gối
- Tác động: Phiến sát thân, không cage
- Tan biến: Nứt rồi vỡ khi buff hết
- Attach: CASTER_BODY; shape ARMOR_BUFF; module tối đa96px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: BUFF_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/stone_armor.
- Icon: ba giáp đá. LowFX: giữ ba plates, bỏ bụi quanh.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-TC-04 — Khiêu Chiến
- HUD slot4 · CLASS_THACH_CHUY · ACTIVE
- Chuẩn bị: Gõ chùy một nhịp, vòng âm đất
- Tác động: Chevron ở quái thường hướng về caster
- Tan biến: Sóng âm tan, không damage spark
- Attach: CASTER_FOOT_AND_TARGETS; shape TAUNT_RING; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: TAUNT_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/stone_call.
- Icon: chùy và chevron. LowFX: giữ threat glyph, bỏ debris.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-TC-05 — Phá Nham (cơ động)
- HUD slot5 · CLASS_THACH_CHUY · MOBILITY
- Chuẩn bị: Ghì vai sau chùy
- Tác động: Dải bụi thấp theo lao, vòng đá gọn tại hit hợp lệ
- Tan biến: Bụi lắng ở điểm dừng
- Attach: CASTER_TRAIL; shape DASH_HIT; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: DASH_HIT_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/stone_charge.
- Icon: vai và đầu chùy. LowFX: giữ đầu/đích và impact nhỏ.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-TC-06 — Sơn Thần Giáng Thế (tuyệt kỹ)
- HUD slot6 · CLASS_THACH_CHUY · ULTIMATE
- Chuẩn bị: Các đế đá thấp chỉ vùng
- Tác động: Phiến thấp có lối mở phía camera, KHÔNG collision
- Tan biến: Giảm plates từ giây cuối rồi bụi tắt
- Attach: GROUND_ZONE; shape OPEN_SANCTUARY; module tối đa512px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: SANCTUARY_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/stone_sanctuary.
- Icon: vòng đá mở. LowFX: giữ biên/vài slab, không che telegraph.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-LC-01 — Khóa Mạch
- HUD slot1 · CLASS_LINH_CUNG · ACTIVE
- Chuẩn bị: Đầu tên hình lá
- Tác động: Một tên dài trúng, dấu nhánh tại target
- Tan biến: Vệt lá gãy, mark tồn tại theo server
- Attach: PROJECTILE_AND_TARGET; shape LEAF_MARK; module tối đa128px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: PROJECTILE_MARK_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/leaf_arrow.
- Icon: tên và dấu nhánh. LowFX: giữ arrowhead/mark.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-LC-02 — Dây Gai
- HUD slot2 · CLASS_LINH_CUNG · ACTIVE
- Chuẩn bị: Một hạt đặt xuống điểm đất
- Tác động: Ba nhánh gai thấp trong vòng bẫy
- Tan biến: Thu gai khi trigger/expire, không tự nổ
- Attach: GROUND_ZONE; shape ROOT_TRAP; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: TRAP_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/root_grow.
- Icon: hạt và ba gai. LowFX: giữ trap boundary và cue trigger.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-LC-03 — Liên Châu
- HUD slot3 · CLASS_LINH_CUNG · ACTIVE
- Chuẩn bị: Năm chấm nhỏ bên dây cung
- Tác động: Năm tên theo nhịp0,11s, không bắn đồng thời do ảnh
- Tan biến: Vệt lá tan từng tên
- Attach: PROJECTILES; shape FIVE_ARROW_VOLLEY; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: VOLLEY_PROJECTILE_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/leaf_volley.
- Icon: năm mũi tên. LowFX: giữ đủ5head, giảm trail.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-LC-04 — Tán Hoa
- HUD slot4 · CLASS_LINH_CUNG · ACTIVE
- Chuẩn bị: Năm đến bảy cánh gỗ mở quạt
- Tác động: Quạt cánh100độ, không cầu nổ
- Tan biến: Cánh rơi thành cụm nhỏ
- Attach: CASTER_FRONT; shape WOOD_FAN; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: FAN_HIT_CONFIRMED (cần adapter server, chưa là wire event). Sound: SFX/SKILL/leaf_fan.
- Icon: quạt năm cánh. LowFX: giữ cánh chính, bỏ bụi lá.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-LC-05 — Phi Diệp (cơ động)
- HUD slot5 · CLASS_LINH_CUNG · MOBILITY
- Chuẩn bị: Dấu lá sau gót, cung hướng trước
- Tác động: Lùi theo server và một tên phản kích riêng
- Tan biến: Foot trail tắt, hit tên chỉ khi confirmed
- Attach: CASTER_TRAIL_AND_PROJECTILE; shape RETREAT_AND_ARROW; module tối đa256px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: RETREAT_ARROW_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/leaf_retreat.
- Icon: cung và bước lùi. LowFX: giữ một tên và hai dấu chân.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.

## SK-LC-06 — Bách Tiễn Quy Tông (tuyệt kỹ)
- HUD slot6 · CLASS_LINH_CUNG · ULTIMATE
- Chuẩn bị: Vòng rêu viền ochre, ba glyph tên
- Tác động: Bốn đợt mưa tên trong vùng đã khóa
- Tan biến: Vệt tên ngắn tắt, không cây mọc ngoài vùng
- Attach: GROUND_ZONE; shape ARROW_RAIN; module tối đa512px ở20PPU. Module không phải kích thước hitbox.
- Cue semantic: ARROW_RAIN_STATE (cần adapter server, chưa là wire event). Sound: SFX/SKILL/leaf_rain.
- Icon: ba tên trên vòng. LowFX: giữ ranh/nhịp4đợt, giảm tên trang trí.
- Frame budget2/3/3 ở12fps là số keyframe minh họa; hold/loop theo server state, không lấy tổng frame làm cooldown/duration.
