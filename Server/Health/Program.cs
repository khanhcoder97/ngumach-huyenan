using System.Text.Json.Serialization;
using Microsoft.Extensions.Options;
using Server.Health.Endpoints;
using Server.Health.Gameplay.Alpha;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;
using Server.Health.Gameplay.Inventory;
using Server.Health.Gameplay.Pets;
using Server.Health.Gameplay.Progress;
using Server.Health.Gameplay.Quests;
using Server.Health.Gameplay.Teleport;
using Server.Health.Smoke;
using Server.Health.World;

var selfCheck = args.Contains("--self-check", StringComparer.Ordinal);
var builder = WebApplication.CreateBuilder(
    selfCheck
        ? args.Where(argument => !string.Equals(argument, "--self-check", StringComparison.Ordinal)).ToArray()
        : args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow;
});
builder.Services.Configure<P1WorldOptions>(
    builder.Configuration.GetSection(P1WorldOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<P1WorldOptions>>().Value);
builder.Services.AddSingleton<ServerClock>();
builder.Services.AddSingleton<IServerClock>(
    serviceProvider => serviceProvider.GetRequiredService<ServerClock>());
builder.Services.AddSingleton<ISessionStore, InMemorySessionStore>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = MapBoundsLoader.DiscoverPath(configuration, environment.ContentRootPath);
    return MapBoundsLoader.Load(path);
});
builder.Services.AddSingleton<ICombatSkillCatalog>(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var directory = CombatSkillCatalogLoader.DiscoverDirectory(
        configuration, environment.ContentRootPath);
    return CombatSkillCatalogLoader.Load(directory);
});
builder.Services.AddSingleton<InMemoryCombatTargetProvider>();
builder.Services.AddSingleton<WorldEntityTargetProvider>();
builder.Services.AddSingleton<ICombatTargetProvider>(serviceProvider =>
    new CompositeCombatTargetProvider(
        serviceProvider.GetRequiredService<WorldEntityTargetProvider>(),
        serviceProvider.GetRequiredService<InMemoryCombatTargetProvider>()));
builder.Services.AddSingleton<ICombatService, InMemoryCombatService>();
builder.Services.Configure<MobBehaviorOptions>(
    builder.Configuration.GetSection(MobBehaviorOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<MobBehaviorOptions>>().Value);
builder.Services.AddSingleton<MobLifecycleService>();
builder.Services.AddSingleton<MobAttackService>();
builder.Services.AddSingleton<IQuestCatalog>(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var directory = QuestCatalogLoader.DiscoverDirectory(
        configuration, environment.ContentRootPath);
    var catalog = QuestCatalogLoader.Load(directory);
    var alphaOptions = serviceProvider.GetRequiredService<AlphaProfileOptions>();
    if (!alphaOptions.Enabled)
    {
        return catalog;
    }

    var overlayDirectory = AlphaQuestCatalogMerger.DiscoverOverlayDirectory(
        environment.ContentRootPath);
    return AlphaQuestCatalogMerger.Merge(
        catalog, QuestCatalogLoader.Load(overlayDirectory));
});
builder.Services.AddSingleton<IQuestStateStore, InMemoryQuestStateStore>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = NarrativeNodeCatalog.Discover(configuration, environment.ContentRootPath);
    return NarrativeNodeCatalog.Load(path);
});
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return LevelProgressionTable.Load(LevelProgressionTable.Discover(environment.ContentRootPath));
});
builder.Services.AddSingleton<QuestXpSnapshotStore>();
builder.Services.AddSingleton<IQuestXpRule>(serviceProvider =>
{
    // The approved alpha progression is the only source that states what a quest
    // reward is worth; with the profile off nothing does, so the shipped resolver
    // keeps answering "unresolved" and XP stays unapplied on the wire.
    var alphaProfile = serviceProvider
        .GetRequiredService<IOptions<AlphaProfileOptions>>().Value;
    return alphaProfile.Enabled
        ? new AlphaQuestXpRules(
            serviceProvider.GetRequiredService<AlphaDesign>().Progression)
        : new UnresolvedQuestXpRules();
});
builder.Services.AddSingleton<ExperienceService>();
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return ItemCatalog.Load(
        ItemCatalogDiscovery.DiscoverDirectory(environment.ContentRootPath));
});
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return ClassPassiveCatalogLoader.Load(
        ClassPassiveCatalogLoader.DiscoverDirectory(environment.ContentRootPath));
});
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return CurrencyCatalogLoader.Load(
        CurrencyCatalogLoader.DiscoverDirectory(environment.ContentRootPath));
});
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return LifeSimCatalogLoader.Load(
        LifeSimCatalogLoader.DiscoverDirectory(environment.ContentRootPath));
});
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return WeeklyBossRotationCatalogLoader.Load(
        WeeklyBossRotationCatalogLoader.DiscoverDirectory(environment.ContentRootPath));
});
// Work order 29 Q5: the `Tiêu hao` rows are classified at boot, so a source cell that
// stops parsing (a new stat label, a percentage outside the wording this loader accepts)
// fails startup instead of silently healing nobody. Loading is not applying: no route
// consumes this yet, because what a client may ask for is a contract decision.
builder.Services.AddSingleton(serviceProvider =>
    ConsumableCatalog.Load(serviceProvider.GetRequiredService<ItemCatalog>()));
