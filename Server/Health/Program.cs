using System.Text.Json.Serialization;
using Microsoft.Extensions.Options;
using Server.Health.Endpoints;
using Server.Health.Gameplay.Inventory;
using Server.Health.Gameplay.Teleport;
using Server.Health.World;

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow;
});
builder.Services.Configure<P1WorldOptions>(
    builder.Configuration.GetSection(P1WorldOptions.SectionName));
builder.Services.AddSingleton<ServerClock>();
builder.Services.AddSingleton<ISessionStore, InMemorySessionStore>();
builder.Services.AddSingleton<IInventoryStateStore, InMemoryInventoryStateStore>();
builder.Services.AddSingleton<IInventoryService, InMemoryInventoryService>();
builder.Services.AddSingleton<ITeleportService, InMemoryTeleportService>();
builder.Services.AddSingleton(serviceProvider =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var environment = serviceProvider.GetRequiredService<IHostEnvironment>();
    var path = MapBoundsLoader.DiscoverPath(configuration, environment.ContentRootPath);
    return MapBoundsLoader.Load(path);
});

var app = builder.Build();

var worldOptions = app.Services.GetRequiredService<IOptions<P1WorldOptions>>().Value;
var mapBounds = app.Services.GetRequiredService<MapBoundsCatalog>();
P1WorldOptionsValidator.Validate(worldOptions, mapBounds);
app.Logger.LogInformation("Loaded map bounds for {MapCount} maps.", mapBounds.Count);

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
