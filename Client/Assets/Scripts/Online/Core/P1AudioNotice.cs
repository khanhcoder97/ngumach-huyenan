namespace NguMach.Client.P1
{
    // Local correlation for a validated command result, not a new server wire event.
    public sealed class P1AudioNotice
    {
        public readonly string eventId, cueKey, semantic;
        public P1AudioNotice(string id, string key, string meaning)
        { eventId = id; cueKey = key; semantic = meaning; }
    }
}
