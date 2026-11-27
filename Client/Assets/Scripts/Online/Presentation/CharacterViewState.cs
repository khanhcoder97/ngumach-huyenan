// CharacterViewState — Immutable view state for character stats & equipped items.
// Rules:
//   - Authoritative stats come strictly from P1Self; no local ATK/DEF calculations.
//   - Missing combat stats explicitly marked with MissingStatReason.
//   - Slot normalization maps DEC-023 aliases to 12 canonical slots.
//   - Unsupported mutations (equip/unequip/salvage) marked with ActionDisabledReason.
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class CharacterViewState
    {
        // ── Canonical slot identifiers (Spec §3) ──────────────────────────────
        public const string SlotHat = "EQUIP_HAT";
        public const string SlotChest = "EQUIP_CHEST";
        public const string SlotLegs = "EQUIP_LEGS";
        public const string SlotWeapon = "EQUIP_WEAPON";
        public const string SlotGloves = "EQUIP_GLOVES";
        public const string SlotBoots = "EQUIP_BOOTS";
        public const string SlotNeck = "EQUIP_NECK";
        public const string SlotRingL = "EQUIP_RING_L";
        public const string SlotRingR = "EQUIP_RING_R";
        public const string SlotPendant = "EQUIP_PENDANT";
        public const string SlotCloak = "EQUIP_CLOAK";
        public const string SlotSeal = "EQUIP_SEAL";

        public static readonly string[] AllCanonicalSlots = new[]
        {
            SlotHat, SlotChest, SlotLegs, SlotWeapon,
            SlotGloves, SlotBoots, SlotNeck, SlotRingL,
            SlotRingR, SlotPendant, SlotCloak, SlotSeal
        };

        // ── Authoritative character vitals ───────────────────────────────────
        public string CharacterId { get; }
        public string ClassId { get; }
        public int Hp { get; }
        public int MaxHp { get; }
        public int Mp { get; }
        public int MaxMp { get; }
        public double X { get; }
        public double Y { get; }

        // ── Equipment slots ──────────────────────────────────────────────────
        public IReadOnlyDictionary<string, ItemSlotView> EquippedSlots { get; }

        // ── Server baseline flags & missing fields ───────────────────────────
        public const string MissingStatReason = "Chưa có trong snapshot authoritative - missing server field";
        public const string ActionDisabledReason = "Chưa có endpoint server (authoritative action unavailable in baseline)";

        public bool HasAuthoritativeCombatStats => false;
        public int? PhysicalAttack => null;
        public int? MagicAttack => null;
        public int? Armor => null;
        public float? CritRate => null;
        public float? MoveSpeed => null;

        public bool CanEquip => false;
        public bool CanUnequip => false;
        public bool CanSalvage => false;
        public bool CanEnhance => false;

        public CharacterViewState(
            P1Self self,
            IReadOnlyDictionary<string, ItemSlotView> equippedSlots = null)
        {
            if (self == null) throw new ArgumentNullException(nameof(self));
            CharacterId = self.characterId ?? "";
            ClassId = self.classId ?? "";
            Hp = self.hp;
            MaxHp = self.maxHp;
            Mp = self.mp;
            MaxMp = self.maxMp;
            X = self.x;
            Y = self.y;
            EquippedSlots = equippedSlots ?? new Dictionary<string, ItemSlotView>(StringComparer.OrdinalIgnoreCase);
        }

        public ItemSlotView GetEquippedItem(string slot)
        {
            string canonical = NormalizeSlot(slot);
            if (string.IsNullOrEmpty(canonical)) return null;
            EquippedSlots.TryGetValue(canonical, out var item);
            return item;
        }

        public static string NormalizeSlot(string rawSlot)
        {
            if (string.IsNullOrWhiteSpace(rawSlot)) return null;
            string trimmed = rawSlot.Trim();

            // Direct canonical matching
            if (trimmed.Equals(SlotHat, StringComparison.OrdinalIgnoreCase)) return SlotHat;
            if (trimmed.Equals(SlotChest, StringComparison.OrdinalIgnoreCase)) return SlotChest;
            if (trimmed.Equals(SlotLegs, StringComparison.OrdinalIgnoreCase)) return SlotLegs;
            if (trimmed.Equals(SlotWeapon, StringComparison.OrdinalIgnoreCase)) return SlotWeapon;
            if (trimmed.Equals(SlotGloves, StringComparison.OrdinalIgnoreCase)) return SlotGloves;
            if (trimmed.Equals(SlotBoots, StringComparison.OrdinalIgnoreCase)) return SlotBoots;
            if (trimmed.Equals(SlotNeck, StringComparison.OrdinalIgnoreCase)) return SlotNeck;
            if (trimmed.Equals(SlotRingL, StringComparison.OrdinalIgnoreCase)) return SlotRingL;
            if (trimmed.Equals(SlotRingR, StringComparison.OrdinalIgnoreCase)) return SlotRingR;
            if (trimmed.Equals(SlotPendant, StringComparison.OrdinalIgnoreCase)) return SlotPendant;
            if (trimmed.Equals(SlotCloak, StringComparison.OrdinalIgnoreCase)) return SlotCloak;
            if (trimmed.Equals(SlotSeal, StringComparison.OrdinalIgnoreCase)) return SlotSeal;

            // DEC-023 / Core model alias mappings
            if (trimmed.Equals("MAIN_HAND", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("WEAPON", StringComparison.OrdinalIgnoreCase)) return SlotWeapon;

            if (trimmed.Equals("HEAD", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("HELM", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("HAT", StringComparison.OrdinalIgnoreCase)) return SlotHat;

            if (trimmed.Equals("BODY", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("CHEST", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("ARMOR", StringComparison.OrdinalIgnoreCase)) return SlotChest;

            if (trimmed.Equals("PANTS", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("LEGS", StringComparison.OrdinalIgnoreCase)) return SlotLegs;

            if (trimmed.Equals("FEET", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("BOOTS", StringComparison.OrdinalIgnoreCase)) return SlotBoots;

            if (trimmed.Equals("GLOVES", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("HANDS", StringComparison.OrdinalIgnoreCase)) return SlotGloves;

            if (trimmed.Equals("AMULET", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("NECK", StringComparison.OrdinalIgnoreCase)) return SlotNeck;

            if (trimmed.Equals("RING1", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("RING_1", StringComparison.OrdinalIgnoreCase)) return SlotRingL;

            if (trimmed.Equals("RING2", StringComparison.OrdinalIgnoreCase) ||
                trimmed.Equals("RING_2", StringComparison.OrdinalIgnoreCase)) return SlotRingR;

            if (trimmed.Equals("CLOAK", StringComparison.OrdinalIgnoreCase)) return SlotCloak;
            if (trimmed.Equals("SEAL", StringComparison.OrdinalIgnoreCase)) return SlotSeal;
            if (trimmed.Equals("PENDANT", StringComparison.OrdinalIgnoreCase)) return SlotPendant;

            return trimmed.ToUpperInvariant();
        }
    }
}
