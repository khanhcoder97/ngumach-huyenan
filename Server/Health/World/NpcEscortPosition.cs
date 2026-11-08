namespace Server.Health.World;

// Work order 30 item 3: the escorted actor walks on the server tick, so its position
// belongs to the escort domain. The world read model has to publish that position instead
// of leaving the anchor static, because the alternative is a client that infers the path -
// which is what the standing rule forbids ("every gameplay mutation is validated by the
// server", and the same logic applies to what a client is shown).
//
// The answer is owner-scoped on purpose. An escort attempt is per character, so a second
// player standing on the same map must keep seeing the canonical anchor rather than
// someone else's NPC mid-walk, and the source names the entity it moves so the projection
// can prove it is overriding that actor and nothing else.
public interface INpcEscortPositionSource
{
    // True only when this character has a live escort attempt and the source can name the
    // single world entity it is moving. A production profile never gets here: the
    // projection is wired to a source only when the alpha profile is enabled.
    bool TryGetEscortPosition(
        string characterId, out string npcEntityId, out double x, out double y);
}
