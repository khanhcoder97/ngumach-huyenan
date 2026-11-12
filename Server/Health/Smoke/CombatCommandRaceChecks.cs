using Server.Health.Gameplay.Combat;
using Server.Health.World;

namespace Server.Health.Smoke;

internal static class CombatCommandRaceChecks
{
    public static void Run(ICombatSkillCatalog catalog, Func<string, PlayerSession> create,
        Action<string, bool, string?> check)
    {
        foreach (bool differentPayload in new[] { false, true })
        {
            var actor = create(differentPayload ? "CHR_RACE_CONFLICT" : "CHR_RACE_REPLAY");
            using var catalogEntered = new CountdownEvent(2);
            using var threadsReady = new CountdownEvent(2);
            var stream = new CombatEventStore(new CombatEventStreamOptions());
            var service = new InMemoryCombatV2Service(new EntryProbeCatalog(catalog, catalogEntered), stream, new ServerClock());
            var first = new CombatV2Intent(CombatV2Actions.Skill, "SK-MK-01", null, 1, 1, 0, null);
            var second = differentPayload ? first with { SkillId = "SK-MK-03", InputSequence = 2 } : first;
            Task<CombatV2Outcome> Start(CombatV2Intent intent) => Task.Factory.StartNew(() =>
            {
                threadsReady.Signal();
                return service.Resolve(actor, actor.SessionId, intent, new string('a', 32));
            }, CancellationToken.None, TaskCreationOptions.LongRunning, TaskScheduler.Default);
            Task<CombatV2Outcome>[] requests;
            lock (actor.SyncRoot)
            {
                requests = [Start(first), Start(second)];
                if (!threadsReady.Wait(TimeSpan.FromSeconds(5))) throw new InvalidOperationException("Race workers did not start.");
                // Before the fix both requests can pass the cache and reach the catalog
                // while side effects wait for this lock. With atomic dedupe they wait
                // before the cache; releasing the lock must yield one charge either way.
                catalogEntered.Wait(TimeSpan.FromMilliseconds(300));
            }
            if (!Task.WaitAll(requests, TimeSpan.FromSeconds(5))) throw new InvalidOperationException("Race workers did not complete.");
            var outcomes = requests.Select(t => t.Result).ToArray();
            var accepted = outcomes.Where(o => o.Accepted).ToArray();
            var fresh = accepted.Where(o => !o.Replayed).ToArray();
            check(differentPayload ? "combatv2.concurrent_conflict" : "combatv2.concurrent_replay",
                fresh.Length == 1 && actor.Mp == 50 - fresh[0].Result!.MpCost &&
                stream.Read(actor.SessionId, 0, 100).Events.Count == 1 &&
                (differentPayload
                    ? accepted.Length == 1 && outcomes.Count(o => o.Failure?.Code == CombatErrorCodes.IdempotencyConflict) == 1
                    : accepted.Length == 2 && accepted.Count(o => o.Replayed) == 1 && ReferenceEquals(accepted[0].Result, accepted[1].Result)),
                $"fresh={fresh.Length} accepted={accepted.Length} mp={actor.Mp}");
        }
    }
    private sealed class EntryProbeCatalog(ICombatSkillCatalog inner, CountdownEvent entered) : ICombatSkillCatalog
    {
        public int Count => inner.Count;
        public bool TryGet(string id, out CombatSkillDefinition skill)
        {
            entered.Signal();
            return inner.TryGet(id, out skill);
        }
    }
}
