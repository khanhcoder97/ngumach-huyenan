# Export nội dung, topology và bàn giao đủ phạm vi

Tài liệu này chốt field và hành vi còn thiếu để chuyển catalogue thành nội dung executable. Đọc cùng Production_Rules_Complete_v1_vi.md. Một record có tên/ID chưa được xem là có đủ script/asset/gameplay. Mọi exporter báo file/recordId/field/errorCode và fail khi thiếu numeric hoặc foreign key.

## 1. Bundle và nguồn dữ liệu

Bundle manifest có bundleId/version/schemaVersion/minClientBuild/protocolVersion/createdUtc/sourceCommit và files[path,sha256,recordCount]. Hash tính trên bytes sau export; paths repo-relative, chặn traversal/symlink ra ngoài. Build chưa resolve đủ reference không tạo release bundle. DesignBaselines là đầu vào thiết kế, không tự đăng ký vào loader P1.

Thứ tự: decision hiện hành→numeric dataset chuyên ngành→domain spec→GDD. Chỗ đã bổ sung mới trong completion_v1 ưu tiên hơn câu mô tả chưa có số. Mọi override cần ghi sourceRef và migration; không im lặng nhận min/max range như số tuyệt đối. Field unit phải nằm trong schema; mét chuyển WU đúng một lần.

## 2. Record bắt buộc theo miền

| Loại record | Trường bổ sung phải có trước content lock |
|---|---|
| Class | classId, base stat profile, damage type, weapon slots, resource rules, six active IDs,8 passive IDs, starter gear, portrait/source refs |
| Skill | ID/class, unlock/rank, target mode, range/radius/angle WU, maxTargets, cast/recovery/tick timeline, cost/CD, damage/heal/status coefficients cho PvE/PvP/boss, interrupt/cancel policy, VFX/SFX keys |
| Monster | ID/archetype/level scaling, footprint/nav profile, HP/attack/defense, aggro/leash/threat, attacks, state graph, death/respawn, loot/quest event refs |
| Boss | Monster fields + phase graph thresholds/objectives, attack chooser/priority/CD, target-lock timing, arena, safe zones, reset/wipe, versioned rewards |
| NPC | canonical ID, instance placement/floor, role/service list, interaction radius, display/dialogue keys, quest phase conditions, invulnerability, actor/portrait assets |
| Quest | accept/turn-in NPC, level/prereqs, objective graph, target record IDs/count/map/floor/range, shared/unique progress policy, checkpoints/timeouts/retry, dialogue graph, rewards/reset/unlocks |
| Item | template/variant ID, slot/class/tier/rarity, base stat values, weighted affix pool, hidden/set/socket, durability/bind/trade, maxStack, use effect/cooldown, source/price/localization |
| Recipe | ID/output choice, full cost vector, skill/level guard, success/fail outputs, probability/pity policy, fees/caps, lock/commit/retry policy |
| Map | TOP_DOWN_XY/version/bounds, floors, walkable/blocked polygons, floor links, placements/portals/safe zones/weather, asset chunk refs, migration review |
| Activity | roster/eligibility/ready/timers/phase states, scheduler timezone, reconnect/tie/void, reward/cap and compensation policy |

Skill metadata dùng mỗi distance field đúng ngữ nghĩa: SELF buff có effectRadius riêng nếu phản kích, CONE có range+angle, DASH có travel distance+hit shape, projectile có speed/TTL/collision. Không dùng một rangeWu duy nhất thay cả ba chức năng khác nhau khi runtime mở rộng.

## 3. Topology theo từng map

Giữ tất cả46 map ID và349 placements trong manifest. Mỗi map phải có file topology riêng; không clone một polygon chữ nhật cho cả46 map để coi đã xong. Frame Y hiện hành là Bắc–Nam theo DEC-016, không độ cao. Source geometry chưa có không suy thành walkable.

Một placement review ghi recordId/originalXY/newXY/floorId/footprint/reason/reviewer/evidence. Điểm mới phải nằm trong nav, không đè blocked polygon/NPC/arrival safe zone; route quest từ spawn đến target có path. Khi NPC cùng ID có nhiều vị trí, instance key là mapInstanceId+recordId; service đi cùng canonical NPC ID không tạo inventory riêng ngoài policy.

Bến Mưa ưu tiên9 anchors NPC,7 spawn thường/elite,2 quest waves,quest/world boss variants và các node/interactions đang có. Từng khu cần đường vòng telegraph, đường đến package/van, rescue và escort checkpoint. NPC escort dùng một actor với phasing theo party/instance, không tạo NPC_LYAN_ESCORT entity canonical mới.

Thăng Long ưu tiên chợ/lò rèn/kho/bang/khán đài/cổng bốn hướng; spawn crowd tách collision và service. Arena có boundary và instance riêng; spectator không cùng damage roster. Node, crowd hoặc banner không chặn đường merchant→storage→forge. Chunk art đề nghị32×32 tile (25,6×25,6WU); stream visible chunks+1 vòng lân cận, unload khi không còn refs. Đây là chunk render, không đổi map bounds hay portal coordinates.

## 4. Pixel art và animation

Directional actor dùng cell48×64, directions N/NE/E/SE/S/SW/W/NW. Boss có frame size riêng trong atlas<=2048; không kéo boss về cell hero. Idle4frame@6fps; walk6@8fps theo DEC-015; các combat clips dùng timeline skill và frame hold, không đổi server hit time theo FPS. Mỗi event có semantic name và tick offset, không đọc tên sprite để gây damage.

Manifest hiện tại giữ schema đã merge. Mở proposal sidecar v2 cho frameWidth/frameHeight/rows/columns/pivotXY/animation frame list/event anchors/assetRole; directional=false cho VFX/UI/tileset. Migration validator phải chấp nhận v1 đến hết cửa tương thích, không bắt VFX có8 hướng. Chỉ đếm PNG IHDR không chứng minh alpha/palette/duplicate frame; pipeline cần decoded-pixel audit và preview playback.

Art catalogue cần entries cho5 class base+gear variants,83 NPC,quái/boss canonical,companion/mount,environment46 maps,30 active VFX,basic/dodge/hit/death/weather,items/skills/services/minimap icons,UI/font/portraits. Mỗi entry có requiredForGate,sourceRef,source/exports,license,state và evidence. Không mặc định có asset cho mỗi ID chỉ vì dùng chung archetype; shared asset phải khai explicit alias.

## 5. Coverage và đóng thiếu

Coverage report tách required IDs / executable records / refs resolved / assets art-approved / engine-imported / integrated / device-tested. Mẫu: quest76 required,1 runtime không thể báo100% do76 dialogue IDs tồn tại. Level table100 rows không chứng minh class balance. Unknown không đổi thành PASS; absent là BLOCKED_CONTENT.

P1 yêu cầu đường chơi Bến Mưa và lưu tiến trình thật. Full game yêu cầu tất cả hàng catalogue được review/export, asset không draft trong user flow, không graph cycle/soft-lock, server từng activity chạy được. Mỗi map/quest/boss có acceptance record kèm build/data hash. Mọi title/legal/hosting quyết định chưa có owner sign-off phải ghi pending, không viết giả chữ ký.
