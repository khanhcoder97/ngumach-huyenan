// OPC-17 checkpoint 3 (O-E) — deterministic combat trace fixtures.
// Sample factory for Codex/host consumers: builds wire-valid P1EventV2
// sequences (cast -> guard/counter -> impact/miss -> death/respawn, two
// owners interleaved, cursor gaps, late ticks) so presenters/VFX binders
// can be exercised without a live server. Fixtures only: the client never
// treats a trace as a server grant. All ids are 32-hex and every cursor
// sequence is strictly increasing, matching P1ClientV2.ValidEvents.
// Pure C#. Owner: OpenCode.

using System;
using System.Globalization;

namespace NguMach.Client.P1
{
    public static class CombatTraceFactory
    {
        private const string IdPrefix = "c0ffee11";

        public static P1CastV2 BasicAttackSample(double aimX = 1.0, double aimY = 0.0)
        {
            return new P1CastV2
            {
                actionKind = "BASIC_ATTACK",
                skillId = null,
                targetId = "ENT_BOSS_BM_05",
                clientTimeUtc = "2026-11-07T00:00:00Z",
                inputSequence = 1,
                aimX = aimX,
                aimY = aimY
            };
        }

        public static P1CastV2 SkillSample(string skillId, string targetId = null, double aimX = 0.0, double aimY = 0.0)
        {
            return new P1CastV2
            {
                actionKind = "SKILL",
                skillId = skillId,
                targetId = targetId,
                clientTimeUtc = "2026-11-07T00:00:00Z",
                inputSequence = 1,
                aimX = aimX,
                aimY = aimY
            };
        }

        // CAST_START -> COUNTER_CONFIRMED -> IMPACT(hit) -> DEATH -> END.
        public static P1EventV2[] HitDeathTrace(
            string castId, string actorId, string targetId,
            long cursorStart = 1, long tickStart = 500)
        {
            return new[]
            {
                Event("CAST_START", castId, actorId, targetId, cursorStart, tickStart, null),
                Event("COUNTER_CONFIRMED", castId, actorId, targetId, cursorStart + 1, tickStart + 1, null),
                Impact(castId, actorId, targetId, cursorStart + 2, tickStart + 2, hit: true, amount: 32, hpDamage: 30, absorbed: 2),
                Event("DEATH", castId, actorId, targetId, cursorStart + 3, tickStart + 3, null),
                Event("END", castId, actorId, targetId, cursorStart + 4, tickStart + 4, null)
            };
        }

        // CAST_START -> MISS -> END (no damage, no death).
        public static P1EventV2[] MissTrace(
            string castId, string actorId, string targetId,
            long cursorStart = 1, long tickStart = 500)
        {
            return new[]
            {
                Event("CAST_START", castId, actorId, targetId, cursorStart, tickStart, null),
                Impact(castId, actorId, targetId, cursorStart + 1, tickStart + 1, hit: false, amount: 0, hpDamage: 0, absorbed: 0),
                Event("END", castId, actorId, targetId, cursorStart + 2, tickStart + 2, null)
            };
        }

        // Cursors jump (gap); the missing cursors belong to another page.
        // Presenters must resync instead of guessing the missing events.
        public static P1EventV2[] GapTrace(
            string castId, string actorId, string targetId,
            long tickStart = 500)
        {
            return new[]
            {
                Event("CAST_START", castId, actorId, targetId, 1, tickStart, null),
                Event("END", castId, actorId, targetId, 5, tickStart + 4, null)
            };
        }

        // Two owners alternating on the same map: cursors interleave, cast
        // ids differ, and neither stream may be read as the other's receipt.
        public static P1EventV2[] TwoOwnersTrace(
            long tickStart = 500,
            string actorA = "CHR_TEST_A", string actorB = "CHR_TEST_B",
            string targetId = "ENT_BOSS_BM_05")
        {
            string castA = Id(1), castB = Id(2);
            return new[]
            {
                Event("CAST_START", castA, actorA, targetId, 1, tickStart, null),
                Event("CAST_START", castB, actorB, targetId, 2, tickStart + 1, null),
                Impact(castA, actorA, targetId, 3, tickStart + 2, hit: true, amount: 32, hpDamage: 30, absorbed: 2),
                Impact(castB, actorB, targetId, 4, tickStart + 3, hit: true, amount: 18, hpDamage: 18, absorbed: 0),
                Event("END", castA, actorA, targetId, 5, tickStart + 4, null),
                Event("END", castB, actorB, targetId, 6, tickStart + 5, null)
            };
        }

        // Impact carries an older server tick than the cast start (slow
        // delivery). Cursors stay monotonic; the tick is what the consumer
        // must order by, not arrival order.
        public static P1EventV2[] LateImpactTrace(
            string castId, string actorId, string targetId,
            long cursorStart = 1, long tickStart = 500)
        {
            return new[]
            {
                Event("CAST_START", castId, actorId, targetId, cursorStart, tickStart, null),
                Impact(castId, actorId, targetId, cursorStart + 1, tickStart - 2, hit: true, amount: 32, hpDamage: 32, absorbed: 0),
                Event("END", castId, actorId, targetId, cursorStart + 2, tickStart + 1, null)
            };
        }

        public static string Id(int index)
        {
            return IdPrefix + index.ToString("x24", CultureInfo.InvariantCulture);
        }

        private static P1EventV2 Event(
            string type, string castId, string actorId, string targetId,
            long cursor, long tick, P1ImpactResultV2 result)
        {
            return new P1EventV2
            {
                eventId = Id((int)(cursor + tick)),
                type = type,
                castId = castId,
                actorId = actorId,
                mapInstanceId = "MI_BEN_MUA_01",
                floorId = "F1",
                emittedAtUtc = "2026-11-07T00:00:00Z",
                cursor = cursor,
                sourceRevision = 1,
                serverTick = tick,
                targetId = targetId,
                targetLifeId = 7,
                targetRevision = 2,
                hitIndex = 1,
                result = result
            };
        }

        private static P1EventV2 Impact(
            string castId, string actorId, string targetId,
            long cursor, long tick, bool hit, int amount, int hpDamage, int absorbed)
        {
            return Event("IMPACT", castId, actorId, targetId, cursor, tick, new P1ImpactResultV2
            {
                hit = hit,
                crit = false,
                immune = false,
                amount = amount,
                absorbed = absorbed,
                hpDamage = hpDamage
            });
        }
    }
}
