using Server.Health.Gameplay.Inventory;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

// QOD-21 Q1: the alpha JSON is approved design data, not a suggestion. These
// checks fail startup (when the profile is loaded) instead of letting a typo or
// a drifted copy change what a private alpha run can do. The numbers checked
// here are the ones the approved decision fixes; anything not checked yet is
// still parsed and will be validated by its own consumer.
public static class AlphaProfileValidator
{
    public const string DecisionId = "DESIGN-BM-ALPHA-20261103";

    public static void Validate(
        AlphaDesign design,
        MapBoundsCatalog maps,
        NpcAnchorCatalog npcs,
        WorldRecordCatalog records)
    {
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(maps);
        ArgumentNullException.ThrowIfNull(npcs);
        ArgumentNullException.ThrowIfNull(records);

        if (design.SchemaVersion != 1)
        {
            throw new InvalidOperationException(
                $"Alpha profile schemaVersion {design.SchemaVersion} is not 1.");
        }

        if (!string.Equals(design.DecisionId, DecisionId, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"Alpha profile decisionId '{design.DecisionId}' is not {DecisionId}.");
        }

        if (!design.Status.StartsWith(
                "APPROVED_FOR_IMPLEMENTATION", StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"Alpha profile status '{design.Status}' is not approved for implementation.");
        }

        if (design.DefaultEnabled)
        {
            throw new InvalidOperationException(
                "Alpha profile must not be enabled by default.");
        }

        ValidateScope(design, maps);
        ValidateInventory(design.Inventory);
        ValidateProgression(design.Progression);
        ValidateOverlay(design, maps, npcs, records);
        ValidateQuestRules(design, maps, npcs, records);
        ValidateBoss(design.Boss, maps);
        ValidateLoot(design.Loot);
        ValidateDeathReturn(design.DeathReturn, design.Scope.MapId, maps);

        if (!design.ProductionGatesRemainOff ||
            !design.DevProfileMustBeExplicit ||
            !design.NoReadDialogueReward ||
            !design.NoDuplicateBoss ||
            !design.FullBagKeepsReady ||
            !design.UnknownFieldMustFailExport ||
            !design.NoTopologySelfCertification)
        {
            throw new InvalidOperationException(
                "Alpha acceptance flags must keep production gates off, require an " +
                "explicit dev profile, forbid dialogue rewards, duplicate bosses, " +
                "full-bag rejection, unknown-field export and topology self-certification.");
        }

        if (design.Sources.Count == 0)
        {
            throw new InvalidOperationException("Alpha profile has no sources.");
        }
    }

    private static void ValidateScope(AlphaDesign design, MapBoundsCatalog maps)
    {
        if (design.Scope.ClassIds.Count != 1 ||
            !string.Equals(design.Scope.ClassIds[0], "CLASS_MINH_KIEM", StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "Alpha scope must cover exactly CLASS_MINH_KIEM.");
        }

        if (!string.Equals(design.Scope.MapId, "MAP_BEN_MUA", StringComparison.Ordinal) ||
            !maps.TryResolve(design.Scope.MapId, out _))
        {
            throw new InvalidOperationException(
                $"Alpha scope map '{design.Scope.MapId}' is not MAP_BEN_MUA.");
        }

        if (design.Scope.WorldBossEnabled ||
            design.Scope.CanonicalPlacementCsvEdited ||
            design.Scope.TopologyReviewed ||
            !design.Scope.RequiresExplicitPrivateProfile)
        {
            throw new InvalidOperationException(
                "Alpha scope must disable the world boss, keep the placement CSV " +
                "untouched, keep topology unreviewed and require an explicit profile.");
        }
    }

    private static void ValidateInventory(AlphaInventoryRules inventory)
    {
        if (inventory.BagSlots != 100)
        {
            throw new InvalidOperationException(
                $"Alpha bagSlots {inventory.BagSlots} is not the approved 100.");
        }

        // The implemented twelve-token vocabulary is the single source of truth: the
        // design list must equal it (same tokens, same order) and every token must be
        // reachable from a canonical catalog slot label. A design edit therefore fails
        // here instead of being served by a stale list.
        InventoryV2Slots.ValidateAgainstDesign(inventory.EquipmentSlots);
        InventoryV2Slots.ValidateLabelMap();

        if (inventory.AutoSwap ||
            !string.Equals(inventory.Revision, "INVENTORY_AGGREGATE", StringComparison.Ordinal) ||
            !string.Equals(
                inventory.MaxResourceChange,
                "KEEP_CURRENT_ABSOLUTE_THEN_CLAMP_NO_HEAL", StringComparison.Ordinal) ||
            !string.Equals(
                inventory.WireMigration,
                "V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT", StringComparison.Ordinal) ||
            inventory.SchemaVersion != 2)
        {
            throw new InvalidOperationException(
                "Alpha inventory rules do not match the approved no-swap v2 contract.");
        }

        if (!string.Equals(inventory.ReadRoute, "GET /p1/inventory/v2/{sessionId}",
                StringComparison.Ordinal) ||
            !string.Equals(inventory.EquipRoute, "POST /p1/inventory/v2/equip",
                StringComparison.Ordinal) ||
            !string.Equals(inventory.UnequipRoute, "POST /p1/inventory/v2/unequip",
                StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "Alpha inventory routes do not match the approved v2 routes.");
        }
    }

