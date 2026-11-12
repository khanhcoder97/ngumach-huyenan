# Quyết định triển khai inventory/progression private-alpha — 08/11/2026

`DEC-INVENTORY-ALPHA-20261108`, JSON nguồn tại `Implementation/Content/DesignBaselines/inventory_capacity_consumption_20261108.json`. Duyệt hai packet QOD-24 về túi đầy và consume với sửa dưới đây. Nguồn DEC-023/Runtime_State_and_Catalog_Precision ở main `a793aed89e8c5fc152f60e8ead30c7cf25280978` đã được đọc; Qoder không cần merge toàn main để nhận các quyết định này. Đây là quyền triển khai/schema additive, chưa nghiệm thu runtime. Release OFF.

## Túi đầy: duyệt luật100slot và sửa hai mâu thuẫn của packet

Một stack hợp lệ chiếm một slot BAG authoritative, quantity không vượt `stack_limit`; giá trị3 là maximum quantity của một stack, không là lượng phải nhận mỗi lần. Chỉ merge template/metadata fingerprint tương thích (binding, durability, affix/instance semantics có nguồn); không trộn item khác rarity hoặc “gần giống”. Phân trang/view index không là slot ID. Planning theo thứ tự slot ổn định trước khi commit; một reward batch phải fit cả batch.

Duyệt `inventory_full`, HTTP409, retryableTrue, messageKeyP1.ERROR.INVENTORY_FULL, bổ sung schema/error vocabulary/examples/negative fixtures tương ứng. Refusal không đổi item/currency/XP/quest/revision, không ghi success receipt; cùng key/body có thể retry sau giải phóng chỗ cho tới khi commit thật. **Không cache từ chối túi đầy vĩnh viễn** như §4.6 packet: điều đó mâu thuẫn retryable và việc cho người chơi thử lại. Nếu payload có expectedRevision, request mới với revision mới phải dùng key mới; không đổi body của key đã commit.

**Equip/unequip có thể đổi số slot BAG**: equip có thể giải phóng một slot, unequip có thể cần một slot. Không nhận câu “equip/unequip không đổi số item trong túi” làm ngoại lệ capacity. Refuse unequip nếu không fit, giữ nguyên equipment/revision/receipt. Nghiệp vụ swap chỉ được làm nếu transaction đã có policy, không tự invent swap.

Grant quest/gather/loot/bag grant khác dùng chung capacity planner. Turn-in full giữ READY_TO_TURN_IN, không tiêu quest item, không complete và không cấp thưởng từng phần. Loot full giữ cùng death/roll decision pending, không reroll khi retry và không đánh dấu PAID trước grant; nếu thời hạn claim chưa có nguồn, giữ private-alpha obligation rõ thay vì làm mất reward im lặng. Không suy mailbox hoặc quest pouch để né fullbag.

Áp sau gate mới `P1:InventoryCapacity:Enabled` cộng AlphaProfile, defaultOFF; bật capacity khi không có profile là lỗi startup. Đây là sửa packet đề nghị đổi production-default không gate. Capability/handoff phải nói rõ enforcement active hay metadata-only. Inventory hiện vượt100 do build cũ không được xóa item: preserve rồi refuse net-new allocation; cho phép consume/equip hoặc operation giảm chỗ. Quest pouch30 và bank120–200 là container riêng còn unsupported, chưa mở InventoryLocations/v1enum trong gói này.

## Consume: duyệt HP/MP có nguồn, chưa mở revive/buff/repair

Duyệt route `POST /p1/inventory/consume`, gate riêng `P1:InventoryConsume:Enabled` cộng AlphaProfile, releaseOFF. Payload chỉ itemInstanceId và expectedRevision trong envelope/idempotency/owner hiện hành. Response InventorySnapshotv1 hiện có cộng receipt hpRestored/mpRestored/hpAfter/mpAfter/effectItemId; Qoder chốt schema đầy đủ từ domain, công bố cho client trước code. Không để comment tên schema tưởng tượng thành hợp đồng.

Lượng hồi = floor(max hiệu dụng hiện tại × % nguồn), clamp vào maximum; max3 và25% cho0 thì no_effect, không tiêu stack. Đầy pool thì no_effect, giữ item/revision. ActorHP0 không được dùng thuốcHP để bypass death/life; từ chối invalid_condition với fieldhp. Không guard khoảng cáchNPC, không tự đặt extra cooldown hoặc anti-macro phí. Nguyên tử spend đúng một unit stack + actor pool + inventory revision + receipt; global key/owner/hash replay historical result không heal/spend lần nữa, kể cả reconnect hoặc pool đã đổi.

Duyệt codes mới not_consumable/effect_unsupported/revive_not_modelled/no_effect theo packet và schema; confirmed error client phải được xử lý khác timeout. Giữ toàn bộ data hàng nguồn, chỉ activation HP/MP đã đủ effect. Revive, buff food20phút, repair kit target và ally-heal chưa được mở public handler theo suy đoán. Food clock là UTC/expiresAt offline theo DEC-023; status skill là simulationtick. Các domain/model đó có thể làm độc lập có fixture và activation refusal, không giả đã có route.

Auto-use là lựa chọn rõ của người chơi, chỉ sau wire review. Consume accepted áp ngay; không delay2s để chờUndo, không “undo” healing đã commit. Mất response giữ key/body để đối chiếu; hủy local intent chưa gửi không phải rollback command đã gửi.

## Effective stats và progression

Cho phép triển khai DEC-023 source-backed aggregation sau gate `P1:EffectiveStats:Enabled` + AlphaProfile, releaseOFF. Oracles giữ: L1noGear HP198/MP102/PhysicalAttack20/Armor10; weaponMK-T1power12+STR2 choAttack38 (không50); hatArmor2+VIT1 choHP212/Armor14 (không16). weapon_power/primaryAttack là alias, armor/primaryGiáp là alias, secondary thêm đúng một lần, CSV rarity đã scale không nhân lại. Modifier chưa có nguồn không mặc định0 rồi gọi hoàn thành effect.

Thay maxHP/MP do level/equip/buff hết: giữ current tuyệt đối rồi clamp; HP0 giữ0. XP/level/điểm chưa phân phối/stat/reward/revision/receipt phải cùng transaction. Không tự phân điểm/auto-build nếu người chơi chưa chọn; EXP cấp100 không đổi thành tiền. Snapshotcast accepted giữ semantics nguồn, hit recheck guards. Legacy REFERENCE_L5/enduranceHP2000 phải là profile riêng có nhãn, không bị thay silently rồi đổi expected cũ cho xanh.

Đường tự chơi lên11 chưa được bypass bởi tutorial unlock. Giao bảng progression source và golden journey thật; positive conformance fixture level11 có nhãn không chứng minh natural progression. Thay wire actor/stat projection theo additive packet/schema riêng, giữ old consumers và world/event enums đóng. Không đổi số cân bằng ngoài nguồn trong quyết định này.
