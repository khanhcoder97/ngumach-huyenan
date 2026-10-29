using System.Threading;
using Microsoft.Extensions.Options;
using Server.Health.Contracts;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;
using Server.Health.Gameplay.Inventory;
using Server.Health.Gameplay.Quests;
using Server.Health.Gameplay.Teleport;
using Server.Health.World;

namespace Server.Health.Smoke;

public static class ServiceSelfCheck
{
    private const string PlayerClassId = "CLASS_MINH_KIEM";

    public static int Run(IServiceProvider services, ILogger logger)
    {
        var options = services.GetRequiredService<IOptions<P1WorldOptions>>().Value;
        var maps = services.GetRequiredService<MapBoundsCatalog>();
        var combat = services.GetRequiredService<ICombatService>();
        var combatSkills = services.GetRequiredService<ICombatSkillCatalog>();
        var targets = services.GetRequiredService<InMemoryCombatTargetProvider>();
        var quests = services.GetRequiredService<IQuestService>();
        var questCatalog = services.GetRequiredService<IQuestCatalog>();
        var inventory = services.GetRequiredService<IInventoryService>();
        var teleport = services.GetRequiredService<ITeleportService>();
        var questAccept = services.GetRequiredService<IQuestAcceptService>();
        var npcAnchors = services.GetRequiredService<NpcAnchorCatalog>();
        var questTurnIn = services.GetRequiredService<IQuestTurnInService>();
        var rewardLedger = services.GetRequiredService<RewardLedgerStore>();

        var results = new List<(string Name, bool Passed, string? Detail)>();
        void Check(string name, bool passed, string? detail = null) =>
            results.Add((name, passed, detail));

        PlayerSession NewPlayer(
            string characterId,
            string classId = PlayerClassId,
            int hp = 100,
            int mp = 50) =>
            new(
                $"SES_{Guid.NewGuid():N}",
                characterId,
                classId,
                options.DefaultMapId,
                options.SpawnX,
                options.SpawnY,
                hp,
                options.StartingMaxHp,
                mp,
                options.StartingMaxMp,
                DateTimeOffset.UtcNow);

        Check("combat.catalog", combatSkills.Count == 3, $"count={combatSkills.Count}");

        var combatActor = NewPlayer("CHR_SELFCHECK_COMBAT");
        var badSkill = combat.Resolve(
            combatActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-99" });
        Check(
            "combat.invalid_skill_input",
            badSkill.Failure?.Code == P1ErrorCodes.InvalidPayload,
            badSkill.Failure?.Code);

        var wrongClass = NewPlayer(
            "CHR_SELFCHECK_CLASS", classId: "CLASS_LUYEN_TAM");
        var wrongClassCast = combat.Resolve(
            wrongClass, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.class_gate",
            wrongClassCast.Failure?.Code == CombatErrorCodes.SkillNotAvailable,
            wrongClassCast.Failure?.Code);

        var staleActor = NewPlayer("CHR_SELFCHECK_STALE");
        staleActor.LastInputSequence = 1;
        var staleCast = combat.Resolve(
            staleActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.stale_sequence",
            staleCast.Failure?.Code == P1ErrorCodes.StaleSequence,
            staleCast.Failure?.Code);

        var selfCast = combat.Resolve(
            combatActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.self_cast",
            selfCast.Accepted &&
            selfCast.Event?.Payload.TargetId == combatActor.CharacterId &&
            combatActor.Mp == options.StartingMp - 12 &&
            combatActor.LastInputSequence == 1 &&
            combatActor.Revision == 2,
            $"mp={combatActor.Mp} revision={combatActor.Revision}");

        var cooldownCast = combat.Resolve(
            combatActor, new CombatCommand { AimX = 0, AimY = 0, InputSequence = 2, SkillId = "SK-MK-01" });
        Check(
            "combat.cooldown",
            cooldownCast.Failure?.Code == CombatErrorCodes.CooldownActive,
            cooldownCast.Failure?.Code);

        var missingTarget = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_TARGET"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-03", TargetId = "TGT_MISSING" });
        Check(
            "combat.target_not_found",
            missingTarget.Failure?.Code == CombatErrorCodes.TargetNotFound,
            missingTarget.Failure?.Code);

