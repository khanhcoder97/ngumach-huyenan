using System;
using System.Text.Json;
using Server.Health.World;
using Server.Health.Gameplay.Combat;

// Synthetic reservation fixture using the actual server queue type. No mock
// queue, no source patch, and no claim of a full mob/guard HTTP encounter.
var defender = new PlayerSession("review-session", "CHR_REVIEW_GUARD", "CLASS_MINH_KIEM",
    "MAP_BEN_MUA", 40, 0, 100, 100, 50, 50, DateTimeOffset.UtcNow);
var windows = new GuardWindowStore();
var window = new GuardWindowState
{
    Defender = defender, SessionId = defender.SessionId,
    GuardCastId = new string('f', 32), CastStartTick = 100,
    FacingX = 1, FacingY = 0, AttackSnapshot = 20, CounterCoefficient = 1.8,
    MapId = defender.MapId, FloorId = defender.FloorId,
    GuardDurationTicks = 8, WhiffDurationTicks = 20,
    CounterSourceEntityId = "ENT_REVIEW_SOURCE", CounterSourceLifeId = 1,
    CounterTick = 102, ConfirmationCount = 1
};
windows.Open(window);
var atDueTick = windows.PendingCounters(102).Count;
// Background clock is wall time and PeriodicTimer can coalesce callbacks:
// next actual callback may be 103, even though a counter was due at 102.
var afterSkippedTick = windows.PendingCounters(103).Count;
var evidence = new
{
    scope = "Actual GuardWindowStore queue, synthetic reservation, not full guard HTTP",
    dueTick = window.CounterTick,
    exactDuePending = atDueTick,
    nextObservedTick = 103,
    overduePending = afterSkippedTick,
    counterResolved = window.CounterResolved,
    expected = "Unresolved overdue work must remain eligible for exactly one resolution",
    status = atDueTick == 1 && afterSkippedTick == 1 ? "PASS" : "FAIL"
};
Console.WriteLine("QUEUE_EVIDENCE " + JsonSerializer.Serialize(evidence));
return evidence.status == "PASS" ? 0 : 1;
