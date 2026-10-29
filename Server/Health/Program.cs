using System.Text.Json.Serialization;
using Microsoft.Extensions.Options;
using Server.Health.Endpoints;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;
using Server.Health.Gameplay.Inventory;
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
builder.Services.AddSingleton<IQuestCatalog>(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var directory = QuestCatalogLoader.DiscoverDirectory(
        configuration, environment.ContentRootPath);
    return QuestCatalogLoader.Load(directory);
});
builder.Services.AddSingleton<IQuestStateStore, InMemoryQuestStateStore>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = WorldRecordLoader.DiscoverPath(configuration, environment.ContentRootPath);
    return WorldRecordLoader.Load(
        path, serviceProvider.GetRequiredService<MapBoundsCatalog>());
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
    return WorldEntityLoader.Load(
        path, serviceProvider.GetRequiredService<MapBoundsCatalog>());
});
builder.Services.AddSingleton(serviceProvider => new WorldEntityRegistry(
    serviceProvider.GetRequiredService<WorldEntityCatalog>(),
    serviceProvider.GetRequiredService<IServerClock>()));
builder.Services.AddSingleton<IInventoryStateStore, InMemoryInventoryStateStore>();
builder.Services.AddSingleton<IInventoryService, InMemoryInventoryService>();
builder.Services.AddSingleton<ITeleportService, InMemoryTeleportService>();
builder.Services.Configure<InteractionOptions>(
    builder.Configuration.GetSection(InteractionOptions.SectionName));
builder.Services.AddSingleton(serviceProvider =>
    serviceProvider.GetRequiredService<IOptions<InteractionOptions>>().Value);
builder.Services.AddSingleton<IYieldRoller, SystemYieldRoller>();
builder.Services.AddSingleton<GatherClaimStore>();
builder.Services.AddSingleton<IInteractionService, InMemoryInteractionService>();
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
        "DEV FIXTURE: P1:MobBehavior is enabled with labelled fixture radii; " +
        "no damage or canonical mob stats are applied.");
}

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

    if (!npcAnchors.HasAnchorFor(questDefinition.TurnInNpcId))
    {
        throw new InvalidOperationException(
            $"Quest '{questId}' turn-in NPC '{questDefinition.TurnInNpcId}' has no anchor.");
    }
}

var worldRecords = app.Services.GetRequiredService<WorldRecordCatalog>();
app.Logger.LogInformation(
    "Loaded world records: {RecordCount}.", worldRecords.Count);
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