        targets.Upsert(new CombatTarget(
            "TGT_SELFCHECK_FAR",
            options.DefaultMapId,
            "OVERWORLD",
            options.SpawnX + 50,
            options.SpawnY,
            Alive: true));
        var farCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_RANGE"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-02", TargetId = "TGT_SELFCHECK_FAR" });
        Check(
            "combat.out_of_range",
            farCast.Failure?.Code == CombatErrorCodes.OutOfRange,
            farCast.Failure?.Code);

        var worldTargets = services.GetRequiredService<ICombatTargetProvider>();
        var resolvedMob = worldTargets.TryResolve("ENT_MAN_BM_SPAWN_BM_01", out var mobTarget);
        Check(
            "combat.world_target",
            resolvedMob &&
            mobTarget is { MapId: "MAP_BEN_MUA", FloorId: "OVERWORLD", X: 84, IsAlive: true },
            mobTarget?.EntityId);
        Check(
            "combat.world_target_npc_rejected",
            !worldTargets.TryResolve("ENT_MAN_BM_NPC_LYAN", out _));

        var worldRangeCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_WORLD_RANGE"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-02", TargetId = "ENT_MAN_BM_SPAWN_BM_01" });
        Check(
            "combat.world_target_out_of_range",
            worldRangeCast.Failure?.Code == CombatErrorCodes.OutOfRange,
            worldRangeCast.Failure?.Code);

        var worldConeActor = NewPlayer("CHR_SELFCHECK_WORLD_CONE");
        var worldConeCast = combat.Resolve(
            worldConeActor,
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-03", TargetId = "ENT_MAN_BM_SPAWN_BM_01" });
        Check(
            "combat.world_target_resolves",
            worldConeCast.Accepted && worldConeActor.Mp == 28,
            worldConeCast.Failure?.Code);

        targets.Upsert(new CombatTarget(
            "TGT_SELFCHECK_OTHER_FLOOR",
            options.DefaultMapId,
            "UNDERGROUND",
            options.SpawnX + 1,
            options.SpawnY,
            Alive: true));
        var floorCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_FLOOR"),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-03", TargetId = "TGT_SELFCHECK_OTHER_FLOOR" });
        Check(
            "combat.floor_mismatch",
            floorCast.Failure?.Code == CombatErrorCodes.TargetNotFound,
            floorCast.Failure?.Code);

        var idemActor = NewPlayer("CHR_SELFCHECK_COMBAT_IDEM");
        var idemCommand = new CombatCommand
        {
            AimX = 0,
            AimY = 0,
            InputSequence = 1,
            SkillId = "SK-MK-01"
        };
        var idemFirst = combat.Resolve(idemActor, idemCommand, new string('a', 32));
        var idemReplay = combat.Resolve(idemActor, idemCommand, new string('a', 32));
        Check(
            "combat.idempotency_replay",
            idemFirst.Accepted &&
            idemReplay.Accepted &&
            ReferenceEquals(idemFirst.Event, idemReplay.Event) &&
            idemActor.Mp == 38 &&
            idemActor.Revision == 2,
            $"mp={idemActor.Mp} revision={idemActor.Revision}");

        var idemConflict = combat.Resolve(
            idemActor,
            new CombatCommand
            {
                AimX = 0,
                AimY = 0,
                InputSequence = 2,
                SkillId = "SK-MK-01"
            },
            new string('a', 32));
        Check(
            "combat.idempotency_conflict",
            idemConflict.Failure?.Code == CombatErrorCodes.IdempotencyConflict,
            idemConflict.Failure?.Code);

        

        var noMpCast = combat.Resolve(
            NewPlayer("CHR_SELFCHECK_MP", mp: 0),
            new CombatCommand { AimX = 0, AimY = 0, InputSequence = 1, SkillId = "SK-MK-01" });
        Check(
            "combat.insufficient_resource",
            noMpCast.Failure?.Code == CombatErrorCodes.InsufficientResource,
            noMpCast.Failure?.Code);

        // ─── QOD-16: combat subset domain + entity read-model projection ───

        var configuration = services.GetRequiredService<IConfiguration>();
        var hostEnvironment = services.GetRequiredService<IHostEnvironment>();
        bool Near(double actual, double expected) => Math.Abs(actual - expected) < 1e-9;

        var combatDamage = services.GetRequiredService<CombatDamageFeature>();
        Check(
            "combat.damage_gate_off_by_default",
            !combatDamage.Enabled,
            $"enabled={combatDamage.Enabled}");
        var gateBlockedLoad = false;
        try
        {
            _ = combatDamage.MobStats;
        }
        catch (InvalidOperationException)
        {
            gateBlockedLoad = true;
        }

        Check("combat.damage_gate_blocks_load", gateBlockedLoad);

        var enabledCombat = new CombatDamageFeature(
            new P1CombatDamageOptions { Enabled = true },
            configuration,
            hostEnvironment);

        combatSkills.TryGet("SK-MK-01", out var mk01);
        combatSkills.TryGet("SK-MK-02", out var mk02);
        combatSkills.TryGet("SK-MK-03", out var mk03);
        Check(
            "combat.skill_coefficients",
            mk01 is
            {
                TargetingType: CombatTargetingTypes.Self,
                RangeWu: 4.4,
                AngleDegrees: 120,
                MaxTargets: 1,
                TelegraphSeconds: 0.4,
                VfxKey: "VFX/Skill/SK-MK-01"
            } &&
            mk01.Coefficients is { Pve: 1.8, Boss: 1.8, Pvp: 0.65 } &&
            mk02 is
            {
                TargetingType: CombatTargetingTypes.Dash,
                RangeWu: 11,
                AngleDegrees: null,
                MaxTargets: 1,
                TelegraphSeconds: 0.15,
                VfxKey: "VFX/Skill/SK-MK-02"
            } &&
            mk02.Coefficients is { Pve: 1.5, Boss: 1.5, Pvp: 0.65 } &&
            mk03 is
            {
                TargetingType: CombatTargetingTypes.Cone,
                RangeWu: null,
                AngleDegrees: 100,
                MaxTargets: 5,
                TelegraphSeconds: 0.1,
                VfxKey: "VFX/Skill/SK-MK-03"
            } &&
            mk03.Coefficients is { Pve: 1.9, Boss: 1.9, Pvp: 0.65 },
            $"{mk01?.SkillId}/{mk02?.SkillId}/{mk03?.SkillId}");

        var rangeMigration = enabledCombat.RangeMigration;
        Check(
            "combat.skill_range_migration",
            Near(rangeMigration.RangeWuBySkillId["SK-MK-01"], 4.4) &&
            Near(rangeMigration.RangeWuBySkillId["SK-MK-02"], 11.0) &&
            Near(rangeMigration.RangeWuBySkillId["SK-MK-03"], 4.4),
            string.Join(
                ",",
                rangeMigration.RangeWuBySkillId
                    .OrderBy(pair => pair.Key, StringComparer.Ordinal)
                    .Select(pair => $"{pair.Key}={pair.Value}")));

        var mobStats = enabledCombat.MobStats;
        Check(
            "combat.mob_stats_bundle",
            mobStats is
            {
                SchemaVersion: 1,
                BundleId: "COMBAT_MOB_STATS_V1",
                Activation: CombatMobStatLoader.DesignOnlyActivation,
                ReferenceLevel: 5,
                LevelPolicy: "REFERENCE_L5"
            } &&
            mobStats.Archetypes.Count == 3 &&
            mobStats.Bosses.Count == 1,
            $"bundle={mobStats.BundleId} archetypes={mobStats.Archetypes.Count}");

        Check(
            "combat.mob_stats_elite_multipliers",
            mobStats.Elite is { Hp: 6.0, Attack: 1.6, Defense: 1.8 },
            $"{mobStats.Elite.Hp}/{mobStats.Elite.Attack}/{mobStats.Elite.Defense}");

        var carpling = mobStats.Archetypes.First(stats => stats.MobId == "MOB_CARPLING");
        Check(
            "combat.mob_stats_carpling_l5",
            carpling.ReferenceLevel5 is { Hp: 192, Attack: 15, Defense: 4.2 },
            $"{carpling.ReferenceLevel5.Hp}/{carpling.ReferenceLevel5.Attack}/{carpling.ReferenceLevel5.Defense}");

        var shoreStalker = mobStats.Archetypes.First(stats => stats.MobId == "MOB_SHORE_STALKER");
        Check(
            "combat.mob_stats_shore_stalker_l5",
            shoreStalker.ReferenceLevel5 is { Hp: 216, Attack: 23, Defense: 4.8 },
            $"{shoreStalker.ReferenceLevel5.Hp}/{shoreStalker.ReferenceLevel5.Attack}/{shoreStalker.ReferenceLevel5.Defense}");

        var mangCot = mobStats.Bosses.Single();
        Check(
            "combat.mob_stats_boss_blocked",
            mangCot is
            {
                BossId: "BOSS_MANG_COT",
                HpMultiplier: 35,
                AttackMultiplier: 2.0,
                PartyHpMultiplierPerAdditionalPlayer: 0.65,
                ReferenceLevel: 10,
                Activation: "BOSSDATA_BLOCKED"
            } &&
            mangCot.ReferenceStats is { Hp: 12600, Attack: 60, Defense: 10 } &&
            mangCot.Attacks.Count == 3 &&
            mangCot.BlockedReason.Length > 0,
            $"activation={mangCot.Activation} attacks={mangCot.Attacks.Count}");

        var carplingL6 = CombatMobStatLoader.EffectiveAt(mobStats, "MOB_CARPLING", 6);
        Check(
            "combat.mob_stats_level_formula",
            carplingL6.Hp == 211 &&
            Near(carplingL6.Attack, 16.5) &&
            Near(carplingL6.Defense, 4.76),
            $"{carplingL6.Hp}/{carplingL6.Attack}/{carplingL6.Defense}");

        Check(
            "damage.oracle_raw",
            Near(DamageFormula.RawDamage(20, 0, 1.5, 1, 0), 30),
            $"{DamageFormula.RawDamage(20, 0, 1.5, 1, 0)}");

        var oracleMitigation = DamageFormula.MitigationMultiplier(10);
        Check(
            "damage.oracle_noncrit",
            DamageFormula.FinalDamage(30, oracleMitigation, 1, 1, 1) == 27,
            $"{DamageFormula.FinalDamage(30, oracleMitigation, 1, 1, 1)}");
        Check(
            "damage.oracle_crit",
            DamageFormula.FinalDamage(30, oracleMitigation, 1, DamageFormula.CritMultiplier, 1) == 40,
            $"{DamageFormula.FinalDamage(30, oracleMitigation, 1, DamageFormula.CritMultiplier, 1)}");
        Check("damage.armor_zero", Near(DamageFormula.MitigationMultiplier(0), 1));
        Check(
            "damage.reduction_cap",
            Near(DamageFormula.DamageReductionMultiplier(0.9), 0.2),
            $"{DamageFormula.DamageReductionMultiplier(0.9)}");
        Check(
            "damage.resist_pve_cap",
            Near(DamageFormula.ElementMultiplier(0.7, pvp: false), 0.5) &&
            Near(DamageFormula.ElementMultiplier(0.7, pvp: true), 0.7),
            $"{DamageFormula.ElementMultiplier(0.7, pvp: false)}/{DamageFormula.ElementMultiplier(0.7, pvp: true)}");
        Check(
            "damage.final_min_one",
            DamageFormula.FinalDamage(0.001, 1, 1, 1, 1) == 1);
        Check(
            "damage.hit_clamp",
            Near(DamageFormula.HitProbability(1, 0), 0.98) &&
            Near(DamageFormula.HitProbability(0, 1), 0.05),
            $"{DamageFormula.HitProbability(1, 0)}/{DamageFormula.HitProbability(0, 1)}");
        Check(
            "damage.attribute_derived",
            Near(DamageFormula.AttributeCritChance(5, 0, 1), 0.0525) &&
            Near(DamageFormula.AttributeAccuracy(5, 0), 0.0025) &&
            Near(DamageFormula.AttributeDodge(5, 0, 1), 0.0015));

        var rngSameSeed = CombatRng.Uniform01("CAST_1", "TGT_1", 0);
        var rngRepeat = CombatRng.Uniform01("CAST_1", "TGT_1", 0);
        var rngNextHit = CombatRng.Uniform01("CAST_1", "TGT_1", 1);
        Check(
            "damage.rng_deterministic",
            rngSameSeed == rngRepeat &&
            rngNextHit != rngSameSeed &&
            rngSameSeed is >= 0 and < 1,
            $"hit0={rngSameSeed} hit1={rngNextHit}");

        var registry = services.GetRequiredService<WorldEntityRegistry>();
        var projection = services.GetRequiredService<WorldEntityProjectionService>();
        var projectedGateOff = projection.Project();
        Check(
            "projection.all_entities",
            projectedGateOff.Count == registry.Count && registry.Count == 27,
            $"projected={projectedGateOff.Count} registry={registry.Count}");

        var mobGateOff = projectedGateOff.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_01");
        Check(
            "projection.mob_zero_when_gate_off",
            mobGateOff is { Kind: WorldEntityKinds.Mob, Hp: 0, MaxHp: 0, LifeId: 1 },
            $"hp={mobGateOff.Hp}");

        var enabledProjection = new WorldEntityProjectionService(
            registry,
            services.GetRequiredService<MobLifecycleService>(),
            enabledCombat);
        var projected = enabledProjection.Project();

        var npcLyan = projected.First(entity => entity.EntityId == "ENT_MAN_BM_NPC_LYAN");
        Check(
            "projection.npc_invulnerable",
            npcLyan is
            {
                Kind: WorldEntityKinds.Npc,
                Hp: 0,
                MaxHp: 0,
                LifeId: 1,
                Revision: 1,
                State: WorldEntityStates.Active
            },
            $"hp={npcLyan.Hp} state={npcLyan.State}");

        var spawn01 = projected.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_01");
        Check(
            "projection.mob_reference_stats",
            spawn01 is
            {
                Kind: WorldEntityKinds.Mob,
                Hp: 192,
                MaxHp: 192,
                LifeId: 1,
                State: MobBehaviorStates.Idle
            },
            $"hp={spawn01.Hp} state={spawn01.State}");

        var spawn07 = projected.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_07");
        Check(
            "projection.elite_stats",
            spawn07 is { Kind: WorldEntityKinds.Mob, Hp: 1296, MaxHp: 1296 },
            $"hp={spawn07.Hp}");

        var bossSpawn = projected.First(entity => entity.EntityId == "ENT_MAN_BM_SPAWN_BM_05_QUEST");
        Check(
            "projection.boss_zero_blocked",
            bossSpawn is { Kind: WorldEntityKinds.Boss, Hp: 0, MaxHp: 0 },
            $"hp={bossSpawn.Hp}");

        var lifeIdClock = new ManualServerClock(DateTimeOffset.UtcNow);
        var lifeIdRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [MakeFixtureNode("ENT_SELFCHECK_LIFEID_NODE", "MAN-BM-NODE_BM_ORE_01", 21, 60)]),
            lifeIdClock);
        var lifeIdProjection = new WorldEntityProjectionService(
            lifeIdRegistry,
            services.GetRequiredService<MobLifecycleService>(),
            enabledCombat);
        lifeIdRegistry.Despawn("ENT_SELFCHECK_LIFEID_NODE");
        lifeIdClock.Advance(TimeSpan.FromSeconds(60));
        lifeIdRegistry.Update();
        var lifeIdProjected = lifeIdProjection.Project().Single();
        Check(
            "projection.life_id_bump",
            lifeIdProjected is
            {
                State: WorldEntityStates.Available,
                Revision: 3,
                LifeId: 2,
                Hp: 0
            },
            $"state={lifeIdProjected.State} revision={lifeIdProjected.Revision} lifeId={lifeIdProjected.LifeId}");

        Check("quest.catalog", questCatalog.Count == 1, $"count={questCatalog.Count}");
        Check(
            "quest.catalog_ids",
            questCatalog.QuestIds.SequenceEqual(new[] { "P00-01" }, StringComparer.Ordinal),
            string.Join(",", questCatalog.QuestIds));

        var questActor = NewPlayer("CHR_SELFCHECK_QUEST");
        var questInitial = quests.GetState(questActor.CharacterId, "P00-01");
        Check(
            "quest.initial_available",
            questInitial.State?.State == QuestStates.Available,
            questInitial.State?.State);

        var questAccepted = quests.Accept(questActor, "P00-01");
        Check(
            "quest.accept",
            questAccepted.Accepted && questAccepted.State?.State == QuestStates.Active,
            questAccepted.State?.State);

        var eventP1 = new string('a', 32);
        var eventP2 = new string('b', 32);
        var eventP3 = new string('c', 32);

        var progress1 = quests.RecordVerifiedEvent(
            questActor, eventP1, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_01", options.DefaultMapId);
        var progress2 = quests.RecordVerifiedEvent(
            questActor, eventP2, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_02", options.DefaultMapId);
        var progress3 = quests.RecordVerifiedEvent(
            questActor, eventP3, QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_03", options.DefaultMapId);
        Check(
            "quest.ready_to_turn_in",
            progress1.SingleOrDefault() is { State: QuestStates.Active, Revision: 3 } p1 &&
            p1.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 1 &&
            progress2.SingleOrDefault() is { State: QuestStates.Active, Revision: 4 } &&
            progress3.SingleOrDefault() is { State: QuestStates.ReadyToTurnIn, Revision: 5 } p3 &&
            p3.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3,
            progress3.SingleOrDefault()?.State);

        var duplicateProgress = quests.RecordVerifiedEvent(
            questActor, new string('d', 32), QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_01", options.DefaultMapId);
        Check(
            "quest.distinct_record_dedupe",
            duplicateProgress.Count == 0,
            duplicateProgress.Count.ToString());

        var inactiveActor = NewPlayer("CHR_SELFCHECK_QUEST_IDLE");
        var inactiveProgress = quests.RecordVerifiedEvent(
            inactiveActor, new string('e', 32), QuestProgressEventTypes.InteractClaim,
            "MAN-BM-OBJ_BM_PACKAGE_01", options.DefaultMapId);
        Check(
            "quest.progress_ignored_when_inactive",
            inactiveProgress.Count == 0,
            inactiveProgress.Count.ToString());

        var questCompleted = quests.TurnIn(questActor, "P00-01");
        Check(
            "quest.completed",
            questCompleted.State?.State == QuestStates.Completed,
            questCompleted.State?.State);

        var reAccept = quests.Accept(questActor, "P00-01");
        Check(
            "quest.invalid_transition",
            reAccept.Failure?.Code == QuestErrorCodes.InvalidTransition,
            reAccept.Failure?.Code);

        var unknownQuest = quests.GetState(questActor.CharacterId, "P99-99");
        Check(
            "quest.unknown_quest",
            unknownQuest.Failure?.Code == QuestErrorCodes.UnknownQuest,
            unknownQuest.Failure?.Code);

        Check(
            "npc.registry",
            npcAnchors.Count > 0 &&
            npcAnchors.TryResolve("NPC_LYAN", options.DefaultMapId, out var lyanAnchor) &&
            lyanAnchor.X == 42 &&
            lyanAnchor.Y == 0,
            $"count={npcAnchors.Count}");

        var worldEntities = services.GetRequiredService<WorldEntityRegistry>();
        Check("world.registry", worldEntities.Count == 27, $"count={worldEntities.Count}");

        var npcEntity = worldEntities.TryGet("ENT_MAN_BM_NPC_LYAN", out var foundNpc)
            ? foundNpc
            : null;
        Check(
            "world.npc_entity",
            npcEntity is { Kind: WorldEntityKinds.Npc, State: WorldEntityStates.Active } &&
            npcEntity.X == 42 &&
            npcEntity.Y == 0,
            npcEntity?.Kind);

        var mobEntity = worldEntities.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var foundMob)
            ? foundMob
            : null;
        Check(
            "world.mob_entity",
            mobEntity is
            {
                Kind: WorldEntityKinds.Mob,
                State: WorldEntityStates.Alive,
                Quantity: 3,
                RespawnSeconds: 18
            } &&
            mobEntity.X == 84,
            mobEntity?.Kind);

        var worldCatalog = services.GetRequiredService<WorldEntityCatalog>();
        var manualClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 0, 0, 0, TimeSpan.Zero));
        var manualWorld = new WorldEntityRegistry(worldCatalog, manualClock);

        Check("world.despawn_unknown", !manualWorld.Despawn("ENT_MISSING"));

        var despawned = manualWorld.Despawn("ENT_MAN_BM_SPAWN_BM_01") &&
                        manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var deadMob) &&
                        deadMob.State == WorldEntityStates.Dead &&
                        deadMob.Revision == 2;
        Check("world.despawn_mob", despawned);

        var beforeRespawn = manualWorld.Update();
        Check(
            "world.respawn_wait",
            beforeRespawn == 0 &&
            manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var waitingMob) &&
            waitingMob.State == WorldEntityStates.Dead,
            $"respawned={beforeRespawn}");

        manualClock.Advance(TimeSpan.FromSeconds(18));
        var respawned = manualWorld.Update();
        Check(
            "world.respawn",
            respawned == 1 &&
            manualWorld.TryGet("ENT_MAN_BM_SPAWN_BM_01", out var revivedMob) &&
            revivedMob.State == WorldEntityStates.Alive &&
            revivedMob.Revision == 3,
            $"respawned={respawned}");

        Check("world.despawn_npc_rejected", !manualWorld.Despawn("ENT_MAN_BM_NPC_LYAN"));

        var nodeCleared = manualWorld.Despawn("ENT_MAN_BM_NODE_BM_ORE_01") &&
                          manualWorld.TryGet("ENT_MAN_BM_NODE_BM_ORE_01", out var node) &&
                          node.State == WorldEntityStates.Depleted;
        Check("world.node_lifecycle", nodeCleared);

        var startNpcOk = questCatalog.TryGet("P00-01", out var p0001) &&
                         string.Equals(p0001.StartNpcId, "NPC_LYAN", StringComparison.Ordinal);
        Check("quest.start_npc", startNpcOk, p0001?.StartNpcId);

        var accepter = NewPlayer("CHR_SELFCHECK_ACCEPT");
        accepter.X = 42;
        accepter.Y = 0;
        var accepted = questAccept.Accept(
            accepter, "P00-01", "NPC_LYAN", new string('a', 32));
        Check(
            "quest_accept.success",
            accepted.Accepted &&
            accepted.State?.State == QuestStates.Active &&
            accepted.State.Revision == 2,
            accepted.Failure?.Code ?? $"state={accepted.State?.State}");

        var replayed = questAccept.Accept(
            accepter, "P00-01", "NPC_LYAN", new string('a', 32));
        Check(
            "quest_accept.replay",
            replayed.Accepted && replayed.State?.Revision == 2,
            replayed.Failure?.Code);

        var keyConflict = questAccept.Accept(
            accepter, "P00-01", "NPC_TA_VAN_KHANH", new string('a', 32));
        Check(
            "quest_accept.idempotency_conflict",
            keyConflict.Failure?.Code == QuestAcceptErrorCodes.IdempotencyConflict,
            keyConflict.Failure?.Code);

        var secondAccept = questAccept.Accept(
            accepter, "P00-01", "NPC_LYAN", new string('b', 32));
        Check(
            "quest_accept.invalid_transition",
            secondAccept.Failure?.Code == QuestErrorCodes.InvalidTransition,
            secondAccept.Failure?.Code);

        var farActor = NewPlayer("CHR_SELFCHECK_ACCEPT_FAR");
        var tooFar = questAccept.Accept(
            farActor, "P00-01", "NPC_LYAN", new string('c', 32));
        Check(
            "quest_accept.out_of_range",
            tooFar.Failure?.Code == QuestAcceptErrorCodes.OutOfRange && tooFar.Failure.Retryable,
            tooFar.Failure?.Code);

        var wrongNpc = questAccept.Accept(
            NewPlayer("CHR_SELFCHECK_ACCEPT_NPC"),
            "P00-01", "NPC_TA_VAN_KHANH", new string('d', 32));
        Check(
            "quest_accept.npc_mismatch",
            wrongNpc.Failure?.Code == QuestAcceptErrorCodes.NpcMismatch,
            wrongNpc.Failure?.Code);

        var highLevel = NewPlayer("CHR_SELFCHECK_ACCEPT_LEVEL");
        highLevel.X = 42;
        highLevel.Level = 11;
        var levelGate = questAccept.Accept(
            highLevel, "P00-01", "NPC_LYAN", new string('e', 32));
        Check(
            "quest_accept.level_band",
            levelGate.Failure?.Code == QuestAcceptErrorCodes.PrerequisiteNotMet,
            levelGate.Failure?.Code);

        var missingQuest = questAccept.Accept(
            NewPlayer("CHR_SELFCHECK_ACCEPT_UNKNOWN"),
            "P99-99", "NPC_LYAN", new string('f', 32));
        Check(
            "quest_accept.unknown_quest",
            missingQuest.Failure?.Code == QuestErrorCodes.QuestNotFound,
            missingQuest.Failure?.Code);

        MapPolygon Rect(double x1, double y1, double x2, double y2) =>
            new("OVERWORLD",
            [
                new TopologyPoint(x1, y1),
                new TopologyPoint(x2, y1),
                new TopologyPoint(x2, y2),
                new TopologyPoint(x1, y2)
            ]);

        maps.TryResolve(options.DefaultMapId, out var topologyBounds);
        var reviewedTopology = new MapTopologyBundle
        {
            MapId = options.DefaultMapId,
            LayoutVersion = 1,
            BundleVersion = 2,
            ReviewState = TopologyReviewStates.Reviewed,
            IsReviewed = true,
            Bounds = topologyBounds,
            FloorIds = ["OVERWORLD"],
            WalkablePolygons = [Rect(30, -10, 60, 10)],
            BlockedPolygons = [Rect(45, -10, 46, 10), Rect(52, 2, 54, 4)],
            Placements = [new TopologyPlacement(
                "MAN-BM-NPC_LYAN", "NPC_LYAN", "OVERWORLD", 42, 0)]
        };
        var geometry = new WorldGeometryService(
            new WorldGeometryCatalog([reviewedTopology]));

        var clearLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 35, 0, 42, 0);
        Check("los.clear", clearLine.Status == LineOfSightStatus.Allowed, clearLine.Reason);

        var wallLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 50, 0, 42, 0);
        Check("los.wall", wallLine.Status == LineOfSightStatus.Blocked, wallLine.Reason);

        var endpointInWall = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 45.5, 0, 42, 0);
        Check(
            "los.endpoint_in_wall",
            endpointInWall.Status == LineOfSightStatus.Blocked,
            endpointInWall.Reason);

        var holeLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 50, 3, 56, 3);
        Check("los.hole", holeLine.Status == LineOfSightStatus.Blocked, holeLine.Reason);

        var cornerLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 50, 4, 58, 4);
        Check(
            "los.corner_touch",
            cornerLine.Status == LineOfSightStatus.Blocked,
            cornerLine.Reason);

        var sweepClear = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 35, 0, 38, 0, 0.6);
        Check("sweep.clear", sweepClear.Status == LineOfSightStatus.Allowed, sweepClear.Reason);

        var sweepWall = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 46.5, 0, 42, 0, 0.6);
        Check("sweep.wall", sweepWall.Status == LineOfSightStatus.Blocked, sweepWall.Reason);

        var sweepBigStep = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 35, 0, 50, 0, 0.6);
        Check(
            "sweep.big_step",
            sweepBigStep.Status == LineOfSightStatus.Blocked,
            sweepBigStep.Reason);

        var sweepHole = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 3, 56, 3, 0.6);
        Check("sweep.hole", sweepHole.Status == LineOfSightStatus.Blocked, sweepHole.Reason);

        var sweepCorner = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 4, 58, 4, 0.6);
        Check(
            "sweep.corner_touch",
            sweepCorner.Status == LineOfSightStatus.Blocked,
            sweepCorner.Reason);

        var sweepFloor = geometry.CheckWalkSegment(
            options.DefaultMapId, "UNDERGROUND", 35, 0, 38, 0, 0.6);
        Check("sweep.floor", sweepFloor.Status == LineOfSightStatus.Blocked, sweepFloor.Reason);

        var sweepNonfiniteRadius = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 35, 0, 38, 0, double.NaN);
        Check(
            "sweep.nonfinite_radius",
            sweepNonfiniteRadius.Status == LineOfSightStatus.Blocked,
            sweepNonfiniteRadius.Reason);

        var sweepFootprint = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 4.5, 58, 4.5, 0.6);
        Check(
            "sweep.footprint_blocked",
            sweepFootprint.Status == LineOfSightStatus.Blocked &&
            sweepFootprint.Reason == "footprint",
            sweepFootprint.Reason);

        var sweepNarrow = geometry.CheckWalkSegment(
            options.DefaultMapId, "OVERWORLD", 50, 4.5, 58, 4.5, 0.1);
        Check(
            "sweep.footprint_small_allowed",
            sweepNarrow.Status == LineOfSightStatus.Allowed,
            sweepNarrow.Reason);

        var floorLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "UNDERGROUND", 35, 0, 42, 0);
        Check("los.floor", floorLine.Status == LineOfSightStatus.Blocked, floorLine.Reason);

        var nonfiniteLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", double.NaN, 0, 42, 0);
        Check(
            "los.nonfinite",
            nonfiniteLine.Status == LineOfSightStatus.Blocked,
            nonfiniteLine.Reason);

        var outsideLine = geometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 20, 0, 42, 0);
        Check(
            "los.outside_walkable",
            outsideLine.Status == LineOfSightStatus.Blocked,
            outsideLine.Reason);

        var shippedGeometry = services.GetRequiredService<IWorldGeometryService>();
        var notEnforced = shippedGeometry.CheckLineOfSight(
            options.DefaultMapId, "OVERWORLD", 35, 0, 42, 0);
        Check(
            "los.not_enforced_without_reviewed_bundle",
            notEnforced.Status == LineOfSightStatus.NotEnforced,
            notEnforced.Reason?.ToString());

        WorldEntityInstance MakeFixtureMob(string entityId, double x, double y)
        {
            var mob = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-TEST-" + entityId,
                Kind = WorldEntityKinds.Mob,
                TemplateIds = new[] { "MOB_CARPLING" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = y,
                Quantity = 1,
                RespawnSeconds = 18
            };
            mob.Initialize();
            return mob;
        }

        var mobClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 1, 0, 0, TimeSpan.Zero));
        var mobOptions = new MobBehaviorOptions
        {
            AggroRadiusWu = 6,
            LeashRadiusWu = 12,
            AttackRangeWu = 1.2,
            AttackCooldownSeconds = 2,
            MoveSpeedWuPerSecond = 2
        };
        var mobRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_MOB", 43, 0)]),
            mobClock);
        var mobAi = new MobLifecycleService(mobRegistry, geometry, mobOptions, mobClock);
        var prey = NewPlayer("CHR_SELFCHECK_PREY");
        prey.X = 44;
        prey.Y = 0;

        mobAi.Tick([prey]);
        Check(
            "mob.aggro",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Aggro,
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        mobClock.Advance(TimeSpan.FromSeconds(0.5));
        var attackTick = mobAi.Tick([prey]);
        var attackEvents = attackTick.Count(
            lifecycle => lifecycle.FromState == MobBehaviorStates.Attack &&
                         lifecycle.ToState == MobBehaviorStates.Attack);
        Check(
            "mob.attack",
            mobAi.GetState("ENT_SELFCHECK_MOB") == MobBehaviorStates.Attack &&
            attackEvents == 1,
            mobAi.GetState("ENT_SELFCHECK_MOB"));

        mobClock.Advance(TimeSpan.FromSeconds(0.5));
        var cooldownTick = mobAi.Tick([prey]);
        Check(
            "mob.attack_cooldown",
            cooldownTick.All(lifecycle =>
                lifecycle.FromState != MobBehaviorStates.Attack ||
                lifecycle.ToState != MobBehaviorStates.Attack),
            "attack fired during cooldown");

        var wallClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 2, 0, 0, TimeSpan.Zero));
        var wallRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_WALL_MOB", 43, 0)]),
            wallClock);
        var wallAi = new MobLifecycleService(wallRegistry, geometry, mobOptions, wallClock);
        var blockedPrey = NewPlayer("CHR_SELFCHECK_BLOCKED_PREY");
        blockedPrey.X = 47.5;
        blockedPrey.Y = 0;
        wallAi.Tick([blockedPrey]);
        Check(
            "mob.los_blocks_aggro",
            wallAi.GetState("ENT_SELFCHECK_WALL_MOB") == MobBehaviorStates.Idle,
            wallAi.GetState("ENT_SELFCHECK_WALL_MOB"));

        var leashOptions = new MobBehaviorOptions
        {
            AggroRadiusWu = 20,
            LeashRadiusWu = 12,
            AttackRangeWu = 1.2,
            AttackCooldownSeconds = 2,
            MoveSpeedWuPerSecond = 2
        };
        var leashClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 3, 0, 0, TimeSpan.Zero));
        var leashRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_LEASH_MOB", 32, 0)]),
            leashClock);
        var leashAi = new MobLifecycleService(
            leashRegistry, geometry, leashOptions, leashClock);
        var farPrey = NewPlayer("CHR_SELFCHECK_FAR_PREY");
        farPrey.X = 44.5;
        farPrey.Y = 0;
        leashAi.Tick([farPrey]);
        Check(
            "mob.leash_return",
            leashAi.GetState("ENT_SELFCHECK_LEASH_MOB") == MobBehaviorStates.Return,
            leashAi.GetState("ENT_SELFCHECK_LEASH_MOB"));

        var floorPrey = NewPlayer("CHR_SELFCHECK_FLOOR_PREY");
        floorPrey.X = 44;
        floorPrey.Y = 0;
        floorPrey.FloorId = "UNDERGROUND";
        var floorClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 4, 0, 0, TimeSpan.Zero));
        var floorRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog([], [MakeFixtureMob("ENT_SELFCHECK_FLOOR_MOB", 43, 0)]),
            floorClock);
        var floorAi = new MobLifecycleService(floorRegistry, geometry, mobOptions, floorClock);
        floorAi.Tick([floorPrey]);
        Check(
            "mob.floor_ignored",
            floorAi.GetState("ENT_SELFCHECK_FLOOR_MOB") == MobBehaviorStates.Idle,
            floorAi.GetState("ENT_SELFCHECK_FLOOR_MOB"));

        var losAccept = new InMemoryQuestAcceptService(
            questCatalog, quests, npcAnchors, geometry,
            services.GetRequiredService<QuestAcceptOptions>());

        var blockedActor = NewPlayer("CHR_SELFCHECK_LOS_BLOCKED");
        blockedActor.X = 46.5;
        blockedActor.Y = 0;
        var blockedAccept = losAccept.Accept(
            blockedActor, "P00-01", "NPC_LYAN", new string('1', 31) + "0");
        Check(
            "quest_accept.los_blocked",
            blockedAccept.Failure?.Code == QuestAcceptErrorCodes.OutOfRange &&
            blockedAccept.Failure.Retryable,
            blockedAccept.Failure?.Code);

        var blockedState = quests.GetState(blockedActor.CharacterId, "P00-01").State;
        Check(
            "quest_accept.los_blocked_state",
            blockedState is { State: QuestStates.Available, Revision: 1 },
            blockedState?.State);

        var clearActor = NewPlayer("CHR_SELFCHECK_LOS_CLEAR");
        clearActor.X = 38;
        clearActor.Y = 0;
        var clearAccept = losAccept.Accept(
            clearActor, "P00-01", "NPC_LYAN", new string('2', 31) + "0");
        Check(
            "quest_accept.los_allowed",
            clearAccept.Accepted && clearAccept.State?.State == QuestStates.Active,
            clearAccept.Failure?.Code);

        var worldRecords = services.GetRequiredService<WorldRecordCatalog>();
        Check("world.records", worldRecords.Count == 352, $"count={worldRecords.Count}");
        Check(
            "world.records_resolve_target",
            worldRecords.TryResolveTarget("OBJ_BM_PACKAGE_01", options.DefaultMapId, out var packageRecord) &&
            packageRecord.RecordId == "MAN-BM-OBJ_BM_PACKAGE_01" &&
            packageRecord.RecordType == WorldEntityKinds.Interactable &&
            worldRecords.TryResolveTarget(
                "MAN-BM-OBJ_BM_PACKAGE_02", options.DefaultMapId, out _),
            packageRecord?.RecordId);

        WorldEntityInstance MakeFixtureInteractable(
            string entityId,
            string recordId,
            double x,
            int respawnSeconds,
            string claimPolicy = WorldEntityClaimPolicies.Shared)
        {
            var interactable = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = recordId,
                Kind = WorldEntityKinds.Interactable,
                TemplateIds = new[] { "OBJ_BM_PACKAGE_01" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = respawnSeconds,
                ClaimPolicy = claimPolicy
            };
            interactable.Initialize();
            return interactable;
        }

        WorldEntityInstance MakeFixtureNpc(string entityId)
        {
            var npc = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = "MAN-BM-NPC_LYAN",
                Kind = WorldEntityKinds.Npc,
                TemplateIds = new[] { "NPC_LYAN" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = 42,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = 0
            };
            npc.Initialize();
            return npc;
        }

        var interactClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 5, 0, 0, TimeSpan.Zero));
        var interactRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG_1", "MAN-BM-OBJ_BM_PACKAGE_01", 36, 20),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG_2", "MAN-BM-OBJ_BM_PACKAGE_02", 44, 20),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG_3", "MAN-BM-OBJ_BM_PACKAGE_03", 52, 20),
                    MakeFixtureNpc("ENT_SELFCHECK_NPC")
                ]),
            interactClock);
        var interactStates = new InMemoryQuestStateStore();
        var interactQuests = new InMemoryQuestService(
            questCatalog, interactStates, worldRecords, interactClock);
        var interactInventory = new InMemoryInventoryService(new InMemoryInventoryStateStore());
        var fixedRoller = new FixedYieldRoller(2);
        var interactOptions = new InteractionOptions
        {
            Enabled = true,
            MaxInteractionDistanceWu = 5,
            AssumedProfessionLevel = 1
        };
        var interactions = new InMemoryInteractionService(
            interactRegistry,
            worldRecords,
            interactQuests,
            interactInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var interactActor = NewPlayer("CHR_SELFCHECK_INTERACT");
        interactActor.X = 36;
        interactActor.Y = 0;
        var interactAccepted = interactQuests.Accept(interactActor, "P00-01");
        Check(
            "interact.quest_accepted",
            interactAccepted.Accepted && interactAccepted.State?.State == QuestStates.Active,
            interactAccepted.Failure?.Code);

        var badTargetShape = interactions.Interact(
            interactActor, "not-an-entity", new string('0', 32));
        Check(
            "interact.invalid_payload",
            badTargetShape.Failure?.Code == P1ErrorCodes.InvalidPayload,
            badTargetShape.Failure?.Code);

        var missingInteractTarget = interactions.Interact(
            interactActor, "ENT_SELFCHECK_MISSING", new string('1', 31) + "a");
        Check(
            "interact.target_not_found",
            missingInteractTarget.Failure?.Code == InteractionErrorCodes.TargetNotFound,
            missingInteractTarget.Failure?.Code);

        var npcTarget = interactions.Interact(
            interactActor, "ENT_SELFCHECK_NPC", new string('1', 31) + "b");
        Check(
            "interact.invalid_target",
            npcTarget.Failure?.Code == InteractionErrorCodes.InvalidTarget,
            npcTarget.Failure?.Code);

        var collect1 = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_1", new string('1', 31) + "c");
        Check(
            "interact.collect_package",
            collect1.Accepted &&
            collect1.Result is
            {
                Kind: WorldEntityKinds.Interactable,
                Outcome: "collected",
                TargetState: WorldEntityStates.Depleted,
                RecordId: "MAN-BM-OBJ_BM_PACKAGE_01",
                Yield: null,
                RespawnAtUtc: not null
            } &&
            collect1.Result.QuestUpdates.SingleOrDefault() is
            {
                State: QuestStates.Active,
                Revision: 3
            } collect1Quest &&
            collect1Quest.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 1,
            collect1.Failure?.Code ?? collect1.Result?.TargetState);

        var collect1Replay = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_1", new string('1', 31) + "c");
        Check(
            "interact.idempotency_replay",
            collect1Replay.Accepted && ReferenceEquals(collect1Replay.Result, collect1.Result),
            collect1Replay.Failure?.Code);

        var collectConflict = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_2", new string('1', 31) + "c");
        Check(
            "interact.idempotency_conflict",
            collectConflict.Failure?.Code == InteractionErrorCodes.IdempotencyConflict,
            collectConflict.Failure?.Code);

        var collectDepleted = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_1", new string('1', 31) + "d");
        Check(
            "interact.target_depleted",
            collectDepleted.Failure?.Code == InteractionErrorCodes.TargetNotAvailable,
            collectDepleted.Failure?.Code);

        var farInteractor = NewPlayer("CHR_SELFCHECK_INTERACT_FAR");
        var farCollect = interactions.Interact(
            farInteractor, "ENT_SELFCHECK_PKG_3", new string('1', 31) + "e");
        Check(
            "interact.out_of_range",
            farCollect.Failure is
            {
                Code: InteractionErrorCodes.OutOfRange,
                Retryable: true
            },
            farCollect.Failure?.Code);

        interactActor.X = 44;
        var collect2 = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_2", new string('2', 31) + "a");
        Check(
            "interact.collect_second",
            collect2.Accepted &&
            collect2.Result!.QuestUpdates.SingleOrDefault() is
            {
                State: QuestStates.Active,
                Revision: 4
            },
            collect2.Failure?.Code);

        interactActor.X = 52;
        var collect3 = interactions.Interact(
            interactActor, "ENT_SELFCHECK_PKG_3", new string('3', 31) + "a");
        Check(
            "interact.ready_to_turn_in",
            collect3.Accepted &&
            collect3.Result!.QuestUpdates.SingleOrDefault() is
            {
                State: QuestStates.ReadyToTurnIn,
                Revision: 5
            } collect3Quest &&
            collect3Quest.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3,
            collect3.Failure?.Code ?? collect3.Result?.QuestUpdates.SingleOrDefault()?.State);

        var interactTurnIn = interactQuests.TurnIn(interactActor, "P00-01");
        Check(
            "interact.turn_in_completed",
            interactTurnIn.Accepted &&
            interactTurnIn.State is { State: QuestStates.Completed, Revision: 6 },
            interactTurnIn.Failure?.Code ?? interactTurnIn.State?.State);

        interactClock.Advance(TimeSpan.FromSeconds(20));
        var sharedRespawn = interactRegistry.Update();
        Check("interact.respawn_shared", sharedRespawn == 3, $"respawned={sharedRespawn}");

        var dedupeActor = NewPlayer("CHR_SELFCHECK_DEDUPE");
        dedupeActor.X = 36;
        dedupeActor.Y = 0;
        interactQuests.Accept(dedupeActor, "P00-01");
        var dedupe1 = interactions.Interact(
            dedupeActor, "ENT_SELFCHECK_PKG_1", new string('4', 31) + "a");
        interactClock.Advance(TimeSpan.FromSeconds(20));
        interactRegistry.Update();
        var dedupe2 = interactions.Interact(
            dedupeActor, "ENT_SELFCHECK_PKG_1", new string('5', 31) + "a");
        var dedupeState = interactQuests.GetState(dedupeActor.CharacterId, "P00-01").State;
        Check(
            "interact.distinct_record_dedupe",
            dedupe1.Accepted &&
            dedupe2.Accepted &&
            dedupe2.Result!.QuestUpdates.Count == 0 &&
            dedupeState is { State: QuestStates.Active } &&
            dedupeState.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 1,
            $"{dedupe2.Failure?.Code} updates={dedupe2.Result?.QuestUpdates.Count}");

        // Production Rules §5: P00-01 packages are per-character claims — two
        // characters collect all three at the same time without waiting for a
        // global respawn, and the shared registry state never leaves AVAILABLE.
        var packageClock = new ManualServerClock(
            new DateTimeOffset(2026, 10, 29, 6, 0, 0, TimeSpan.Zero));
        var packageRegistry = new WorldEntityRegistry(
            new WorldEntityCatalog(
                [],
                [
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG1", "MAN-BM-OBJ_BM_PACKAGE_01", 36, 20,
                        WorldEntityClaimPolicies.PerCharacter),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG2", "MAN-BM-OBJ_BM_PACKAGE_02", 44, 20,
                        WorldEntityClaimPolicies.PerCharacter),
                    MakeFixtureInteractable(
                        "ENT_SELFCHECK_PKG3", "MAN-BM-OBJ_BM_PACKAGE_03", 52, 20,
                        WorldEntityClaimPolicies.PerCharacter)
                ]),
            packageClock);
        var packageQuests = new InMemoryQuestService(
            questCatalog, new InMemoryQuestStateStore(), worldRecords, packageClock);
        var packageInteractions = new InMemoryInteractionService(
            packageRegistry,
            worldRecords,
            packageQuests,
            new InMemoryInventoryService(new InMemoryInventoryStateStore()),
            services.GetRequiredService<IWorldGeometryService>(),
            packageClock,
            fixedRoller,
            new GatherClaimStore(packageClock),
            interactOptions);

        var packageActorA = NewPlayer("CHR_SELFCHECK_PACKAGE_A");
        var packageActorB = NewPlayer("CHR_SELFCHECK_PACKAGE_B");
        packageQuests.Accept(packageActorA, "P00-01");
        packageQuests.Accept(packageActorB, "P00-01");

        var packageTargets = new[]
        {
            ("ENT_SELFCHECK_PKG1", 36.0),
            ("ENT_SELFCHECK_PKG2", 44.0),
            ("ENT_SELFCHECK_PKG3", 52.0)
        };
        var packageOutcomes = new InteractionOutcome?[packageTargets.Length, 2];
        using (var packageBarrier = new Barrier(2))
        {
            RunBarrierParallel(2, index =>
            {
                var session = index == 0 ? packageActorA : packageActorB;
                var keyStem = index == 0 ? 'a' : 'b';
                for (var step = 0; step < packageTargets.Length; step++)
                {
                    session.X = packageTargets[step].Item2;
                    session.Y = 0;
                    packageBarrier.SignalAndWait();
                    packageOutcomes[step, index] = packageInteractions.Interact(
                        session,
                        packageTargets[step].Item1,
                        $"{keyStem}{step}{new string('0', 30)}");
                }
            });
        }

        var packageAccepted = packageOutcomes
            .Cast<InteractionOutcome?>()
            .Count(outcome => outcome is { Accepted: true });
        var packageStateA = packageQuests.GetState(packageActorA.CharacterId, "P00-01").State;
        var packageStateB = packageQuests.GetState(packageActorB.CharacterId, "P00-01").State;
        Check(
            "interact.package_per_character_parallel",
            packageAccepted == 6 &&
            packageStateA is { State: QuestStates.ReadyToTurnIn } &&
            packageStateB is { State: QuestStates.ReadyToTurnIn } &&
            packageStateA.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3 &&
            packageStateB.ObjectiveCounters.GetValueOrDefault("OBJ_P00_01_PACKAGES") == 3,
            $"accepted={packageAccepted}/6 a={packageStateA?.State} b={packageStateB?.State}");

        packageRegistry.TryGet("ENT_SELFCHECK_PKG1", out var packageEntity);
        Check(
            "interact.package_state_stays_available",
            packageEntity.State == WorldEntityStates.Available &&
            packageRegistry.Update() == 0,
            packageEntity.State);

        packageActorA.X = 36;
        packageActorA.Y = 0;
        var packageReclaim = packageInteractions.Interact(
            packageActorA, "ENT_SELFCHECK_PKG1", new string('7', 32));
        Check(
            "interact.package_per_character_window",
            packageReclaim.Failure?.Code == InteractionErrorCodes.TargetNotAvailable,
            packageReclaim.Failure?.Code);

        packageClock.Advance(TimeSpan.FromSeconds(20));
        var packageReclaimAfterWindow = packageInteractions.Interact(
            packageActorA, "ENT_SELFCHECK_PKG1", new string('8', 32));
        Check(
            "interact.package_per_character_respawn",
            packageReclaimAfterWindow.Accepted &&
            packageReclaimAfterWindow.Result!.QuestUpdates.Count == 0 &&
            packageQuests.GetState(packageActorA.CharacterId, "P00-01").State is
            {
                State: QuestStates.ReadyToTurnIn
            },
            packageReclaimAfterWindow.Failure?.Code);

        // Progress dedupe scope: unique(actor, quest, objective, event-or-record)
        // — state is per character + quest, so the objective scope keeps two
        // valid objectives that reference the same record independent.
        if (!questCatalog.TryGet("P00-01", out var dedupeBaseQuest))
        {
            throw new InvalidOperationException("P00-01 must exist for the dedupe self-check.");
        }

        QuestDefinition MakeSyntheticQuest(
            string questId, params QuestObjectiveDefinition[] objectives) =>
            dedupeBaseQuest with
            {
                QuestId = questId,
                Objectives = objectives,
                InitialStepId = QuestStepIds.FromObjectiveId(objectives[0].ObjectiveId),
                PrerequisiteQuestIds = []
            };

        var syntheticDefinitions = new Dictionary<string, QuestDefinition>(StringComparer.Ordinal)
        {
            ["TEST-DEDUPE-01"] = MakeSyntheticQuest(
                "TEST-DEDUPE-01",
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SHARE_A", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_01"], 1, options.DefaultMapId),
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SHARE_B", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_01", "MAN-BM-OBJ_BM_PACKAGE_02"], 2,
                    options.DefaultMapId)),
            ["TEST-SEQ-01"] = MakeSyntheticQuest(
                "TEST-SEQ-01",
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SEQ_A", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_01"], 1, options.DefaultMapId),
                new QuestObjectiveDefinition(
                    "OBJ_TEST_SEQ_B", QuestObjectiveTypes.Collect,
                    ["MAN-BM-OBJ_BM_PACKAGE_03"], 1, options.DefaultMapId)),
            ["TEST-KILL-01"] = MakeSyntheticQuest(
                "TEST-KILL-01",
                new QuestObjectiveDefinition(
                    "OBJ_TEST_KILL_A", QuestObjectiveTypes.Kill,
                    ["MAN-BM-SPAWN_BM_01"], 2, options.DefaultMapId),
                new QuestObjectiveDefinition(
                    "OBJ_TEST_KILL_B", QuestObjectiveTypes.Kill,
                    ["MAN-BM-SPAWN_BM_01"], 2, options.DefaultMapId))
        };
        var syntheticQuests = new InMemoryQuestService(
            new QuestCatalog(syntheticDefinitions),
            new InMemoryQuestStateStore(),
            worldRecords,
            interactClock);
        var dedupeScopeActor = NewPlayer("CHR_SELFCHECK_DEDUPE_SCOPE");

        syntheticQuests.Accept(dedupeScopeActor, "TEST-DEDUPE-01");
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('a', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_01",
            options.DefaultMapId);
        var sharedRecordState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-DEDUPE-01").State;
        Check(
            "quest.dedupe_two_objectives_share_record",
            sharedRecordState is { State: QuestStates.Active } &&
            sharedRecordState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_A") == 1 &&
            sharedRecordState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B") == 1,
            $"{sharedRecordState?.State} " +
            $"a={sharedRecordState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_A")} " +
            $"b={sharedRecordState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B")}");

        var duplicateEvent = syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('b', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_01",
            options.DefaultMapId);
        var duplicateState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-DEDUPE-01").State;
        Check(
            "quest.dedupe_duplicate_event",
            duplicateEvent.Count == 0 &&
            duplicateState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_A") == 1 &&
            duplicateState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B") == 1,
            $"updates={duplicateEvent.Count}");

        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('c', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_02",
            options.DefaultMapId);
        var secondRecordState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-DEDUPE-01").State;
        Check(
            "quest.dedupe_second_record",
            secondRecordState is { State: QuestStates.ReadyToTurnIn } &&
            secondRecordState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SHARE_B") == 2,
            secondRecordState?.State);

        syntheticQuests.Accept(dedupeScopeActor, "TEST-SEQ-01");
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('d', 32),
            QuestProgressEventTypes.InteractClaim, "MAN-BM-OBJ_BM_PACKAGE_01",
            options.DefaultMapId);
        var sequentialState = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-SEQ-01").State;
        Check(
            "quest.dedupe_sequential_step_guard",
            sequentialState is { State: QuestStates.Active } &&
            sequentialState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SEQ_A") == 1 &&
            sequentialState.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SEQ_B") == 0,
            $"{sequentialState?.State} " +
            $"b={sequentialState?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_SEQ_B")}");

        syntheticQuests.Accept(dedupeScopeActor, "TEST-KILL-01");
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('e', 32),
            QuestProgressEventTypes.Kill, "MAN-BM-SPAWN_BM_01", options.DefaultMapId);
        var killFirst = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-KILL-01").State;
        var killReplay = syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('e', 32),
            QuestProgressEventTypes.Kill, "MAN-BM-SPAWN_BM_01", options.DefaultMapId);
        syntheticQuests.RecordVerifiedEvent(
            dedupeScopeActor, new string('f', 32),
            QuestProgressEventTypes.Kill, "MAN-BM-SPAWN_BM_01", options.DefaultMapId);
        var killSecond = syntheticQuests.GetState(
            dedupeScopeActor.CharacterId, "TEST-KILL-01").State;
        Check(
            "quest.dedupe_kill_event_scope",
            killFirst.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_A") == 1 &&
            killFirst.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_B") == 1 &&
            killReplay.Count == 0 &&
            killSecond is { State: QuestStates.ReadyToTurnIn } &&
            killSecond.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_A") == 2 &&
            killSecond.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_B") == 2,
            $"{killSecond?.State} " +
            $"a={killSecond?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_A")} " +
            $"b={killSecond?.ObjectiveCounters.GetValueOrDefault("OBJ_TEST_KILL_B")}");

        var losInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [
                        MakeFixtureInteractable(
                            "ENT_SELFCHECK_LOS_BLOCKED", "MAN-BM-OBJ_BM_PACKAGE_01", 46.5, 60),
                        MakeFixtureInteractable(
                            "ENT_SELFCHECK_LOS_CLEAR", "MAN-BM-OBJ_BM_PACKAGE_01", 40, 60)
                    ]),
                interactClock),
            worldRecords,
            interactQuests,
            interactInventory,
            geometry,
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var losBlockedActor = NewPlayer("CHR_SELFCHECK_INTERACT_LOS");
        losBlockedActor.X = 44;
        losBlockedActor.Y = 0;
        var losBlocked = losInteractions.Interact(
            losBlockedActor, "ENT_SELFCHECK_LOS_BLOCKED", new string('6', 31) + "a");
        Check(
            "interact.los_blocked",
            losBlocked.Failure is
            {
                Code: InteractionErrorCodes.OutOfRange,
                Retryable: true
            },
            losBlocked.Failure?.Code);

        losBlockedActor.X = 36;
        var losClear = losInteractions.Interact(
            losBlockedActor, "ENT_SELFCHECK_LOS_CLEAR", new string('7', 31) + "a");
        Check(
            "interact.los_allowed",
            losClear.Accepted &&
            losClear.Result is { Outcome: "collected", TargetState: WorldEntityStates.Depleted },
            losClear.Failure?.Code);

        WorldEntityInstance MakeFixtureNode(
            string entityId,
            string recordId,
            double x,
            int respawnSeconds)
        {
            var node = new WorldEntityInstance
            {
                EntityId = entityId,
                RecordId = recordId,
                Kind = WorldEntityKinds.GatherNode,
                TemplateIds = new[] { "NODE_BM_ORE_01" },
                MapId = options.DefaultMapId,
                FloorId = "OVERWORLD",
                X = x,
                Y = 0,
                Quantity = 1,
                RespawnSeconds = respawnSeconds
            };
            node.Initialize();
            return node;
        }

        var gatherInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [
                        MakeFixtureNode("ENT_SELFCHECK_NODE_ORE", "MAN-BM-NODE_BM_ORE_01", 21, 60),
                        MakeFixtureNode("ENT_SELFCHECK_NODE_T2", "MAN-BM-NODE_BM_HERB_02", 132, 120)
                    ]),
                interactClock),
            worldRecords,
            interactQuests,
            interactInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var gatherer1 = NewPlayer("CHR_SELFCHECK_GATHER_1");
        gatherer1.X = 21;
        gatherer1.Y = 0;
        var gather1 = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('8', 31) + "a");
        Check(
            "interact.gather_claim",
            gather1.Accepted &&
            gather1.Result is
            {
                Kind: WorldEntityKinds.GatherNode,
                Outcome: "gathered",
                TargetState: WorldEntityStates.Available,
                RecordId: "MAN-BM-NODE_BM_ORE_01",
                RespawnAtUtc: not null
            } &&
            gather1.Result.Yield is { ItemId: "MAT-ORE-01", Quantity: 2 },
            gather1.Failure?.Code ?? gather1.Result?.Outcome);

        var gather1Inventory = interactInventory.GetSnapshot(gatherer1.CharacterId);
        Check(
            "interact.gather_inventory",
            gather1Inventory.InventoryRevision == 1 &&
            gather1Inventory.Items.Single() is
            {
                TemplateId: "MAT-ORE-01",
                Stack: 2,
                Location: InventoryLocations.Bag
            },
            $"revision={gather1Inventory.InventoryRevision} items={gather1Inventory.Items.Count}");

        var gather1Replay = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('8', 31) + "a");
        Check(
            "interact.gather_replay_no_double",
            gather1Replay.Accepted && ReferenceEquals(gather1Replay.Result, gather1.Result) &&
            interactInventory.GetSnapshot(gatherer1.CharacterId).Items.Count == 1,
            gather1Replay.Failure?.Code);

        var gather1Cooldown = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('9', 31) + "a");
        Check(
            "interact.gather_shard_cooldown",
            gather1Cooldown.Failure?.Code == InteractionErrorCodes.TargetNotAvailable &&
            interactInventory.GetSnapshot(gatherer1.CharacterId).Items.Count == 1,
            gather1Cooldown.Failure?.Code);

        var gatherer2 = NewPlayer("CHR_SELFCHECK_GATHER_2");
        gatherer2.X = 21;
        gatherer2.Y = 0;
        var gather2 = gatherInteractions.Interact(
            gatherer2, "ENT_SELFCHECK_NODE_ORE", new string('a', 32));
        Check(
            "interact.gather_shard_other_character",
            gather2.Accepted &&
            interactInventory.GetSnapshot(gatherer2.CharacterId).Items.Count == 1 &&
            interactInventory.GetSnapshot(gatherer1.CharacterId).Items.Count == 1,
            gather2.Failure?.Code);

        interactClock.Advance(TimeSpan.FromSeconds(60));
        var gather1Again = gatherInteractions.Interact(
            gatherer1, "ENT_SELFCHECK_NODE_ORE", new string('b', 32));
        Check(
            "interact.gather_respawn_per_character",
            gather1Again.Accepted &&
            interactInventory.GetSnapshot(gatherer1.CharacterId) is
            {
                InventoryRevision: 2,
                Items: { Count: 2 }
            },
            $"{gather1Again.Failure?.Code} revision={interactInventory.GetSnapshot(gatherer1.CharacterId).InventoryRevision}");

        var professionActor = NewPlayer("CHR_SELFCHECK_GATHER_GATE");
        professionActor.X = 132;
        professionActor.Y = 0;
        var professionGate = gatherInteractions.Interact(
            professionActor, "ENT_SELFCHECK_NODE_T2", new string('c', 32));
        Check(
            "interact.profession_gate",
            professionGate.Failure?.Code == InteractionErrorCodes.ProfessionLevelInsufficient &&
            interactInventory.GetSnapshot(professionActor.CharacterId).Items.Count == 0,
            professionGate.Failure?.Code);

        // ─── barrier-coordinated concurrency + failure injection (QOD-A) ───

        var raceInventory = new InMemoryInventoryService(new InMemoryInventoryStateStore());
        var raceInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [
                        MakeFixtureNode("ENT_SELFCHECK_RACE_NODE", "MAN-BM-NODE_BM_ORE_01", 21, 60),
                        MakeFixtureInteractable(
                            "ENT_SELFCHECK_RACE_PKG", "MAN-BM-OBJ_BM_PACKAGE_01", 36, 20)
                    ]),
                interactClock),
            worldRecords,
            interactQuests,
            raceInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        // Same key, same payload in parallel: both requests must replay the
        // winner's stored result — one interactionId, one yield.
        var raceActor = NewPlayer("CHR_SELFCHECK_RACE_GATHER");
        raceActor.X = 21;
        raceActor.Y = 0;
        var sameKeyRace = Guid.NewGuid().ToString("N");
        var sameKeyRaceOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            sameKeyRaceOutcomes[index] = raceInteractions.Interact(
                raceActor, "ENT_SELFCHECK_RACE_NODE", sameKeyRace);
        });
        var sameKeyRaceAccepted = sameKeyRaceOutcomes.Count(outcome => outcome.Accepted);
        var sameKeyRaceIds = sameKeyRaceOutcomes
            .Where(outcome => outcome.Accepted)
            .Select(outcome => outcome.Result!.InteractionId)
            .Distinct()
            .Count();
        Check(
            "interact.parallel_same_key_single_result",
            sameKeyRaceAccepted == 2 &&
            sameKeyRaceIds == 1 &&
            ReferenceEquals(sameKeyRaceOutcomes[0].Result, sameKeyRaceOutcomes[1].Result) &&
            raceInventory.GetSnapshot(raceActor.CharacterId).Items.Count == 1,
            $"accepted={sameKeyRaceAccepted} distinctIds={sameKeyRaceIds} " +
            $"codes={string.Join(",", sameKeyRaceOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Two different keys, same character/node in parallel: exactly one
        // claim wins, the other gets the per-character cooldown.
        var twoKeyActor = NewPlayer("CHR_SELFCHECK_RACE_2KEY");
        twoKeyActor.X = 21;
        twoKeyActor.Y = 0;
        var twoKeyOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            twoKeyOutcomes[index] = raceInteractions.Interact(
                twoKeyActor, "ENT_SELFCHECK_RACE_NODE", Guid.NewGuid().ToString("N"));
        });
        var twoKeyAccepted = twoKeyOutcomes.Count(outcome => outcome.Accepted);
        var twoKeyCooldown = twoKeyOutcomes.Count(outcome =>
            !outcome.Accepted &&
            outcome.Failure?.Code == InteractionErrorCodes.TargetNotAvailable);
        Check(
            "interact.parallel_two_keys_single_grant",
            twoKeyAccepted == 1 && twoKeyCooldown == 1 &&
            raceInventory.GetSnapshot(twoKeyActor.CharacterId).Items.Count == 1,
            $"accepted={twoKeyAccepted} " +
            $"codes={string.Join(",", twoKeyOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Two characters claim the same node in parallel: per-character
        // shards mean both win independently.
        var shardA = NewPlayer("CHR_SELFCHECK_SHARD_A");
        shardA.X = 21;
        shardA.Y = 0;
        var shardB = NewPlayer("CHR_SELFCHECK_SHARD_B");
        shardB.X = 21;
        shardB.Y = 0;
        var shardActors = new[] { shardA, shardB };
        var shardOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            shardOutcomes[index] = raceInteractions.Interact(
                shardActors[index], "ENT_SELFCHECK_RACE_NODE", Guid.NewGuid().ToString("N"));
        });
        Check(
            "interact.parallel_two_characters_independent",
            shardOutcomes.All(outcome => outcome.Accepted) &&
            raceInventory.GetSnapshot(shardA.CharacterId).Items.Count == 1 &&
            raceInventory.GetSnapshot(shardB.CharacterId).Items.Count == 1,
            $"codes={string.Join(",", shardOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Two characters race for one shared INTERACTABLE: the registry's
        // atomic check-and-set lets exactly one collect.
        var pkgA = NewPlayer("CHR_SELFCHECK_RACE_PKG_A");
        pkgA.X = 36;
        pkgA.Y = 0;
        var pkgB = NewPlayer("CHR_SELFCHECK_RACE_PKG_B");
        pkgB.X = 36;
        pkgB.Y = 0;
        var pkgActors = new[] { pkgA, pkgB };
        var pkgOutcomes = new InteractionOutcome[2];
        RunBarrierParallel(2, index =>
        {
            pkgOutcomes[index] = raceInteractions.Interact(
                pkgActors[index], "ENT_SELFCHECK_RACE_PKG", Guid.NewGuid().ToString("N"));
        });
        var pkgAccepted = pkgOutcomes.Count(outcome => outcome.Accepted);
        var pkgDepleted = pkgOutcomes.Count(outcome =>
            !outcome.Accepted &&
            outcome.Failure?.Code == InteractionErrorCodes.TargetNotAvailable);
        Check(
            "interact.parallel_shared_interactable_single_claim",
            pkgAccepted == 1 && pkgDepleted == 1,
            $"accepted={pkgAccepted} " +
            $"codes={string.Join(",", pkgOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        // Failure after the reservation: the claim is released by token, the
        // node stays claimable and the retry grants exactly once.
        var failInventory = new InMemoryInventoryService(new InMemoryInventoryStateStore());
        var raceFailOnceInventory = new FailOnceInventoryDecorator(failInventory);
        var failInteractions = new InMemoryInteractionService(
            new WorldEntityRegistry(
                new WorldEntityCatalog(
                    [],
                    [MakeFixtureNode("ENT_SELFCHECK_FAIL_NODE", "MAN-BM-NODE_BM_ORE_01", 21, 60)]),
                interactClock),
            worldRecords,
            interactQuests,
            raceFailOnceInventory,
            services.GetRequiredService<IWorldGeometryService>(),
            interactClock,
            fixedRoller,
            new GatherClaimStore(interactClock),
            interactOptions);

        var failGatherer = NewPlayer("CHR_SELFCHECK_GATHER_FAIL");
        failGatherer.X = 21;
        failGatherer.Y = 0;
        var failedGather = failInteractions.Interact(
            failGatherer, "ENT_SELFCHECK_FAIL_NODE", Guid.NewGuid().ToString("N"));
        Check(
            "interact.fail_after_reserve_rejected",
            !failedGather.Accepted &&
            failedGather.Failure is
            {
                Code: InteractionErrorCodes.TargetNotAvailable,
                Retryable: true
            } &&
            failInventory.GetSnapshot(failGatherer.CharacterId).Items.Count == 0,
            failedGather.Failure?.Code);

        var retriedGather = failInteractions.Interact(
            failGatherer, "ENT_SELFCHECK_FAIL_NODE", Guid.NewGuid().ToString("N"));
        Check(
            "interact.fail_after_reserve_retry_grants_once",
            retriedGather.Accepted &&
            failInventory.GetSnapshot(failGatherer.CharacterId) is { Items: { Count: 1 } },
            retriedGather.Failure?.Code);

        var inventoryActor = NewPlayer("CHR_SELFCHECK_INVENTORY");
        var emptyInventory = inventory.GetSnapshot(inventoryActor.CharacterId);
        Check(
            "inventory.empty",
            emptyInventory.InventoryRevision == 0 && emptyInventory.Items.Count == 0,
            $"revision={emptyInventory.InventoryRevision}");

        var granted = inventory.Apply(inventoryActor, new InventoryMutation
        {
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Bag,
                    Durability = 100
                }
            ],
            CurrencyDeltas = [new CurrencyDelta { CurrencyId = "COIN", Amount = 20 }]
        });
        Check(
            "inventory.grant",
            granted.IsSuccess &&
            granted.Snapshot!.InventoryRevision == 1 &&
            granted.Snapshot.Items.Count == 1 &&
            granted.Snapshot.Currencies.Single().Amount == 20,
            granted.ErrorCode ?? $"revision={granted.Snapshot?.InventoryRevision}");

        var equipped = inventory.Apply(inventoryActor, new InventoryMutation
        {
            ExpectedRevision = 1,
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Equipped,
                    Slot = "CHEST",
                    Durability = 100
                }
            ]
        });
        Check(
            "inventory.equip",
            equipped.IsSuccess &&
            equipped.Snapshot!.InventoryRevision == 2 &&
            equipped.Snapshot.Items.Count == 2,
            equipped.ErrorCode ?? $"revision={equipped.Snapshot?.InventoryRevision}");

        var slotClash = inventory.Apply(inventoryActor, new InventoryMutation
        {
            ExpectedRevision = 2,
            AddItems =
            [
                new ItemGrant
                {
                    TemplateId = "EQ-MK-CHEST-T1-R-COMMON",
                    Stack = 1,
                    Location = InventoryLocations.Equipped,
                    Slot = "CHEST",
                    Durability = 100
                }
            ]
        });
        Check(
            "inventory.slot_occupied",
            slotClash.ErrorCode == InventoryErrorCodes.SlotOccupied,
            slotClash.ErrorCode);

        var missingItem = inventory.Apply(inventoryActor, new InventoryMutation
        {
            RemoveItems = [new ItemRemoval { InstanceId = "ITM_SELFCHECK_MISSING", Stack = 1 }]
        });
        Check(
            "inventory.item_not_found",
            missingItem.ErrorCode == InventoryErrorCodes.ItemNotFound,
            missingItem.ErrorCode);

        var overdraw = inventory.Apply(inventoryActor, new InventoryMutation
        {
            CurrencyDeltas = [new CurrencyDelta { CurrencyId = "COIN", Amount = -1000 }]
        });
        Check(
            "inventory.insufficient_currency",
            overdraw.ErrorCode == InventoryErrorCodes.InsufficientCurrency,
            overdraw.ErrorCode);

        var staleWrite = inventory.Apply(inventoryActor, new InventoryMutation
        {
            ExpectedRevision = 1,
            CurrencyDeltas = [new CurrencyDelta { CurrencyId = "COIN", Amount = 1 }]
        });
        Check(
            "inventory.revision_conflict",
            staleWrite.ErrorCode == InventoryErrorCodes.RevisionConflict && staleWrite.Retryable,
            staleWrite.ErrorCode);

        Check(
            "inventory.rejections_do_not_mutate",
            inventory.GetSnapshot(inventoryActor.CharacterId).InventoryRevision == 2,
            inventory.GetSnapshot(inventoryActor.CharacterId).InventoryRevision.ToString());

        var bagItem = inventory.GetSnapshot(inventoryActor.CharacterId)
            .Items.Single(item => item.Location == InventoryLocations.Bag);
        var removed = inventory.Apply(inventoryActor, new InventoryMutation
        {
            RemoveItems = [new ItemRemoval { InstanceId = bagItem.InstanceId, Stack = 1 }]
        });
        Check(
            "inventory.remove",
            removed.IsSuccess &&
            removed.Snapshot!.Items.Count == 1 &&
            removed.Snapshot.InventoryRevision == 3,
            removed.ErrorCode ?? $"revision={removed.Snapshot?.InventoryRevision}");

        // ─── turn-in ───────────────────────────────────────────

        var turnInActor = NewPlayer("CHR_SELFCHECK_TURNIN");
        var turnInQuestId = "P00-01";

        // set up objectives complete → READY_TO_TURN_IN
        var turnInAccept = quests.Accept(turnInActor, turnInQuestId);
        Check(
            "turnin.accept_setup",
            turnInAccept.Accepted,
            turnInAccept.Failure?.Code);

        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            var eventId = Guid.NewGuid().ToString("N");
            quests.RecordVerifiedEvent(
                turnInActor, eventId, QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }

        var readyState = quests.GetState(turnInActor.CharacterId, turnInQuestId);
        Check(
            "turnin.ready_state",
            readyState.Accepted &&
            string.Equals(readyState.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            readyState.State?.State);

        // walk to turn-in NPC anchor
        npcAnchors.TryResolve("NPC_TA_VAN_KHANH", "MAP_BEN_MUA", out var turnInAnchor);
        turnInActor.X = turnInAnchor.X;
        turnInActor.Y = turnInAnchor.Y;

        // NPC mismatch
        var turnInWrongNpc = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_LYAN", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.npc_mismatch",
            !turnInWrongNpc.Accepted &&
            string.Equals(turnInWrongNpc.Failure!.Code, QuestTurnInErrorCodes.NpcMismatch, StringComparison.Ordinal),
            turnInWrongNpc.Failure?.Code);

        // unknown quest
        var turnInUnknownQuest = questTurnIn.TurnIn(
            turnInActor, "QQ-99", "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.quest_not_found",
            !turnInUnknownQuest.Accepted &&
            string.Equals(turnInUnknownQuest.Failure!.Code, QuestErrorCodes.QuestNotFound, StringComparison.Ordinal),
            turnInUnknownQuest.Failure?.Code);

        // wrong floor: actor on a different floor than the NPC anchor
        turnInActor.FloorId = "MAP_BEN_MUA_F1";
        var wrongFloor = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.wrong_floor",
            !wrongFloor.Accepted &&
            string.Equals(wrongFloor.Failure!.Code, QuestTurnInErrorCodes.OutOfRange, StringComparison.Ordinal),
            wrongFloor.Failure?.Code);
        turnInActor.FloorId = "OVERWORLD";

        // out of range
        turnInActor.X = 0;
        turnInActor.Y = 0;
        var outOfRange = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.out_of_range",
            !outOfRange.Accepted &&
            string.Equals(outOfRange.Failure!.Code, QuestTurnInErrorCodes.OutOfRange, StringComparison.Ordinal),
            outOfRange.Failure?.Code);

        // back in range
        turnInActor.X = turnInAnchor.X;
        turnInActor.Y = turnInAnchor.Y;

        // successful turn-in
        var turnInKey = Guid.NewGuid().ToString("N");
        var result = questTurnIn.TurnIn(turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", turnInKey);
        Check(
            "turnin.success",
            result.Accepted &&
            string.Equals(result.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal) &&
            result.Result!.Rewards.Currency.Any(c =>
                string.Equals(c.CurrencyId, "COIN", StringComparison.Ordinal) && c.Amount == 20) &&
            result.Result!.Rewards.Items.Count == 1 &&
            string.Equals(result.Result!.Rewards.Items[0].TemplateId, "EQ-MK-CHEST-T1-R-COMMON", StringComparison.Ordinal) &&
            !result.Result!.Rewards.Xp.Applied &&
            result.Result!.Unlocks.Count == 1 &&
            string.Equals(result.Result!.Unlocks[0], "P00-02", StringComparison.Ordinal),
            result.Failure?.Code);

        // verify inventory was granted
        var postTurnInInv = inventory.GetSnapshot(turnInActor.CharacterId);
        Check(
            "turnin.inventory_granted",
            postTurnInInv.Currencies.Any(c =>
                string.Equals(c.CurrencyId, "COIN", StringComparison.Ordinal) && c.Amount == 20) &&
            postTurnInInv.Items.Any(i =>
                string.Equals(i.TemplateId, "EQ-MK-CHEST-T1-R-COMMON", StringComparison.Ordinal)),
            $"currencies={postTurnInInv.Currencies.Count} items={postTurnInInv.Items.Count}");

        // replay same key returns identical result
        var replay = questTurnIn.TurnIn(turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", turnInKey);
        Check(
            "turnin.replay_same_key",
            replay.Accepted &&
            string.Equals(replay.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            replay.Failure?.Code);

        // second turn-in with new key → invalid_transition
        var newKey = Guid.NewGuid().ToString("N");
        var secondTurnIn = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_TA_VAN_KHANH", newKey);
        Check(
            "turnin.invalid_transition_after_completed",
            !secondTurnIn.Accepted &&
            string.Equals(secondTurnIn.Failure!.Code, QuestErrorCodes.InvalidTransition, StringComparison.Ordinal),
            secondTurnIn.Failure?.Code);

        // inventory unchanged after rejected second turn-in
        var unchangedInv = inventory.GetSnapshot(turnInActor.CharacterId);
        Check(
            "turnin.inventory_no_double_reward",
            unchangedInv.Currencies.Count == 1 &&
            unchangedInv.Items.Count == 1,
            $"currencies={unchangedInv.Currencies.Count} items={unchangedInv.Items.Count}");

        // idempotency conflict: same key, different payload (different npcId)
        var wrongNpcReplay = questTurnIn.TurnIn(
            turnInActor, turnInQuestId, "NPC_LYAN", turnInKey);
        Check(
            "turnin.same_key_different_npc_conflict",
            !wrongNpcReplay.Accepted &&
            string.Equals(
                wrongNpcReplay.Failure!.Code,
                QuestTurnInErrorCodes.IdempotencyConflict,
                StringComparison.Ordinal),
            wrongNpcReplay.Failure?.Code);

        var turnInIdemActor = NewPlayer("CHR_SELFCHECK_IDEM");
        quests.Accept(turnInIdemActor, "P00-01");
        // progress to READY_TO_TURN_IN
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                turnInIdemActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        turnInIdemActor.X = turnInAnchor.X;
        turnInIdemActor.Y = turnInAnchor.Y;

        var conflictKey2 = Guid.NewGuid().ToString("N");
        var firstCall = questTurnIn.TurnIn(turnInIdemActor, turnInQuestId, "NPC_TA_VAN_KHANH", conflictKey2);
        Check(
            "turnin.idempotency_setup",
            firstCall.Accepted,
            firstCall.Failure?.Code);

        // Data integrity: reward-once via ledger
        var ledgerResult = rewardLedger.Find(turnInIdemActor.CharacterId, turnInQuestId);
        Check(
            "turnin.reward_ledger_recorded",
            ledgerResult is not null &&
            string.Equals(ledgerResult.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            ledgerResult?.QuestState.State);

        // ─── failure injection: reward transaction must not partially commit ───

        var failOnceInventory = new FailOnceInventoryDecorator(inventory);
        var failOnceLedger = new RewardLedgerStore();
        var failOnceTurnIn = new InMemoryQuestTurnInService(
            questCatalog,
            quests,
            failOnceInventory,
            npcAnchors,
            services.GetRequiredService<IWorldGeometryService>(),
            failOnceLedger,
            services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);

        var failActor = NewPlayer("CHR_SELFCHECK_FAILONCE");
        quests.Accept(failActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                failActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        failActor.X = turnInAnchor.X;
        failActor.Y = turnInAnchor.Y;

        var failedTurnIn = failOnceTurnIn.TurnIn(
            failActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.failure_injection_rejected",
            !failedTurnIn.Accepted &&
            string.Equals(failedTurnIn.Failure!.Code, InventoryErrorCodes.SlotOccupied, StringComparison.Ordinal) &&
            failedTurnIn.Failure.Retryable,
            failedTurnIn.Failure?.Code);

        var stateAfterFail = quests.GetState(failActor.CharacterId, turnInQuestId);
        Check(
            "turnin.failure_injection_state_kept",
            stateAfterFail.Accepted &&
            string.Equals(stateAfterFail.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            stateAfterFail.State?.State);

        var inventoryAfterFail = inventory.GetSnapshot(failActor.CharacterId);
        Check(
            "turnin.failure_injection_no_partial_reward",
            inventoryAfterFail.Items.Count == 0 && inventoryAfterFail.Currencies.Count == 0,
            $"items={inventoryAfterFail.Items.Count} currencies={inventoryAfterFail.Currencies.Count}");

        Check(
            "turnin.failure_injection_ledger_empty",
            failOnceLedger.Find(failActor.CharacterId, turnInQuestId) is null,
            "ledger entry must not exist after failed grant");

        var retriedTurnIn = failOnceTurnIn.TurnIn(
            failActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.failure_injection_retry_succeeds",
            retriedTurnIn.Accepted &&
            string.Equals(retriedTurnIn.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            retriedTurnIn.Failure?.Code);

        var inventoryAfterRetry = inventory.GetSnapshot(failActor.CharacterId);
        Check(
            "turnin.failure_injection_single_reward",
            inventoryAfterRetry.Currencies.Count == 1 &&
            inventoryAfterRetry.Currencies[0].Amount == 20 &&
            inventoryAfterRetry.Items.Count == 1,
            $"items={inventoryAfterRetry.Items.Count} currencies={inventoryAfterRetry.Currencies.Count}");

        // ─── failure injection: quest flip failure must roll back the grant ───

        var failOnceQuests = new FailOnceQuestDecorator(quests);
        var flipFailLedger = new RewardLedgerStore();
        var flipFailTurnIn = new InMemoryQuestTurnInService(
            questCatalog,
            failOnceQuests,
            inventory,
            npcAnchors,
            services.GetRequiredService<IWorldGeometryService>(),
            flipFailLedger,
            services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);

        var flipFailActor = NewPlayer("CHR_SELFCHECK_FLIPFAIL");
        quests.Accept(flipFailActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                flipFailActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        flipFailActor.X = turnInAnchor.X;
        flipFailActor.Y = turnInAnchor.Y;

        var flipFailed = flipFailTurnIn.TurnIn(
            flipFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.flip_failure_rejected",
            !flipFailed.Accepted &&
            string.Equals(flipFailed.Failure!.Code, QuestErrorCodes.InvalidTransition, StringComparison.Ordinal),
            flipFailed.Failure?.Code);

        var flipStateAfter = quests.GetState(flipFailActor.CharacterId, turnInQuestId);
        Check(
            "turnin.flip_failure_state_kept",
            flipStateAfter.Accepted &&
            string.Equals(flipStateAfter.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            flipStateAfter.State?.State);

        var flipInventoryAfter = inventory.GetSnapshot(flipFailActor.CharacterId);
        Check(
            "turnin.flip_failure_grant_rolled_back",
            flipInventoryAfter.Items.Count == 0 && flipInventoryAfter.Currencies.Count == 0,
            $"items={flipInventoryAfter.Items.Count} currencies={flipInventoryAfter.Currencies.Count}");

        Check(
            "turnin.flip_failure_ledger_empty",
            flipFailLedger.Find(flipFailActor.CharacterId, turnInQuestId) is null,
            "ledger entry must not exist after failed flip");

        var flipRetried = flipFailTurnIn.TurnIn(
            flipFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.flip_failure_retry_succeeds",
            flipRetried.Accepted &&
            string.Equals(flipRetried.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            flipRetried.Failure?.Code);

        var flipInventoryRetry = inventory.GetSnapshot(flipFailActor.CharacterId);
        Check(
            "turnin.flip_failure_single_reward",
            flipInventoryRetry.Currencies.Count == 1 &&
            flipInventoryRetry.Currencies[0].Amount == 20 &&
            flipInventoryRetry.Items.Count == 1,
            $"items={flipInventoryRetry.Items.Count} currencies={flipInventoryRetry.Currencies.Count}");

        // ─── failure injection: ledger failure must roll back grant and flip ───

        var failOnceLedgerStore = new FailOnceLedgerStore();
        var ledgerFailTurnIn = new InMemoryQuestTurnInService(
            questCatalog,
            quests,
            inventory,
            npcAnchors,
            services.GetRequiredService<IWorldGeometryService>(),
            failOnceLedgerStore,
            services.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);

        var ledgerFailActor = NewPlayer("CHR_SELFCHECK_LEDGERFAIL");
        quests.Accept(ledgerFailActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                ledgerFailActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        ledgerFailActor.X = turnInAnchor.X;
        ledgerFailActor.Y = turnInAnchor.Y;

        var ledgerFailed = ledgerFailTurnIn.TurnIn(
            ledgerFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.ledger_failure_rejected",
            !ledgerFailed.Accepted &&
            string.Equals(
                ledgerFailed.Failure!.Code,
                QuestTurnInErrorCodes.IdempotencyConflict,
                StringComparison.Ordinal) &&
            ledgerFailed.Failure.Retryable,
            ledgerFailed.Failure?.Code);

        var ledgerStateAfter = quests.GetState(ledgerFailActor.CharacterId, turnInQuestId);
        Check(
            "turnin.ledger_failure_state_kept",
            ledgerStateAfter.Accepted &&
            string.Equals(ledgerStateAfter.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            ledgerStateAfter.State?.State);

        var ledgerInventoryAfter = inventory.GetSnapshot(ledgerFailActor.CharacterId);
        Check(
            "turnin.ledger_failure_grant_rolled_back",
            ledgerInventoryAfter.Items.Count == 0 && ledgerInventoryAfter.Currencies.Count == 0,
            $"items={ledgerInventoryAfter.Items.Count} currencies={ledgerInventoryAfter.Currencies.Count}");

        Check(
            "turnin.ledger_failure_ledger_empty",
            failOnceLedgerStore.Find(ledgerFailActor.CharacterId, turnInQuestId) is null,
            "ledger entry must not exist after failed record");

        var ledgerRetried = ledgerFailTurnIn.TurnIn(
            ledgerFailActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.ledger_failure_retry_succeeds",
            ledgerRetried.Accepted &&
            string.Equals(ledgerRetried.Result!.QuestState.State, QuestStates.Completed, StringComparison.Ordinal),
            ledgerRetried.Failure?.Code);

        var ledgerInventoryRetry = inventory.GetSnapshot(ledgerFailActor.CharacterId);
        Check(
            "turnin.ledger_failure_single_reward",
            ledgerInventoryRetry.Currencies.Count == 1 &&
            ledgerInventoryRetry.Currencies[0].Amount == 20 &&
            ledgerInventoryRetry.Items.Count == 1,
            $"items={ledgerInventoryRetry.Items.Count} currencies={ledgerInventoryRetry.Currencies.Count}");

        // ─── overflow: balance near long.MaxValue rejects without partial commit ───

        var overflowActor = NewPlayer("CHR_SELFCHECK_OVERFLOW");
        quests.Accept(overflowActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                overflowActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        overflowActor.X = turnInAnchor.X;
        overflowActor.Y = turnInAnchor.Y;

        // Seed the near-max balance directly in the state store: mutation
        // validation caps currency deltas at 10^12, so the overflow boundary
        // can only be reached by writing the stored balance itself.
        var overflowStateStore = services.GetRequiredService<IInventoryStateStore>();
        var overflowBalanceState = overflowStateStore.GetOrAdd(overflowActor.CharacterId);
        lock (overflowBalanceState.SyncRoot)
        {
            overflowBalanceState.Currencies["COIN"] = long.MaxValue - 10;
        }

        var seedOverflow = inventory.GetSnapshot(overflowActor.CharacterId);
        Check(
            "turnin.overflow_seed",
            seedOverflow.Currencies.Count == 1 &&
            seedOverflow.Currencies[0].Amount == long.MaxValue - 10,
            seedOverflow.Currencies.Count.ToString());

        var overflowTurnIn = questTurnIn.TurnIn(
            overflowActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        Check(
            "turnin.overflow_rejected_no_partial",
            !overflowTurnIn.Accepted &&
            string.Equals(overflowTurnIn.Failure!.Code, P1ErrorCodes.InvalidPayload, StringComparison.Ordinal) &&
            overflowTurnIn.Failure.FieldErrors.Contains("currencyDeltas", StringComparer.Ordinal),
            overflowTurnIn.Failure?.Code);

        var overflowState = quests.GetState(overflowActor.CharacterId, turnInQuestId);
        Check(
            "turnin.overflow_state_kept",
            overflowState.Accepted &&
            string.Equals(overflowState.State!.State, QuestStates.ReadyToTurnIn, StringComparison.Ordinal),
            overflowState.State?.State);

        var overflowInventory = inventory.GetSnapshot(overflowActor.CharacterId);
        Check(
            "turnin.overflow_inventory_unchanged",
            overflowInventory.Currencies.Count == 1 &&
            overflowInventory.Currencies[0].Amount == long.MaxValue - 10 &&
            overflowInventory.Items.Count == 0,
            $"items={overflowInventory.Items.Count} currencies={overflowInventory.Currencies.Count}");

        // ─── concurrency: parallel turn-ins must grant exactly once ───

        var parallelActor = NewPlayer("CHR_SELFCHECK_PARALLEL");
        quests.Accept(parallelActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                parallelActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        parallelActor.X = turnInAnchor.X;
        parallelActor.Y = turnInAnchor.Y;

        var parallelOutcomes = new TurnInOutcome[2];
        RunBarrierParallel(2, index =>
        {
            parallelOutcomes[index] = questTurnIn.TurnIn(
                parallelActor, turnInQuestId, "NPC_TA_VAN_KHANH", Guid.NewGuid().ToString("N"));
        });

        var parallelAccepted = parallelOutcomes.Count(outcome => outcome.Accepted);
        var parallelInvalid = parallelOutcomes.Count(outcome =>
            !outcome.Accepted &&
            string.Equals(outcome.Failure?.Code, QuestErrorCodes.InvalidTransition, StringComparison.Ordinal));
        Check(
            "turnin.parallel_exactly_one_win",
            parallelAccepted == 1 && parallelInvalid == 1,
            $"accepted={parallelAccepted} invalid={parallelInvalid} " +
            $"codes={string.Join(",", parallelOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        var parallelInventory = inventory.GetSnapshot(parallelActor.CharacterId);
        Check(
            "turnin.parallel_single_reward",
            parallelInventory.Currencies.Count == 1 &&
            parallelInventory.Currencies[0].Amount == 20 &&
            parallelInventory.Items.Count == 1,
            $"items={parallelInventory.Items.Count} currencies={parallelInventory.Currencies.Count}");

        // same key in parallel: contention must never double-grant; both threads
        // either replay the stored result or one gets invalid_transition.
        var replayActor = NewPlayer("CHR_SELFCHECK_PARALLEL_REPLAY");
        quests.Accept(replayActor, turnInQuestId);
        foreach (var targetId in new[] { "OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03" })
        {
            quests.RecordVerifiedEvent(
                replayActor, Guid.NewGuid().ToString("N"), QuestProgressEventTypes.InteractClaim,
                targetId, "MAP_BEN_MUA");
        }
        replayActor.X = turnInAnchor.X;
        replayActor.Y = turnInAnchor.Y;

        var sameKey = Guid.NewGuid().ToString("N");
        var sameKeyOutcomes = new TurnInOutcome[2];
        RunBarrierParallel(2, index =>
        {
            sameKeyOutcomes[index] = questTurnIn.TurnIn(
                replayActor, turnInQuestId, "NPC_TA_VAN_KHANH", sameKey);
        });

        var sameKeyAccepted = sameKeyOutcomes.Count(outcome => outcome.Accepted);
        var sameKeyRevisions = sameKeyOutcomes
            .Where(outcome => outcome.Accepted)
            .Select(outcome => outcome.Result!.QuestState.Revision)
            .Distinct()
            .Count();
        Check(
            "turnin.parallel_same_key_contention",
            sameKeyAccepted == 2 && sameKeyRevisions == 1,
            $"accepted={sameKeyAccepted} distinctRevisions={sameKeyRevisions} " +
            $"codes={string.Join(",", sameKeyOutcomes.Select(o => o.Failure?.Code ?? "ok"))}");

        var sameKeyInventory = inventory.GetSnapshot(replayActor.CharacterId);
        Check(
            "turnin.parallel_same_key_single_reward",
            sameKeyInventory.Currencies.Count == 1 &&
            sameKeyInventory.Currencies[0].Amount == 20 &&
            sameKeyInventory.Items.Count == 1,
            $"items={sameKeyInventory.Items.Count} currencies={sameKeyInventory.Currencies.Count}");

        var teleportActor = NewPlayer("CHR_SELFCHECK_TELEPORT");
        var badMapShape = teleport.Teleport(
            teleportActor,
            new TeleportCommand("BEN_MUA", options.SpawnX, options.SpawnY, TeleportReasons.Quest));
        Check(
            "teleport.invalid_map_payload",
            badMapShape.ErrorCode == P1ErrorCodes.InvalidPayload,
            badMapShape.ErrorCode);

        var unknownMap = teleport.Teleport(
            teleportActor,
            new TeleportCommand("MAP_SELFCHECK_UNKNOWN", options.SpawnX, options.SpawnY, TeleportReasons.Quest));
        Check(
            "teleport.unknown_map",
            unknownMap.ErrorCode == TeleportErrorCodes.InvalidMap,
            unknownMap.ErrorCode);

        maps.TryResolve(options.DefaultMapId, out var bounds);
        var outside = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, bounds.XMax + 10, options.SpawnY, TeleportReasons.Quest));
        Check(
            "teleport.out_of_bounds",
            outside.ErrorCode == TeleportErrorCodes.OutOfBounds,
            outside.ErrorCode);

        var badReason = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, options.SpawnX, options.SpawnY, "NOWHERE"));
        Check(
            "teleport.invalid_reason",
            badReason.ErrorCode == TeleportErrorCodes.InvalidReason,
            badReason.ErrorCode);

        var prematureRespawn = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, options.SpawnX, options.SpawnY, TeleportReasons.DeathReturn));
        Check(
            "teleport.death_return_requires_death",
            prematureRespawn.ErrorCode == TeleportErrorCodes.InvalidCondition,
            prematureRespawn.ErrorCode);

        var moved = teleport.Teleport(
            teleportActor,
            new TeleportCommand(options.DefaultMapId, 10, 5, TeleportReasons.Quest));
        Check(
            "teleport.success",
            moved.IsSuccess &&
            teleportActor.X == 10 &&
            teleportActor.Y == 5 &&
            moved.Snapshot!.Revision == 2,
            moved.ErrorCode ?? $"x={teleportActor.X} revision={moved.Snapshot?.Revision}");

        var defeated = NewPlayer("CHR_SELFCHECK_DEFEATED", hp: 0);
        var respawn = teleport.Teleport(
            defeated,
            new TeleportCommand(options.DefaultMapId, options.SpawnX, options.SpawnY, TeleportReasons.DeathReturn));
        Check(
            "teleport.death_return",
            respawn.IsSuccess && respawn.Snapshot!.Self.Hp == 0,
            respawn.ErrorCode);

        var failures = results.Count(result => !result.Passed);
        foreach (var (name, passed, detail) in results)
        {
            if (passed)
            {
                logger.LogInformation("PASS {Check}", name);
            }
            else
            {
                logger.LogError("FAIL {Check}: {Detail}", name, detail);
            }
        }

        logger.LogInformation(
            "Service self-check: {Passed} passed, {Failed} failed, {Total} total.",
            results.Count - failures,
            failures,
            results.Count);

        return failures == 0 ? 0 : 1;
    }

    private sealed class FixedYieldRoller : IYieldRoller
    {
        private readonly int _value;

        public FixedYieldRoller(int value)
        {
            _value = value;
        }

        public int Roll(int minInclusive, int maxInclusive) => _value;
    }

    private sealed class FailOnceInventoryDecorator : IInventoryService
    {
        private readonly IInventoryService _inner;
        private bool _failed;

        public FailOnceInventoryDecorator(IInventoryService inner)
        {
            _inner = inner;
        }

        public InventorySnapshot GetSnapshot(string characterId) =>
            _inner.GetSnapshot(characterId);

        public InventoryOutcome Apply(PlayerSession actor, InventoryMutation? mutation)
        {
            if (!_failed)
            {
                _failed = true;
                return InventoryOutcome.Rejected(
                    InventoryErrorCodes.SlotOccupied, retryable: true, "rewards");
            }

            return _inner.Apply(actor, mutation);
        }
    }

    private sealed class FailOnceQuestDecorator : IQuestService
    {
        private readonly IQuestService _inner;
        private bool _failed;

        public FailOnceQuestDecorator(IQuestService inner)
        {
            _inner = inner;
        }

        public QuestOutcome GetState(string characterId, string questId) =>
            _inner.GetState(characterId, questId);

        public IReadOnlyList<QuestState> GetStates(string characterId) =>
            _inner.GetStates(characterId);

        public QuestOutcome Accept(PlayerSession actor, string questId) =>
            _inner.Accept(actor, questId);

        public IReadOnlyList<QuestState> RecordVerifiedEvent(
            PlayerSession actor,
            string eventId,
            string eventType,
            string recordId,
            string mapId) =>
            _inner.RecordVerifiedEvent(actor, eventId, eventType, recordId, mapId);

        public QuestOutcome TurnIn(PlayerSession actor, string questId)
        {
            if (!_failed)
            {
                _failed = true;
                return QuestOutcome.Rejected(
                    QuestErrorCodes.InvalidTransition, retryable: false, "state");
            }

            return _inner.TurnIn(actor, questId);
        }

        public QuestOutcome RevertTurnIn(PlayerSession actor, string questId) =>
            _inner.RevertTurnIn(actor, questId);

        public QuestOutcome Fail(PlayerSession actor, string questId) =>
            _inner.Fail(actor, questId);
    }

    private sealed class FailOnceLedgerStore : RewardLedgerStore
    {
        private bool _failed;

        public override bool TryRecord(string characterId, string questId, TurnInResult result)
        {
            if (!_failed)
            {
                _failed = true;
                return false;
            }

            return base.TryRecord(characterId, questId, result);
        }
    }

    private static void RunBarrierParallel(int count, Action<int> body)
    {
        using var barrier = new Barrier(count);
        var threads = new Thread[count];
        for (var index = 0; index < count; index++)
        {
            var captured = index;
            threads[index] = new Thread(() =>
            {
                barrier.SignalAndWait();
                body(captured);
            });
            threads[index].Start();
        }

        foreach (var thread in threads)
        {
            thread.Join();
        }
    }
}