builder.Services.AddSingleton<IConsumableService>(serviceProvider => new ConsumableService(
    serviceProvider.GetRequiredService<IInventoryService>(),
    serviceProvider.GetRequiredService<IReadOnlyList<ConsumableEntry>>()));
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return MobEliteVariantCatalog.Load(ProductionTableDiscovery.DiscoverDirectory(
        environment.ContentRootPath, MobEliteVariantCatalog.RelativePath));
});
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return NpcActorRegistry.Load(ProductionTableDiscovery.DiscoverDirectory(
        environment.ContentRootPath, NpcActorRegistry.RelativePath));
});
// QOD-24: the pet and mount table, loaded as data only. There is no companion route and
// no gate for it: nothing in Production_Rules says how a pet enters the damage formula,
// the leash tick or the bag, so the table is read to pin what it claims against the item
// catalogue, not to act on it.
builder.Services.AddSingleton(serviceProvider =>
{
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    return CompanionCatalog.Load(ProductionTableDiscovery.DiscoverDirectory(
        environment.ContentRootPath, CompanionCatalog.RelativePath));
});
builder.Services.AddSingleton<NarrativeFlagStore>();
builder.Services.AddSingleton<NarrativeService>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = WorldRecordLoader.DiscoverPath(configuration, environment.ContentRootPath);
    var baseCatalog = WorldRecordLoader.Load(
        path, serviceProvider.GetRequiredService<MapBoundsCatalog>());
    if (!serviceProvider.GetRequiredService<AlphaProfileOptions>().Enabled)
    {
        return baseCatalog;
    }

    return AlphaOverlayMerger.MergeRecords(
        baseCatalog,
        serviceProvider.GetRequiredService<AlphaDesign>(),
        serviceProvider.GetRequiredService<MapBoundsCatalog>());
});
builder.Services.Configure<AlphaProfileOptions>(
    builder.Configuration.GetSection(AlphaProfileOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<AlphaProfileOptions>>().Value);
builder.Services.Configure<AlphaLootOptions>(
    builder.Configuration.GetSection(AlphaLootOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<AlphaLootOptions>>().Value);
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = AlphaProfileLoader.Discover(configuration, environment.ContentRootPath);
    var design = AlphaProfileLoader.Load(path);
    var maps = serviceProvider.GetRequiredService<MapBoundsCatalog>();
    // Validate against the unmerged base records so overlays can never collide
    // with (or depend on) themselves: the runtime merge stays a pure addition.
    var recordsPath = WorldRecordLoader.DiscoverPath(configuration, environment.ContentRootPath);
    var baseRecords = WorldRecordLoader.Load(recordsPath, maps);
    AlphaProfileValidator.Validate(
        design,
        maps,
        serviceProvider.GetRequiredService<NpcAnchorCatalog>(),
        baseRecords);
    // The v2 twelve-slot vocabulary has to cover every equipment label the canonical
    // catalogue carries; a label it cannot name would only surface as a runtime
    // refusal to equip, so it fails here instead.
    InventoryV2Slots.ValidateCatalogLabels(
        serviceProvider.GetRequiredService<ItemCatalog>());
    return design;
});
builder.Services.AddSingleton<IQuestService, InMemoryQuestService>();
builder.Services.Configure<QuestAcceptOptions>(
    builder.Configuration.GetSection(QuestAcceptOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<QuestAcceptOptions>>().Value);
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = NpcAnchorLoader.DiscoverPath(configuration, environment.ContentRootPath);
    return NpcAnchorLoader.Load(path);
});
builder.Services.AddSingleton<IQuestAcceptService, InMemoryQuestAcceptService>();
builder.Services.Configure<QuestTurnInOptions>(
    builder.Configuration.GetSection(QuestTurnInOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<QuestTurnInOptions>>().Value);
builder.Services.AddSingleton<RewardLedgerStore>();
// P00-05's chapter consequence is written inside the turn-in transaction and
// revoked if a later step of that transaction rolls back. The store records
// nothing while P1:AlphaProfile is off, so every other profile's turn-in is
// byte-identical to what it was before this seam existed.
builder.Services.AddSingleton<ChapterUnlockStore>();
builder.Services.AddSingleton<IChapterUnlockSink>(sp =>
    sp.GetRequiredService<ChapterUnlockStore>());
builder.Services.AddSingleton<IQuestTurnInService, InMemoryQuestTurnInService>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var directory = MapTopologyLoader.DiscoverDirectory(
        configuration, environment.ContentRootPath);
    var maps = serviceProvider.GetRequiredService<MapBoundsCatalog>();
    return MapTopologyLoader.Load(directory, maps);
});
builder.Services.AddSingleton<IWorldGeometryService, WorldGeometryService>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = WorldEntityLoader.DiscoverPath(configuration, environment.ContentRootPath);
    var baseCatalog = WorldEntityLoader.Load(
        path, serviceProvider.GetRequiredService<MapBoundsCatalog>());
    if (!serviceProvider.GetRequiredService<AlphaProfileOptions>().Enabled)
    {
        return baseCatalog;
    }

    return AlphaOverlayMerger.MergeEntities(
        baseCatalog,
        serviceProvider.GetRequiredService<AlphaDesign>(),
        serviceProvider.GetRequiredService<MapBoundsCatalog>());
});
builder.Services.AddSingleton(serviceProvider => new WorldEntityRegistry(
    serviceProvider.GetRequiredService<WorldEntityCatalog>(),
    serviceProvider.GetRequiredService<IServerClock>()));