    private static void ValidateProgression(AlphaProgressionRules progression)
    {
        if (!progression.AcceptSnapshot ||
            !progression.AbsoluteSourceRewardWins ||
            progression.NormalQuestXpNumerator != 25 ||
            progression.BossQuestXpNumerator != 55 ||
            progression.Denominator != 100)
        {
            throw new InvalidOperationException(
                "Alpha progression must snapshot 25% / 55% at accept and prefer " +
                "absolute source rewards.");
        }
    }

    private static void ValidateOverlay(
        AlphaDesign design,
        MapBoundsCatalog maps,
        NpcAnchorCatalog npcs,
        WorldRecordCatalog records)
    {
        var recordIds = new HashSet<string>(StringComparer.Ordinal);
        var entityIds = new HashSet<string>(StringComparer.Ordinal);
        var questIds = new HashSet<string>(StringComparer.Ordinal)
        {
            "P00-02", "P00-03", "P00-04", "P00-05"
        };
        if (!maps.TryResolve(design.Scope.MapId, out var bounds))
        {
            throw new InvalidOperationException("Alpha map bounds are missing.");
        }

        foreach (var overlay in design.OverlayRecords)
        {
            if (!recordIds.Add(overlay.RecordId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay recordId '{overlay.RecordId}' is duplicated.");
            }

            if (!entityIds.Add(overlay.EntityId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay entityId '{overlay.EntityId}' is duplicated.");
            }

            if (records.TryGet(overlay.RecordId, out _))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay recordId '{overlay.RecordId}' collides with a world record.");
            }

            if (overlay.Kind is not ("INTERACTABLE" or "RESCUE_INTERACTABLE" or "QUEST_HAZARD"))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' has unsupported kind '{overlay.Kind}'.");
            }

            if (!questIds.Contains(overlay.QuestId))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' references unknown quest '{overlay.QuestId}'.");
            }

            if (!bounds.Contains(overlay.X, overlay.Y))
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' at ({overlay.X},{overlay.Y}) " +
                    $"is outside {design.Scope.MapId} bounds.");
            }

            if (overlay.CountPerCharacter is <= 0)
            {
                throw new InvalidOperationException(
                    $"Alpha overlay '{overlay.RecordId}' countPerCharacter must be positive.");
            }
        }

        if (design.OverlayRecords.Count != 7)
        {
            throw new InvalidOperationException(
                $"Alpha profile must seed 7 overlay records, found {design.OverlayRecords.Count}.");
        }
    }

    private static void ValidateQuestRules(
        AlphaDesign design,
        MapBoundsCatalog maps,
        NpcAnchorCatalog npcs,
        WorldRecordCatalog records)
    {
        var rules = design.QuestRules;
        foreach (var npcId in new[]
                 {
                     rules.P00_02_TurnInNpcId,
                     rules.P00_03_TurnInNpcId,
                     rules.P00_04_TurnInNpcId,
                     rules.P00_04_ActorId,
                     rules.P00_05_TurnInNpcId,
                     rules.P00_05_PhaseNpcId,
                     rules.C1_01_StartNpcId,
                     rules.C1_01_TurnInNpcId,
                     rules.C1_01_TrialRegistrationNpcId
                 })
        {
            if (!npcs.HasAnchorFor(npcId))
            {
                throw new InvalidOperationException(
                    $"Alpha quest rules reference NPC '{npcId}' with no anchor.");
            }
        }

        if (!string.Equals(rules.P00_05_PhaseNpcId, "NPC_TA_VAN_KHANH",
                StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "P00-05 phase override must reuse NPC_TA_VAN_KHANH, not a clone.");
        }

        if (rules.P00_02_RipplesRequired != 3 ||
            rules.P00_02_CarplingKillsRequired != 4 ||
            rules.P00_02_InteractionRangeWu != 5)
        {
            throw new InvalidOperationException(
                "P00-02 alpha counts/range do not match the approved decision.");
        }

        if (rules.P00_03_VillagersRequired != 2 ||
            rules.P00_03_WaterrootKillsRequired != 3 ||
            rules.P00_03_WaveWindupSeconds <= 0 ||
            rules.P00_03_WaveRepeatCooldownSeconds <= 0 ||
            rules.P00_03_WaveRawDamage <= 0)
        {
            throw new InvalidOperationException(
                "P00-03 alpha counts/wave values are not positive as approved.");
        }

        if (rules.P00_03_WaveMin.X >= rules.P00_03_WaveMax.X ||
            rules.P00_03_WaveMin.Y >= rules.P00_03_WaveMax.Y ||
            !maps.TryResolve(design.Scope.MapId, out var bounds) ||
            !bounds.Contains(rules.P00_03_WaveMin.X, rules.P00_03_WaveMin.Y) ||
            !bounds.Contains(rules.P00_03_WaveMax.X, rules.P00_03_WaveMax.Y))
        {
            throw new InvalidOperationException(
                "P00-03 training-wave rectangle is invalid or outside the map.");
        }

        if (rules.P00_04_CheckpointXs.Count != 2 ||
            rules.P00_04_CheckpointXs[0] != 80 ||
            rules.P00_04_CheckpointXs[1] != 120 ||
            rules.P00_04_Waypoints.Count != 3 ||
            rules.P00_04_WaveA.Count != 3 ||
            rules.P00_04_WaveB.Count != 3 ||
            !string.Equals(rules.P00_04_WaveA.MobId, "MOB_CARPLING", StringComparison.Ordinal) ||
            !string.Equals(rules.P00_04_WaveB.MobId, "MOB_WATERROOT", StringComparison.Ordinal) ||
            !records.TryGet(rules.P00_04_WaveA.RecordId, out _) ||
            !records.TryGet(rules.P00_04_WaveB.RecordId, out _))
        {
            throw new InvalidOperationException(
                "P00-04 escort/wave rules do not match the approved decision or records.");
        }

        if (rules.P00_04_CreditKey.Count != 5 ||
            !rules.P00_04_CreditKey.Contains("instanceId") ||
            !rules.P00_04_CreditKey.Contains("questAttemptId") ||
            !rules.P00_04_CreditKey.Contains("waveId") ||
            !rules.P00_04_CreditKey.Contains("entityLifeId") ||
            !rules.P00_04_CreditKey.Contains("deathEventId"))
        {
            throw new InvalidOperationException(
                "P00-04 creditKey must carry instance/attempt/wave/life/death ids.");
        }

        if (!records.TryGet(rules.P00_05_BossRecordId, out var bossRecord) ||
            !string.Equals(bossRecord.MapId, design.Scope.MapId, StringComparison.Ordinal) ||
            !records.TryGet(rules.P00_05_WorldEventRecordIdDisabled, out var worldBoss) ||
            !string.Equals(worldBoss.EntityIds.FirstOrDefault(), "BOSS_MANG_COT",
                StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "P00-05 boss/world-event records do not match the approved decision.");
        }

        if (rules.P00_05_OrderedObjectives.Count != 3 ||
            !rules.P00_05_TrialNpcConditionOverride.Contains("NPC_CLASS_TRIAL", StringComparison.Ordinal) ||
            !rules.P00_05_OrderedObjectives[2].Contains("NPC_CLASS_TRIAL", StringComparison.Ordinal) ||
            !maps.TryResolve(design.Scope.MapId, out var mapBounds) ||
            !mapBounds.Contains(rules.P00_05_PhaseNpcX, rules.P00_05_PhaseNpcY))
        {
            throw new InvalidOperationException(
                "P00-05 ordered objectives, the trial NPC condition override, or the " +
                "phase-NPC position do not match the approved decision.");
        }

        if (rules.C1_01_MinLevel != 11 ||
            !string.Equals(rules.C1_01_MapId, "MAP_THANH_LAC", StringComparison.Ordinal) ||
            !maps.TryResolve(rules.C1_01_MapId, out _) ||
            rules.C1_01_PrerequisiteQuestIds.Count != 1 ||
            !string.Equals(rules.C1_01_PrerequisiteQuestIds[0], "P00-05",
                StringComparison.Ordinal) ||
            rules.C1_01_Representatives.Count == 0 ||
            !string.Equals(rules.C1_01_CurrencyId, "COIN", StringComparison.Ordinal) ||
            rules.C1_01_CurrencyAmount != 80 ||
            !rules.C1_01_NoLevelBypass)
        {
            throw new InvalidOperationException(
                "C1-01 alpha record does not match the approved min-level/reward contract.");
        }

        // The unlock clause is prose in the design, so the flag and the portal map
        // the server commits are pinned against the sentence itself: a design that
        // renames either one fails startup rather than granting something the
        // source no longer names, and the portal it grants has to be the same map
        // C1-01 is played on.
        if (!rules.P00_05_UnlockText.Contains(
                AlphaChapterUnlockRules.Flag, StringComparison.Ordinal) ||
            !rules.P00_05_UnlockText.Contains(
                AlphaChapterUnlockRules.PortalMapId, StringComparison.Ordinal) ||
            !string.Equals(
                AlphaChapterUnlockRules.PortalMapId, rules.C1_01_MapId, StringComparison.Ordinal) ||
            !maps.TryResolve(AlphaChapterUnlockRules.PortalMapId, out _))
        {
            throw new InvalidOperationException(
                "P00-05 unlock clause must name both the committed flag " +
                $"'{AlphaChapterUnlockRules.Flag}' and the C1-01 portal map " +
                $"'{AlphaChapterUnlockRules.PortalMapId}'; found " +
                $"'{rules.P00_05_UnlockText}'.");
        }
    }

    private static void ValidateBoss(AlphaBossRules boss, MapBoundsCatalog maps)
    {
        if (!string.Equals(boss.EntityId, "BOSS_MANG_COT", StringComparison.Ordinal) ||
            !string.Equals(boss.ProfileId, "BOSS_MANG_COT_QUEST_ALPHA_1",
                StringComparison.Ordinal) ||
            boss.Level != 5 ||
            boss.MaxHp != 1200 ||
            boss.Attack != 24 ||
            boss.Armor != 6)
        {
            throw new InvalidOperationException(
                "Alpha boss profile is not the approved tutorial profile.");
        }

        if (!string.Equals(boss.ArenaShape, "CIRCLE", StringComparison.Ordinal) ||
            boss.CenterX != 178 ||
            boss.CenterY != 0 ||
            boss.RadiusWu != 11)
        {
            throw new InvalidOperationException(
                "Alpha boss arena must be the Ø22 ring at (178,0).");
        }

        if (boss.SafePads.Count != 2 ||
            boss.SafePads[0] != new AlphaPoint(168, 0) ||
            boss.SafePads[1] != new AlphaPoint(188, 0) ||
            boss.SafePadRadiusWu != 0.75 ||
            !boss.SafePadsPhase3Only ||
            !maps.TryResolve("MAP_BEN_MUA", out var bounds) ||
            !bounds.Contains(boss.CenterX, boss.CenterY))
        {
            throw new InvalidOperationException(
                "Alpha boss safe pads do not match the approved decision.");
        }

        if (boss.Phase2Threshold != 0.6 ||
            boss.Phase3Threshold != 0.3 ||
            boss.MaxTransitionsPerImpact != 1 ||
            boss.PhaseGuardSeconds != 1.0 ||
            boss.Phase2RecoveryMultiplier != 0.8 ||
            boss.Phase3AdditionalDamageMultiplier != 1.0)
        {
            throw new InvalidOperationException(
                "Alpha boss phase rules do not match the approved decision.");
        }

        if (!boss.Priority.SequenceEqual(new[] { "C", "B", "A" }, StringComparer.Ordinal) ||
            boss.OverlapAllowed)
        {
            throw new InvalidOperationException(
                "Alpha boss must use C→B→A priority with no overlap.");
        }

        if (boss.Moves.Count != 3 ||
            boss.Moves.Select(move => move.Id).OrderBy(id => id, StringComparer.Ordinal)
                .SequenceEqual(new[] { "A", "B", "C" }) is false)
        {
            throw new InvalidOperationException(
                "Alpha boss must define exactly moves A, B and C.");
        }

        foreach (var move in boss.Moves)
        {
            if (move.WindupSeconds <= 0 ||
                move.Coefficient <= 0 ||
                move.RecoverySeconds <= 0 ||
                move.CooldownSeconds <= 0)
            {
                throw new InvalidOperationException(
                    $"Alpha boss move {move.Id} has a non-positive timing/coefficient.");
            }

            // The encounter machine hit-tests each shape, so the geometry the
            // shape needs must be present in the source (never defaulted).
            var missing = move.Shape switch
            {
                "CONE" => move.AngleDegrees is null || move.RangeWu is null,
                "CIRCLE" => move.RadiusWu is null || move.TargetRangeWu is null,
                "ANNULUS" => move.InnerRadiusWu is null || move.OuterRadiusWu is null,
                _ => true
            };
            if (missing)
            {
                throw new InvalidOperationException(
                    $"Alpha boss move {move.Id} shape '{move.Shape}' is missing geometry.");
            }
        }

        var moveC = boss.Moves.Single(move => move.Id == "C");
        if (!string.Equals(moveC.Shape, "ANNULUS", StringComparison.Ordinal) ||
            !string.Equals(moveC.InterruptibleBy, "NONE", StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                "Alpha move C must be the non-interruptible annulus.");
        }

        if (boss.WipeNoAliveTargetSeconds != 10 ||
            !boss.ResetHp ||
            boss.ResetPhase != 1 ||
            !boss.QuestCheckpointPersists ||
            !boss.InvalidateOldCastGeneration ||
            !boss.NoLootOnReset)
        {
            throw new InvalidOperationException(
                "Alpha boss wipe rules do not match the approved decision.");
        }
    }

    private static void ValidateLoot(AlphaLootRules loot)
    {
        if (!string.Equals(loot.CoinMinExpression, "mobLevel", StringComparison.Ordinal) ||
            !string.Equals(loot.CoinMaxExpression, "2*mobLevel", StringComparison.Ordinal) ||
            !loot.InclusiveIntegers)
        {
            throw new InvalidOperationException(
                "Alpha coin band must be inclusive [mobLevel, 2*mobLevel].");
        }

        if (loot.GearRarityWeights.Count != 5 ||
            loot.GearRarityWeights.GetValueOrDefault("COMMON") != 100 ||
            loot.GearRarityWeights.GetValueOrDefault("FINE") != 0 ||
            loot.GearRarityWeights.GetValueOrDefault("SPIRIT") != 0 ||
            loot.GearRarityWeights.GetValueOrDefault("MYSTIC") != 0 ||
            loot.GearRarityWeights.GetValueOrDefault("ANCIENT") != 0)
        {
            throw new InvalidOperationException(
                "Alpha gear vector must be 100% COMMON, not a new rarity chance.");
        }

        if (!loot.RollOnceKey.SequenceEqual(
                new[] { "profileVersion", "characterId", "deathEventId", "lifeId", "groupId" },
                StringComparer.Ordinal) ||
            !loot.NoLiveRerollOnRetry ||
            loot.DefaultGrantEnabled ||
            !loot.BossQuestRewardSeparateFromLoot)
        {
            throw new InvalidOperationException(
                "Alpha loot rules must roll once per death and keep grant OFF.");
        }
    }

    private static void ValidateDeathReturn(
        AlphaDeathReturnRules deathReturn, string mapId, MapBoundsCatalog maps)
    {
        if (!string.Equals(deathReturn.MapId, mapId, StringComparison.Ordinal) ||
            !maps.TryResolve(deathReturn.MapId, out var bounds) ||
            !bounds.Contains(deathReturn.AnchorX, deathReturn.AnchorY) ||
            deathReturn.AnchorX != 18 ||
            deathReturn.AnchorY != 0)
        {
            throw new InvalidOperationException(
                "Alpha death-return anchor must be the approved (18,0) on MAP_BEN_MUA.");
        }

        if (!string.Equals(deathReturn.Route, "POST /p1/actor/death-return",
                StringComparison.Ordinal) ||
            deathReturn.SchemaVersion != 1 ||
            deathReturn.XpPenalty != 0 ||
            deathReturn.CurrencyPenalty != 0 ||
            deathReturn.DurabilityPenalty != 0 ||
            deathReturn.NewDeathReturnCooldownSeconds != 3 ||
            deathReturn.DefaultEnabled)
        {
            throw new InvalidOperationException(
                "Alpha death-return route/penalties/cooldown do not match the decision.");
        }

        if (!deathReturn.Payload.Contains("empty intent", StringComparison.OrdinalIgnoreCase) ||
            !deathReturn.RestoreHp.Contains("0.5", StringComparison.Ordinal) ||
            deathReturn.Clear.Count != 4 ||
            deathReturn.CreditKey.Count != 4)
        {
            throw new InvalidOperationException(
                "Alpha death-return payload/restore/clear/credit keys are incomplete.");
        }
    }
}
