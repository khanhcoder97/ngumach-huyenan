using System.Text.Json.Serialization;
using Microsoft.Extensions.Options;
using Server.Health.Endpoints;
using Server.Health.Gameplay.Alpha;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;
using Server.Health.Gameplay.Inventory;
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
builder.Services.AddSingleton<IInventoryService, InMemoryInventoryService>();
builder.Services.Configure<EquipmentOptions>(
    builder.Configuration.GetSection(EquipmentOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<EquipmentOptions>>().Value);
builder.Services.AddSingleton<IEquipmentService, EquipmentService>();
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
builder.Services.AddSingleton<GuardDefenseService>();
builder.Services.AddSingleton<DashMovementService>();
builder.Services.AddSingleton<CombatStatusProjection>();
builder.Services.AddSingleton<MobTelegraphProjection>();
builder.Services.Configure<DeathReturnOptions>(
    builder.Configuration.GetSection(DeathReturnOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<DeathReturnOptions>>().Value);
builder.Services.AddSingleton<DeathReturnService>();
builder.Services.AddSingleton<CombatTickEngine>();
builder.Services.AddSingleton<LootReceiptLedger>();
builder.Services.AddSingleton<LootGrantLedger>();
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
DeathReturnOptionsValidator.Validate(deathReturn, worldOptions);
if (deathReturn.Enabled)
{
    app.Logger.LogWarning(
        "DEV FIXTURE: P1:DeathReturn is enabled. The anchor is P1World SpawnX/SpawnY " +
        "clamped to the actor's map bounds, not a reviewed safe anchor, and " +
        "RestoreHpFixture {RestoreHp} is a configured starting HP, not a produced " +
        "restore rule; no penalty is applied because no source defines one. Nothing " +
        "reaches it over HTTP until the QOD-18 DeathReturn contract is approved.",
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