builder.Services.AddSingleton<IInventoryStateStore, InMemoryInventoryStateStore>();
// The catalog is passed in so a grant that does not name a durability takes the
// canonical CSV value instead of silently storing 0.
builder.Services.AddSingleton<IInventoryService>(serviceProvider => new InMemoryInventoryService(
    serviceProvider.GetRequiredService<IInventoryStateStore>(),
    serviceProvider.GetRequiredService<ItemCatalog>()));
builder.Services.Configure<EquipmentOptions>(
    builder.Configuration.GetSection(EquipmentOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<EquipmentOptions>>().Value);
builder.Services.AddSingleton<IEquipmentService, EquipmentService>();
// The v2 twelve-slot surface beside the frozen v1 five: same store, same aggregate
// revision, different vocabulary. Its routes are mapped only under P1:AlphaProfile.
builder.Services.AddSingleton<IEquipmentV2Service, EquipmentV2Service>();
builder.Services.AddSingleton<ITeleportService, InMemoryTeleportService>();
builder.Services.Configure<InteractionOptions>(
    builder.Configuration.GetSection(InteractionOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<InteractionOptions>>().Value);
builder.Services.AddSingleton<IYieldRoller, SystemYieldRoller>();
builder.Services.AddSingleton<GatherClaimStore>();
builder.Services.AddSingleton<IInteractionService, InMemoryInteractionService>();
builder.Services.Configure<P1CombatDamageOptions>(
    builder.Configuration.GetSection(P1CombatDamageOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<P1CombatDamageOptions>>().Value);
builder.Services.AddSingleton<CombatDamageFeature>();
builder.Services.Configure<CombatEventStreamOptions>(
    builder.Configuration.GetSection(CombatEventStreamOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<CombatEventStreamOptions>>().Value);
builder.Services.AddSingleton<CombatEventStore>();
builder.Services.Configure<P1CombatV2Options>(
    builder.Configuration.GetSection(P1CombatV2Options.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<P1CombatV2Options>>().Value);
builder.Services.AddSingleton<InMemoryCombatV2Service>();
builder.Services.AddSingleton<MobCombatStateStore>();
builder.Services.AddSingleton<ICombatRollSource, CombatRngRollSource>();
builder.Services.AddSingleton<GuardWindowStore>();
// DEC-DEATH-RETURN-20261105: every player-damage path commits its life/death
// record through this ledger, so it is a single instance for the process and is
// keyed by character, never by session.
builder.Services.AddSingleton<PlayerLifeLedger>();
builder.Services.AddSingleton<GuardDefenseService>();
builder.Services.AddSingleton<DashMovementService>();
builder.Services.AddSingleton<CombatStatusProjection>();
builder.Services.AddSingleton<MobTelegraphProjection>();
builder.Services.Configure<DeathReturnOptions>(
    builder.Configuration.GetSection(DeathReturnOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<DeathReturnOptions>>().Value);
// The approved alpha rules decide the anchor, the HP formula and the cooldown;
// without that profile the service falls back to the labelled DEV fixture shape
// it has always had (spawn anchor, no restore, no cooldown) and no route exists.
builder.Services.AddSingleton(serviceProvider => new DeathReturnService(
    serviceProvider.GetRequiredService<ISessionStore>(),
    serviceProvider.GetRequiredService<MapBoundsCatalog>(),
    serviceProvider.GetRequiredService<P1WorldOptions>(),
    serviceProvider.GetRequiredService<DeathReturnOptions>(),
    serviceProvider.GetRequiredService<GuardWindowStore>(),
    serviceProvider.GetRequiredService<CombatTickEngine>(),
    serviceProvider.GetRequiredService<PlayerLifeLedger>(),
    serviceProvider.GetRequiredService<IServerClock>(),
    serviceProvider.GetRequiredService<AlphaProfileOptions>().Enabled
        ? serviceProvider.GetRequiredService<AlphaDesign>().DeathReturn
        : null));
builder.Services.AddSingleton<CombatTickEngine>();
builder.Services.AddSingleton<LootReceiptLedger>();
builder.Services.AddSingleton<LootGrantLedger>();
// Who may be paid for a kill is the alpha profile's answer; every other profile
// resolves to the same block the shipped bundle has always carried.
builder.Services.AddSingleton<ILootGrantPolicy>(serviceProvider => new AlphaLootGrantPolicy(
    serviceProvider.GetRequiredService<AlphaDesign>(),
    serviceProvider.GetRequiredService<AlphaProfileOptions>(),
    serviceProvider.GetRequiredService<AlphaLootOptions>()));
builder.Services.AddSingleton<LootGrantService>();
builder.Services.AddSingleton<MobSpawnGroupService>();
builder.Services.AddSingleton<WorldEntityProjectionService>();
builder.Services.AddSingleton<WorldAoiProjectionService>();
builder.Services.AddSingleton<AlphaWaveTrialService>();
builder.Services.AddSingleton<AlphaEscortService>();
builder.Services.AddSingleton<AlphaBossEncounterService>();
// The tick engine casts at the alpha quest boss through this bridge; with the
// profile OFF the encounter holds no instance so the impact path is unchanged.
builder.Services.AddSingleton<ICombatBossBridge>(sp =>
    sp.GetRequiredService<AlphaBossEncounterService>());
// Resolved mob deaths are pushed to the escort machine instead of inferred from
// polled world state; with the profile OFF the escort holds no instance, so
// every kill notification is dropped and the mob path is unchanged.
builder.Services.AddSingleton<ICombatKillSink>(sp =>
    sp.GetRequiredService<AlphaEscortService>());
builder.Services.AddHostedService<WorldTickBackgroundService>();

var app = builder.Build();

var worldOptions = app.Services.GetRequiredService<IOptions<P1WorldOptions>>().Value;
var mapBounds = app.Services.GetRequiredService<MapBoundsCatalog>();
P1WorldOptionsValidator.Validate(worldOptions, mapBounds);
app.Logger.LogInformation("Loaded map bounds for {MapCount} maps.", mapBounds.Count);

var combatSkills = app.Services.GetRequiredService<ICombatSkillCatalog>();
app.Logger.LogInformation("Loaded {SkillCount} combat skills.", combatSkills.Count);

var quests = app.Services.GetRequiredService<IQuestCatalog>();
app.Logger.LogInformation("Loaded quest definitions: {QuestCount}.", quests.Count);

var itemCatalog = app.Services.GetRequiredService<ItemCatalog>();
app.Logger.LogInformation("Loaded item catalogue: {ItemCount} items.", itemCatalog.Count);

var weeklyRotation = app.Services.GetRequiredService<WeeklyBossRotationCatalog>();
app.Logger.LogInformation(
    "Loaded weekly boss rotation: {SlotCount} slots (data only - no scheduler, rank or reward contract exists yet).",
    weeklyRotation.Count);

var lifeSim = app.Services.GetRequiredService<LifeSimCatalog>();
app.Logger.LogInformation(
    "Loaded life sim catalog: {ContentCount} entries ({Crops} CROP, {Fish} FISH) - timings and caps are data, not a running gather loop.",
    lifeSim.Count,
    lifeSim.CountOfType("CROP"),
    lifeSim.CountOfType("FISH"));

var eliteVariants = app.Services.GetRequiredService<IReadOnlyList<MobEliteVariant>>();
app.Logger.LogInformation(
    "Loaded elite variant table: {RowCount} elites across {Profiles} profiles (hp {MinHp}–{MaxHp}x, pvp allowed: {Pvp}) - the runtime mob-stat bundle still uses its own multipliers, which the self-check compares.",
    eliteVariants.Count,
    eliteVariants.Select(elite => elite.VariantProfileId).Distinct().Count(),
    eliteVariants.Min(elite => elite.HpMultiplier),
    eliteVariants.Max(elite => elite.HpMultiplier),
    eliteVariants.Any(elite => elite.PvpAllowed) ? "yes somewhere" : "never");

var npcActors = app.Services.GetRequiredService<IReadOnlyList<NpcActorDefinition>>();
app.Logger.LogInformation(
    "Loaded NPC actor registry: {RowCount} NPCs, {ServiceCount} carrying a service token, none combat-targetable - service availability is data, not a route.",
    npcActors.Count,
    npcActors.Count(actor => actor.InteractionServiceId != "NONE"));

var companions = app.Services.GetRequiredService<IReadOnlyList<CompanionEntry>>();
app.Logger.LogInformation(
    "Loaded pet and mount table: {CompanionCount} companions (leash {RangeWu} WU, fed every {FeedHours}h for cosmetics only) and {MountCount} cosmetic mounts (no combat) - the item catalogue names a different creature for every one of these ids, which the self-check pins; there is no companion route.",
    companions.Count(entry => entry.IsCompanion),
    companions.First(entry => entry.IsCompanion).OwnerRangeWu,
    companions.First(entry => entry.IsCompanion).FeedCooldownHours,
    companions.Count(entry => !entry.IsCompanion));

var consumableRules = app.Services.GetRequiredService<IReadOnlyList<ConsumableEntry>>();
app.Logger.LogInformation(
    "Loaded consumable catalogue: {RowCount} rows ({Sourced} percentage rules, {Unsupported} effects with no subsystem here, {Revive} framed as a revive) - domain only, no use route.",
    consumableRules.Count,
    consumableRules.Count(entry => entry.Kind == ConsumableEffectKind.RestorePercent),
    consumableRules.Count(entry => entry.Kind == ConsumableEffectKind.Unsupported),
    consumableRules.Count(entry => entry.ReviveRequired));

var currencies = app.Services.GetRequiredService<CurrencyCatalog>();
app.Logger.LogInformation(
    "Loaded currency catalogue: {CurrencyCount} currencies ({CharacterScoped} character-scoped, " +
    "{AccountScoped} account-scoped, {Tradeable} tradeable - caps are data, not enforced yet).",
    currencies.Count,
    currencies.CountWhere(currency => currency.StorageScope == "character"),
    currencies.CountWhere(currency => currency.StorageScope == "account"),
    currencies.CountWhere(currency => currency.Tradeable));

var classPassives = app.Services.GetRequiredService<ClassPassiveCatalog>();
app.Logger.LogInformation(
    "Loaded class passive catalogue: {PassiveCount} passives across {ClassCount} classes " +
    "(data only - no passive is applied to combat yet).",
    classPassives.Count,
    classPassives.SupportedClassIds.Count);

var narrativeNodes = app.Services.GetRequiredService<NarrativeNodeCatalog>();
app.Logger.LogInformation(
    "Loaded narrative nodes: {NodeCount} (flags {FlagCount}).",
    narrativeNodes.Count,
    narrativeNodes.Flags.Count);

var npcAnchors = app.Services.GetRequiredService<NpcAnchorCatalog>();
NpcAnchorValidator.Validate(npcAnchors, mapBounds);
app.Logger.LogInformation("Loaded NPC anchors: {AnchorCount}.", npcAnchors.Count);

var topology = app.Services.GetRequiredService<WorldGeometryCatalog>();
app.Logger.LogInformation(
    "Loaded topology bundles: {BundleCount} (reviewed {ReviewedCount}).",
    topology.Count,
    topology.ReviewedCount);

var mobBehavior = app.Services.GetRequiredService<MobBehaviorOptions>();
MobBehaviorOptionsValidator.Validate(mobBehavior);
if (mobBehavior.Enabled)
{
    app.Logger.LogWarning(
        "DEV FIXTURE: P1:MobBehavior is enabled with labelled fixture radii, " +
        "telegraph and recovery durations; mob damage still requires " +
        "P1:CombatDamage and uses REFERENCE_L5 stats, not balance.");
}

var combatDamage = app.Services.GetRequiredService<CombatDamageFeature>();
if (combatDamage.Enabled)
{
    app.Logger.LogWarning(
        "DEV STUB: P1:CombatDamage is enabled with the REFERENCE_L5 mob stat " +
        "bundle (DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION); the QOD-16 proposal " +
        "is not approved yet, so every damage number in flight is a DEV fixture, " +
        "not reviewed production balance.");
}

var combatV2 = app.Services.GetRequiredService<P1CombatV2Options>();
if (combatV2.Enabled)
{
    app.Logger.LogWarning(
        "DEV STUB: P1:CombatV2 is enabled — /p1/v2/world, /p1/v2/combat and " +
        "/p1/v2/events use the QOD-17 tick engine for the supported DEV subset.");
}

var deathReturn = app.Services.GetRequiredService<DeathReturnOptions>();
DeathReturnOptionsValidator.Validate(
    deathReturn,
    worldOptions,
    app.Services.GetRequiredService<AlphaProfileOptions>().Enabled);
if (deathReturn.Enabled)
{
    app.Logger.LogWarning(
        "DEV FIXTURE: P1:DeathReturn is enabled. With P1:AlphaProfile off the anchor " +
        "is P1World SpawnX/SpawnY clamped to the actor's map bounds (not a reviewed " +
        "safe anchor), RestoreHpFixture {RestoreHp} is a configured starting HP rather " +
        "than the approved formula, and there is no cooldown because no source defines " +
        "one; in that shape the route stays unmapped and only in-process callers reach " +
        "it. With both gates on the anchor, HP, cooldown and penalties come from " +
        "DEC-DEATH-RETURN-20261105.",
        deathReturn.RestoreHpFixture);
}

var combatEventStreamOptions = app.Services.GetRequiredService<CombatEventStreamOptions>();
CombatEventStreamOptionsValidator.Validate(combatEventStreamOptions);
app.Logger.LogInformation(
    "Combat event stream: {Capacity} events per session, page {PageSize}.",
    combatEventStreamOptions.CapacityPerSession,
    combatEventStreamOptions.MaxPageSize);

var worldEntities = app.Services.GetRequiredService<WorldEntityRegistry>();
app.Logger.LogInformation(
    "Loaded world entities: {EntityCount} (mobs {MobCount}, bosses {BossCount}, " +
    "nodes {NodeCount}, npcs {NpcCount}).",
    worldEntities.Count,
    worldEntities.All.Count(entity => entity.Kind == WorldEntityKinds.Mob),
    worldEntities.All.Count(entity => entity.Kind == WorldEntityKinds.Boss),
    worldEntities.All.Count(entity => entity.Kind == WorldEntityKinds.GatherNode ||
                                      entity.Kind == WorldEntityKinds.Interactable),
    worldEntities.All.Count(entity => entity.Kind == WorldEntityKinds.Npc));

foreach (var questId in quests.QuestIds)
{
    if (!quests.TryGet(questId, out var questDefinition))
    {
        continue;
    }

    if (!npcAnchors.HasAnchorFor(questDefinition.StartNpcId))
    {
        throw new InvalidOperationException(
            $"Quest '{questId}' start NPC '{questDefinition.StartNpcId}' has no anchor.");
    }

    // A blocked quest may not know its turn-in NPC yet; the blocked step names
    // that gap, so only a known NPC anchor is checked here.
    if (questDefinition.TurnInNpcId is { } turnInNpcId &&
        !npcAnchors.HasAnchorFor(turnInNpcId))
    {
        throw new InvalidOperationException(
            $"Quest '{questId}' turn-in NPC '{turnInNpcId}' has no anchor.");
    }
}

var worldRecords = app.Services.GetRequiredService<WorldRecordCatalog>();
app.Logger.LogInformation(
    "Loaded world records: {RecordCount}.", worldRecords.Count);
var alphaDesign = app.Services.GetRequiredService<AlphaDesign>();
var alphaOptions = app.Services.GetRequiredService<AlphaProfileOptions>();
app.Logger.LogInformation(
    "Loaded alpha profile {DecisionId} ({Status}) with {OverlayCount} overlay records; boss {BossProfile}.",
    alphaDesign.DecisionId,
    alphaDesign.Status,
    alphaDesign.OverlayRecords.Count,
    alphaDesign.Boss.ProfileId);
if (alphaOptions.Enabled)
{
    var runtimeEntityCount = alphaDesign.OverlayRecords.Count(overlay =>
        AlphaOverlayMerger.HasRuntimeEntity(overlay.Kind));
    app.Logger.LogWarning(
        "PRIVATE ALPHA: P1:AlphaProfile is enabled; {OverlayCount} overlay records, " +
        "{EntityCount} overlay entities and {QuestCount} alpha quest definitions " +
        "(P00-02..05 unblocked, C1-01 added) are merged into the Bến Mưa world. " +
        "The training-wave hazard stays record-only (no wire hazard kind); the wave " +
        "trial, the P00-04 escort and the P00-05 encounter tick as domain state. " +
        "Production gates remain OFF.",
        alphaDesign.OverlayRecords.Count,
        runtimeEntityCount,
        quests.Count);
}

// The loot payout switch is validated against the profile that owns the only coin
// band, so no other profile can pay it out by turning one flag on.
var alphaLootOptions = app.Services.GetRequiredService<AlphaLootOptions>();
AlphaLootPolicy.Validate(alphaLootOptions, alphaOptions, alphaDesign);
if (AlphaLootPolicy.EffectiveGrantEnabled(alphaLootOptions, alphaOptions, alphaDesign))
{
    app.Logger.LogWarning(
        "PRIVATE ALPHA LOOT: P1:AlphaLoot:GrantEnabled is on with P1:AlphaProfile, so a " +
        "resolved mob kill rolls {CoinMin}..{CoinMax} coin and the sourced recipe items, " +
        "once per (profile, character, death, life, group). The design states this band as " +
        "alpha-only seed data, not a production economy approval.",
        alphaDesign.Loot.CoinMinExpression,
        alphaDesign.Loot.CoinMaxExpression);
}

QuestCatalogValidator.Validate(quests, worldRecords, npcAnchors);
InteractionContentValidator.Validate(worldEntities, worldRecords);

var interactionOptions = app.Services.GetRequiredService<InteractionOptions>();
InteractionOptionsValidator.Validate(interactionOptions);
if (interactionOptions.Enabled)
{
    app.Logger.LogWarning(
        "DEV FIXTURE: P1:Interact is enabled with AssumedProfessionLevel={Level} " +
        "and respawn fixtures; no reviewed gathering topology bundle exists.",
        interactionOptions.AssumedProfessionLevel);
}

var questAcceptOptions = app.Services.GetRequiredService<QuestAcceptOptions>();
QuestAcceptOptionsValidator.Validate(questAcceptOptions);
if (questAcceptOptions.Enabled)
{
    app.Logger.LogWarning(
        "DEV STUB: P1:QuestAccept is enabled. Interaction line-of-sight is not " +
        "enforced because no walkability bundle exists.");
}

var questTurnInOptions = app.Services.GetRequiredService<QuestTurnInOptions>();
QuestTurnInOptionsValidator.Validate(questTurnInOptions);
if (questTurnInOptions.Enabled)
{
    app.Logger.LogWarning(
        "DEV STUB: P1:QuestTurnIn is enabled. Reward ledger is in-memory " +
        "and XP applied=false; no reviewed walkability bundle exists.");
}

var equipmentOptions = app.Services.GetRequiredService<EquipmentOptions>();
if (equipmentOptions.Enabled)
{
    app.Logger.LogWarning(
        "DEV STUB: P1:Equipment is enabled. Equip/unequip move metadata only — " +
        "no stats reach combat while DEC-023 is unresolved. The approved 5-slot " +
        "wire enum folds the six accessory labels into ACCESSORY and refuses " +
        "Quần/Găng (no wire token), so those items stay not_equippable.");
}

if (selfCheck)
{
    Environment.ExitCode = ServiceSelfCheck.Run(app.Services, app.Logger);
    return;
}

const string CorrelationIdHeader = "X-Correlation-ID";
const int MaxCorrelationIdLength = 64;

app.Use(async (context, next) =>
{
    var incomingId = context.Request.Headers.TryGetValue(CorrelationIdHeader, out var incoming)
        ? incoming.ToString().Trim()
        : string.Empty;
    var isSafeId = incomingId.Length is > 0 and <= MaxCorrelationIdLength &&
                   incomingId.All(character => char.IsAsciiLetterOrDigit(character) ||
                                               character is '-' or '_' or '.');

    if (!isSafeId)
    {
        context.TraceIdentifier = Guid.NewGuid().ToString();
    }
    else
    {
        context.TraceIdentifier = incoming.ToString().Trim();
    }

    context.Response.OnStarting(() =>
    {
        context.Response.Headers[CorrelationIdHeader] = context.TraceIdentifier;
        return Task.CompletedTask;
    });

    await next();
});

app.MapGet("/health", (HttpContext context) =>
{
    var correlationId = context.TraceIdentifier;

    app.Logger.LogInformation("Health check requested. CorrelationId: {CorrelationId}", correlationId);

    return Results.Ok(new
    {
        status = "ok",
        service = "ngu-mach-huyen-an-server",
        correlationId
    });
});

app.MapP1Endpoints();

app.Run();
