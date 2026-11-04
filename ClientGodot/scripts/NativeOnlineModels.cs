#nullable enable
using System;
using NguMach.Client.P1;

namespace Ngumach.VisualReboot;

/// <summary>A detached, per-publication frame. None of its mutable DTOs are shared
/// with P1Client or a different published frame. Receipts never synthesize money,
/// inventory instances, damage, HP or quest progress.</summary>
public sealed class NativeOnlineFrame
{
    public string SessionId { get; init; } = "";
    public P1ConnectionState ConnectionState { get; init; } = P1ConnectionState.Disconnected;
    public string Message { get; init; } = "";
    public P1World? World { get; init; }
    public P1WorldV2? WorldV2 { get; init; }
    public P1Quest[] Quests { get; init; } = Array.Empty<P1Quest>();
    public P1Inventory? Inventory { get; init; }
    public P1EventV2[] Events { get; init; } = Array.Empty<P1EventV2>();
    // Edge notifications: cleared for the next poll/frame, never held as state.
    public string? AcceptedAction { get; init; }
    public string? AcceptedSkill { get; init; }
    public bool ScenarioComplete { get; init; }
    public int Assertions { get; init; }
}
