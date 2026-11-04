// OPC-15 O1 (WO26) — Strict validation for encounter snapshots.
// Wire shape authority: encounter_snapshot_v1_reference_20261104.json (design baseline),
// bound to the published QOD-21 Q2 schema `EncounterSnapshotV1.schema.json`:
// additionalProperties:false at every object, required fields, exact enum casing,
// ID patterns, finite numbers, shape-specific semantics and owner/bounds checks.
// Published move states are TELEGRAPH|RECOVERY; IMPACT is not a snapshot state.
// This parser never throws for malformed input: callers get false + a stable error string.
// Pure C#. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace NguMach.Client.Core.Encounter
{
    public static class EncounterSnapshotValidator
    {
        private const int MaxJsonLength = 1024 * 1024;
        private const double Epsilon = 1e-6;

        private static readonly HashSet<string> AllowedTop = new HashSet<string>(StringComparer.Ordinal)
        {
            "schemaVersion", "encounterId", "questId", "bossRecordId", "bossEntityId",
            "bossLifeId", "bossRevision", "status", "phase", "bossHp", "bossMaxHp",
            "serverTick", "registeredCharacterIds", "activeMove",
            "moveCooldownRemainingTicks", "phaseGuardRemainingTicks", "wipeCountdownTicks",
            "arena", "safePads", "phaseNpc", "trialNpcVisible"
        };

        private static readonly HashSet<string> AllowedActiveMove = new HashSet<string>(StringComparer.Ordinal)
        {
            "moveId", "castId", "state", "ticksRemaining", "stateEndsAtTick", "shape", "targetLock"
        };

        private static readonly HashSet<string> AllowedShape = new HashSet<string>(StringComparer.Ordinal)
        {
            "kind", "centerXWu", "centerYWu", "angleDegrees", "rangeWu", "radiusWu",
            "innerRadiusWu", "outerRadiusWu", "facingX", "facingY"
        };

        private static readonly HashSet<string> AllowedArena = new HashSet<string>(StringComparer.Ordinal)
        {
            "shape", "centerXWu", "centerYWu", "radiusWu"
        };

        private static readonly HashSet<string> AllowedSafePad = new HashSet<string>(StringComparer.Ordinal)
        {
            "centerXWu", "centerYWu", "radiusWu", "applies"
        };

        private static readonly HashSet<string> AllowedPhaseNpc = new HashSet<string>(StringComparer.Ordinal)
        {
            "npcId", "xWu", "yWu", "active"
        };

        private static readonly HashSet<string> RequiredCooldowns = new HashSet<string>(StringComparer.Ordinal)
        {
            "A", "B", "C"
        };

        private static readonly string[] MoveIds = { "A", "B", "C" };
        private static readonly string[] MoveStates = { "TELEGRAPH", "RECOVERY" };
        private static readonly string[] TargetLocks =
        {
            "TELEGRAPH_START_FACING",
            "TELEGRAPH_START_TARGET_POSITION",
            "BOSS_POSITION"
        };

        public static bool TryParse(string json, out EncounterSnapshot snapshot, out string error)
        {
            snapshot = null;
            error = null;
            try
            {
                return TryParseCore(json, out snapshot, out error);
            }
            catch (Exception e)
            {
                snapshot = null;
                error = "unexpected parse failure: " + e.Message;
                return false;
            }
        }

        private static bool TryParseCore(string json, out EncounterSnapshot snapshot, out string error)
        {
            snapshot = null;
            if (string.IsNullOrWhiteSpace(json))
            {
                error = "empty json";
                return false;
            }
            if (json.Length > MaxJsonLength)
            {
                error = "json too large";
                return false;
            }

            JObject obj;
            if (!TryLoadObject(json, out obj, out error)) return false;

            if (!CheckOnlyProperties(obj, AllowedTop, "top-level", out error)) return false;
            // additionalProperties:false + required: every declared field is present.
            // Optional semantics are expressed as an explicit null (e.g. activeMove,
            // wipeCountdownTicks, and non-applicable shape fields).
            if (!RequireAllProperties(obj, AllowedTop, "top-level", out error)) return false;

            int schemaVersion;
            if (!ReadInt(obj, "schemaVersion", true, out schemaVersion, out error)) return false;
            if (schemaVersion != 1) { error = "unsupported schemaVersion: " + schemaVersion; return false; }

            string encounterId, questId, bossRecordId, bossEntityId, status;
            if (!ReadString(obj, "encounterId", true, out encounterId, out error)) return false;
            if (!Matches(encounterId, "^ENC-[0-9A-F]{24}$"))
            {
                error = "invalid encounterId pattern";
                return false;
            }
            if (!ReadString(obj, "questId", true, out questId, out error)) return false;
            if (!Matches(questId, "^P[0-9]{2}-[0-9]{2}$"))
            {
                error = "invalid questId pattern";
                return false;
            }
            if (!ReadString(obj, "bossRecordId", true, out bossRecordId, out error)) return false;
            if (!Matches(bossRecordId, "^MAN-BM-[A-Z0-9_]+$"))
            {
                error = "invalid bossRecordId pattern";
                return false;
            }
            if (!ReadString(obj, "bossEntityId", true, out bossEntityId, out error)) return false;
            if (!Matches(bossEntityId, "^ENT_[A-Z0-9_]+$"))
            {
                error = "invalid bossEntityId pattern";
                return false;
            }
            if (!ReadString(obj, "status", true, out status, out error)) return false;
            if (!IsOneOf(status, "OPEN", "DEFEATED", "RESET")) { error = "invalid status: " + status; return false; }

            long bossLifeId, bossRevision, serverTick, phaseGuardRemainingTicks;
            int phase, bossHp, bossMaxHp;
            if (!ReadLong(obj, "bossLifeId", true, out bossLifeId, out error)) return false;
            if (bossLifeId < 1) { error = "bossLifeId must be >= 1"; return false; }
            if (!ReadLong(obj, "bossRevision", true, out bossRevision, out error)) return false;
            if (bossRevision < 1) { error = "bossRevision must be >= 1"; return false; }
            if (!ReadInt(obj, "phase", true, out phase, out error)) return false;
            if (phase < 1 || phase > 3) { error = "phase must be 1..3"; return false; }
            if (!ReadInt(obj, "bossHp", true, out bossHp, out error)) return false;
            if (!ReadInt(obj, "bossMaxHp", true, out bossMaxHp, out error)) return false;
            if (bossMaxHp < 1) { error = "bossMaxHp must be > 0"; return false; }
            if (bossHp < 0 || bossHp > bossMaxHp) { error = "bossHp out of range"; return false; }
            if (!ReadLong(obj, "serverTick", true, out serverTick, out error)) return false;
            if (serverTick < 0) { error = "serverTick must be >= 0"; return false; }
            if (!ReadLong(obj, "phaseGuardRemainingTicks", true, out phaseGuardRemainingTicks, out error)) return false;
            if (phaseGuardRemainingTicks < 0) { error = "phaseGuardRemainingTicks must be >= 0"; return false; }

            long? wipeCountdownTicks;
            if (!ReadNullableLong(obj, "wipeCountdownTicks", out wipeCountdownTicks, out error)) return false;
            if (wipeCountdownTicks.HasValue && wipeCountdownTicks.Value < 0)
            {
                error = "wipeCountdownTicks must be >= 0";
                return false;
            }

            bool trialNpcVisible;
            if (!ReadBool(obj, "trialNpcVisible", true, out trialNpcVisible, out error)) return false;

            List<string> registered;
            if (!ReadStringArray(obj, "registeredCharacterIds", true, out registered, out error)) return false;
            if (registered == null || registered.Count != 1)
            {
                error = "registeredCharacterIds must contain exactly one owner";
                return false;
            }
            var owners = new HashSet<string>(StringComparer.Ordinal);
            foreach (var owner in registered)
            {
                if (!Matches(owner, "^CHR_[A-Z0-9]+$"))
                {
                    error = "invalid registeredCharacterIds owner pattern";
                    return false;
                }
                if (!owners.Add(owner))
                {
                    error = "registeredCharacterIds contains duplicate owner";
                    return false;
                }
            }

            EncounterArena arena;
            if (!ReadArena(obj, out arena, out error)) return false;

            List<SafePad> safePads;
            if (!ReadSafePads(obj, arena, out safePads, out error)) return false;

            PhaseNpc phaseNpc;
            if (!ReadPhaseNpc(obj, arena, out phaseNpc, out error)) return false;

            Dictionary<string, long> cooldowns;
            if (!ReadCooldowns(obj, out cooldowns, out error)) return false;

            ActiveMove activeMove = null;
            if (HasNonNull(obj, "activeMove"))
            {
                if (!ReadActiveMove(obj, serverTick, out activeMove, out error)) return false;
            }

            snapshot = new EncounterSnapshot
            {
                SchemaVersion = schemaVersion,
                EncounterId = encounterId,
                QuestId = questId,
                BossRecordId = bossRecordId,
                BossEntityId = bossEntityId,
                BossLifeId = bossLifeId,
                BossRevision = bossRevision,
                StatusRaw = status,
                PhaseRaw = phase,
                BossHp = bossHp,
                BossMaxHp = bossMaxHp,
                ServerTick = serverTick,
                RegisteredCharacterIds = registered,
                ActiveMove = activeMove,
                MoveCooldownRemainingTicks = cooldowns,
                PhaseGuardRemainingTicks = phaseGuardRemainingTicks,
                WipeCountdownTicks = wipeCountdownTicks,
                Arena = arena,
                SafePads = safePads,
                PhaseNpc = phaseNpc,
                TrialNpcVisible = trialNpcVisible
            };
            return true;
        }

        // Serializes a DTO back through the same strict wire parser so direct callers
        // cannot bypass semantic checks by constructing a DTO manually.
        public static bool IsValid(EncounterSnapshot snapshot, out string reason)
        {
            reason = null;
            if (snapshot == null) { reason = "null"; return false; }
            string json;
            try
            {
                json = JsonConvert.SerializeObject(snapshot, new JsonSerializerSettings
                {
                    NullValueHandling = NullValueHandling.Include,
                    Formatting = Formatting.None
                });
            }
            catch (Exception e)
            {
                reason = "serialize failed: " + e.Message;
                return false;
            }
            EncounterSnapshot parsed;
            return TryParse(json, out parsed, out reason);
        }

        private static bool ReadActiveMove(JObject obj, long serverTick, out ActiveMove move, out string error)
        {
            move = null;
            if (!TryGetObject(obj, "activeMove", out var am, out error)) return false;
            if (!CheckOnlyProperties(am, AllowedActiveMove, "activeMove", out error)) return false;
            if (!RequireAllProperties(am, AllowedActiveMove, "activeMove", out error)) return false;

            string moveId, castId, state, targetLock;
            if (!ReadString(am, "moveId", true, out moveId, out error)) return false;
            if (!IsOneOf(moveId, MoveIds)) { error = "invalid moveId: " + moveId; return false; }
            if (!ReadString(am, "castId", true, out castId, out error)) return false;
            if (!Matches(castId, "^CAST-[A-Z0-9-]{8,40}$"))
            {
                error = "invalid castId pattern";
                return false;
            }
            if (!ReadString(am, "state", true, out state, out error)) return false;
            if (!IsOneOf(state, MoveStates)) { error = "invalid move state: " + state; return false; }
            if (!ReadString(am, "targetLock", true, out targetLock, out error)) return false;
            if (!IsOneOf(targetLock, TargetLocks)) { error = "invalid targetLock: " + targetLock; return false; }

            long ticksRemaining, stateEndsAtTick;
            if (!ReadLong(am, "ticksRemaining", true, out ticksRemaining, out error)) return false;
            if (!ReadLong(am, "stateEndsAtTick", true, out stateEndsAtTick, out error)) return false;
            if (ticksRemaining < 0) { error = "ticksRemaining must be >= 0"; return false; }
            if (stateEndsAtTick < serverTick) { error = "stateEndsAtTick must be >= serverTick"; return false; }
            if (ticksRemaining != stateEndsAtTick - serverTick)
            {
                error = "ticksRemaining must equal stateEndsAtTick - serverTick";
                return false;
            }

            MoveShape shape;
            if (!ReadShape(am, out shape, out error)) return false;

            move = new ActiveMove
            {
                MoveId = moveId,
                CastId = castId,
                StateRaw = state,
                TicksRemaining = ticksRemaining,
                StateEndsAtTick = stateEndsAtTick,
                Shape = shape,
                TargetLock = targetLock
            };
            return true;
        }

        private static bool ReadShape(JObject move, out MoveShape shape, out string error)
        {
            shape = null;
            if (!TryGetObject(move, "shape", out var sh, out error)) return false;
            if (!CheckOnlyProperties(sh, AllowedShape, "shape", out error)) return false;
            if (!RequireAllProperties(sh, AllowedShape, "shape", out error)) return false;

            string kind;
            if (!ReadString(sh, "kind", true, out kind, out error)) return false;
            if (!IsOneOf(kind, "CONE", "CIRCLE", "ANNULUS")) { error = "invalid shape kind: " + kind; return false; }

            double centerX, centerY;
            if (!ReadDouble(sh, "centerXWu", true, out centerX, out error)) return false;
            if (!ReadDouble(sh, "centerYWu", true, out centerY, out error)) return false;

            double? angle, range, radius, inner, outer, facingX, facingY;
            if (!ReadNullableDouble(sh, "angleDegrees", out angle, out error)) return false;
            if (!ReadNullableDouble(sh, "rangeWu", out range, out error)) return false;
            if (!ReadNullableDouble(sh, "radiusWu", out radius, out error)) return false;
            if (!ReadNullableDouble(sh, "innerRadiusWu", out inner, out error)) return false;
            if (!ReadNullableDouble(sh, "outerRadiusWu", out outer, out error)) return false;
            if (!ReadNullableDouble(sh, "facingX", out facingX, out error)) return false;
            if (!ReadNullableDouble(sh, "facingY", out facingY, out error)) return false;

            if (kind == "CONE")
            {
                if (!angle.HasValue) { error = "cone requires angleDegrees"; return false; }
                if (!range.HasValue) { error = "cone requires rangeWu"; return false; }
                if (angle.Value <= 0 || angle.Value > 360) { error = "cone angleDegrees must be in (0,360]"; return false; }
                if (range.Value <= 0) { error = "cone rangeWu must be > 0"; return false; }
                if (!facingX.HasValue || !facingY.HasValue) { error = "cone requires facing vector"; return false; }
                double length = Math.Sqrt(facingX.Value * facingX.Value + facingY.Value * facingY.Value);
                if (Math.Abs(length - 1.0) > 0.001) { error = "cone facing vector must be normalized"; return false; }
                if (radius.HasValue) { error = "cone must not carry radiusWu"; return false; }
                if (inner.HasValue || outer.HasValue) { error = "cone must not carry annulus radii"; return false; }
            }
            else if (kind == "CIRCLE")
            {
                if (!radius.HasValue) { error = "circle requires radiusWu"; return false; }
                if (radius.Value <= 0) { error = "circle radiusWu must be > 0"; return false; }
                if (angle.HasValue || range.HasValue) { error = "circle must not carry cone angle/range"; return false; }
                if (inner.HasValue || outer.HasValue) { error = "circle must not carry annulus radii"; return false; }
                if (facingX.HasValue || facingY.HasValue) { error = "circle must not carry facing"; return false; }
            }
            else // ANNULUS
            {
                if (!inner.HasValue || !outer.HasValue) { error = "annulus requires innerRadiusWu and outerRadiusWu"; return false; }
                if (inner.Value < 0) { error = "annulus innerRadiusWu must be >= 0"; return false; }
                if (inner.Value >= outer.Value) { error = "annulus innerRadiusWu must be < outerRadiusWu"; return false; }
                if (angle.HasValue || range.HasValue) { error = "annulus must not carry cone angle/range"; return false; }
                if (radius.HasValue) { error = "annulus must not carry radiusWu"; return false; }
                if (facingX.HasValue || facingY.HasValue) { error = "annulus must not carry facing"; return false; }
            }

            shape = new MoveShape
            {
                KindRaw = kind,
                CenterXWu = centerX,
                CenterYWu = centerY,
                AngleDegrees = angle,
                RangeWu = range,
                RadiusWu = radius,
                InnerRadiusWu = inner,
                OuterRadiusWu = outer,
                FacingX = facingX,
                FacingY = facingY
            };
            return true;
        }

        private static bool ReadArena(JObject obj, out EncounterArena arena, out string error)
        {
            arena = null;
            if (!TryGetObject(obj, "arena", out var a, out error)) return false;
            if (!CheckOnlyProperties(a, AllowedArena, "arena", out error)) return false;
            if (!RequireAllProperties(a, AllowedArena, "arena", out error)) return false;

            string shape;
            if (!ReadString(a, "shape", true, out shape, out error)) return false;
            if (shape != "CIRCLE") { error = "unsupported arena shape: " + shape; return false; }
            double centerX, centerY, radius;
            if (!ReadDouble(a, "centerXWu", true, out centerX, out error)) return false;
            if (!ReadDouble(a, "centerYWu", true, out centerY, out error)) return false;
            if (!ReadDouble(a, "radiusWu", true, out radius, out error)) return false;
            if (radius <= 0) { error = "arena radiusWu must be > 0"; return false; }

            arena = new EncounterArena { Shape = shape, CenterXWu = centerX, CenterYWu = centerY, RadiusWu = radius };
            return true;
        }

        private static bool ReadSafePads(JObject obj, EncounterArena arena, out List<SafePad> pads, out string error)
        {
            pads = null;
            if (!TryGetArray(obj, "safePads", out var arr, out error)) return false;
            pads = new List<SafePad>(arr.Count);
            foreach (var token in arr)
            {
                var sp = token as JObject;
                if (sp == null) { error = "safePads item must be object"; return false; }
                if (!CheckOnlyProperties(sp, AllowedSafePad, "safePad", out error)) return false;
                if (!RequireAllProperties(sp, AllowedSafePad, "safePad", out error)) return false;
                double x, y, radius;
                bool applies;
                if (!ReadDouble(sp, "centerXWu", true, out x, out error)) return false;
                if (!ReadDouble(sp, "centerYWu", true, out y, out error)) return false;
                if (!ReadDouble(sp, "radiusWu", true, out radius, out error)) return false;
                if (radius <= 0) { error = "safePad radiusWu must be > 0"; return false; }
                if (!ReadBool(sp, "applies", true, out applies, out error)) return false;
                double dx = x - arena.CenterXWu;
                double dy = y - arena.CenterYWu;
                double distance = Math.Sqrt(dx * dx + dy * dy);
                if (distance + radius > arena.RadiusWu + Epsilon)
                {
                    error = "safePad outside arena";
                    return false;
                }
                pads.Add(new SafePad { CenterXWu = x, CenterYWu = y, RadiusWu = radius, Applies = applies });
            }
            return true;
        }

        private static bool ReadPhaseNpc(JObject obj, EncounterArena arena, out PhaseNpc npc, out string error)
        {
            npc = null;
            if (!TryGetObject(obj, "phaseNpc", out var pn, out error)) return false;
            if (!CheckOnlyProperties(pn, AllowedPhaseNpc, "phaseNpc", out error)) return false;
            if (!RequireAllProperties(pn, AllowedPhaseNpc, "phaseNpc", out error)) return false;

            string npcId;
            double x, y;
            bool active;
            if (!ReadString(pn, "npcId", true, out npcId, out error)) return false;
            if (!ReadDouble(pn, "xWu", true, out x, out error)) return false;
            if (!ReadDouble(pn, "yWu", true, out y, out error)) return false;
            if (!ReadBool(pn, "active", true, out active, out error)) return false;

            double dx = x - arena.CenterXWu;
            double dy = y - arena.CenterYWu;
            if (Math.Sqrt(dx * dx + dy * dy) > arena.RadiusWu + Epsilon)
            {
                error = "phaseNpc outside arena";
                return false;
            }
            npc = new PhaseNpc { NpcId = npcId, XWu = x, YWu = y, Active = active };
            return true;
        }

        private static bool ReadCooldowns(JObject obj, out Dictionary<string, long> cooldowns, out string error)
        {
            cooldowns = null;
            if (!TryGetObject(obj, "moveCooldownRemainingTicks", out var mc, out error)) return false;
            foreach (var property in mc.Properties())
            {
                if (!RequiredCooldowns.Contains(property.Name))
                {
                    error = "unknown moveCooldownRemainingTicks key: " + property.Name;
                    return false;
                }
            }
            foreach (var key in RequiredCooldowns)
            {
                if (!mc.ContainsKey(key))
                {
                    error = "missing moveCooldownRemainingTicks key: " + key;
                    return false;
                }
            }
            cooldowns = new Dictionary<string, long>(StringComparer.Ordinal);
            foreach (var property in mc.Properties())
            {
                if (property.Value.Type != JTokenType.Integer)
                {
                    error = "moveCooldownRemainingTicks." + property.Name + " must be integer";
                    return false;
                }
                long ticks;
                if (!TryTokenLong(property.Value, out ticks))
                {
                    error = "moveCooldownRemainingTicks." + property.Name + " out of range";
                    return false;
                }
                if (ticks < 0)
                {
                    error = "moveCooldownRemainingTicks." + property.Name + " must be >= 0";
                    return false;
                }
                cooldowns[property.Name] = ticks;
            }
            return true;
        }

        private static bool TryLoadObject(string json, out JObject obj, out string error)
        {
            obj = null;
            error = null;
            try
            {
                var settings = new JsonLoadSettings
                {
                    CommentHandling = CommentHandling.Ignore,
                    DuplicatePropertyNameHandling = DuplicatePropertyNameHandling.Error,
                    LineInfoHandling = LineInfoHandling.Ignore
                };
                using (var reader = new JsonTextReader(new StringReader(json))
                {
                    DateParseHandling = DateParseHandling.None,
                    MaxDepth = 48
                })
                {
                    obj = JObject.Load(reader, settings);
                    if (reader.Read()) { error = "trailing json content"; obj = null; return false; }
                }
            }
            catch (JsonException e)
            {
                error = "json parse: " + e.Message;
                obj = null;
                return false;
            }
            if (obj == null) { error = "json root must be object"; return false; }
            return true;
        }

        private static bool CheckOnlyProperties(JObject obj, HashSet<string> allowed, string where, out string error)
        {
            error = null;
            foreach (var property in obj.Properties())
            {
                if (!allowed.Contains(property.Name))
                {
                    error = "unknown " + where + " property: " + property.Name;
                    return false;
                }
            }
            return true;
        }

        private static bool RequireAllProperties(JObject obj, HashSet<string> required, string where, out string error)
        {
            error = null;
            foreach (var name in required)
            {
                if (!obj.ContainsKey(name))
                {
                    error = "missing " + where + " property: " + name;
                    return false;
                }
            }
            return true;
        }

        private static bool HasNonNull(JObject obj, string name)
        {
            return obj.TryGetValue(name, out var token) && token.Type != JTokenType.Null;
        }

        private static bool TryGetObject(JObject obj, string name, out JObject value, out string error)
        {
            value = null;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                error = "missing " + name;
                return false;
            }
            if (token.Type != JTokenType.Object)
            {
                error = name + " must be object";
                return false;
            }
            value = (JObject)token;
            return true;
        }

        private static bool TryGetArray(JObject obj, string name, out JArray value, out string error)
        {
            value = null;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                error = "missing " + name;
                return false;
            }
            if (token.Type != JTokenType.Array)
            {
                error = name + " must be array";
                return false;
            }
            value = (JArray)token;
            return true;
        }

        private static bool ReadString(JObject obj, string name, bool required, out string value, out string error)
        {
            value = null;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                if (required) { error = "missing " + name; return false; }
                return true;
            }
            if (token.Type != JTokenType.String)
            {
                error = name + " must be string";
                return false;
            }
            value = token.Value<string>();
            if (string.IsNullOrWhiteSpace(value))
            {
                error = name + " must be non-empty";
                return false;
            }
            return true;
        }

        private static bool ReadBool(JObject obj, string name, bool required, out bool value, out string error)
        {
            value = false;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                if (required) { error = "missing " + name; return false; }
                return true;
            }
            if (token.Type != JTokenType.Boolean)
            {
                error = name + " must be boolean";
                return false;
            }
            value = token.Value<bool>();
            return true;
        }

        private static bool ReadInt(JObject obj, string name, bool required, out int value, out string error)
        {
            value = 0;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                if (required) { error = "missing " + name; return false; }
                return true;
            }
            if (token.Type != JTokenType.Integer)
            {
                error = name + " must be integer";
                return false;
            }
            long raw;
            if (!TryTokenLong(token, out raw) || raw < int.MinValue || raw > int.MaxValue)
            {
                error = name + " out of range";
                return false;
            }
            value = (int)raw;
            return true;
        }

        private static bool ReadLong(JObject obj, string name, bool required, out long value, out string error)
        {
            value = 0;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                if (required) { error = "missing " + name; return false; }
                return true;
            }
            if (token.Type != JTokenType.Integer)
            {
                error = name + " must be integer";
                return false;
            }
            if (!TryTokenLong(token, out value))
            {
                error = name + " out of range";
                return false;
            }
            return true;
        }

        private static bool ReadNullableLong(JObject obj, string name, out long? value, out string error)
        {
            value = null;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null) return true;
            if (token.Type != JTokenType.Integer)
            {
                error = name + " must be integer or null";
                return false;
            }
            long raw;
            if (!TryTokenLong(token, out raw))
            {
                error = name + " out of range";
                return false;
            }
            value = raw;
            return true;
        }

        private static bool ReadDouble(JObject obj, string name, bool required, out double value, out string error)
        {
            value = 0.0;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                if (required) { error = "missing " + name; return false; }
                return true;
            }
            if (token.Type != JTokenType.Float && token.Type != JTokenType.Integer)
            {
                error = name + " must be number";
                return false;
            }
            value = token.Value<double>();
            if (double.IsNaN(value) || double.IsInfinity(value))
            {
                error = name + " must be finite";
                return false;
            }
            return true;
        }

        private static bool ReadNullableDouble(JObject obj, string name, out double? value, out string error)
        {
            value = null;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null) return true;
            if (token.Type != JTokenType.Float && token.Type != JTokenType.Integer)
            {
                error = name + " must be number or null";
                return false;
            }
            double raw = token.Value<double>();
            if (double.IsNaN(raw) || double.IsInfinity(raw))
            {
                error = name + " must be finite";
                return false;
            }
            value = raw;
            return true;
        }

        private static bool ReadStringArray(JObject obj, string name, bool required, out List<string> values, out string error)
        {
            values = null;
            error = null;
            if (!obj.TryGetValue(name, out var token) || token.Type == JTokenType.Null)
            {
                if (required) { error = "missing " + name; return false; }
                return true;
            }
            if (token.Type != JTokenType.Array)
            {
                error = name + " must be array";
                return false;
            }
            values = new List<string>();
            foreach (var item in (JArray)token)
            {
                if (item.Type != JTokenType.String)
                {
                    error = name + " item must be string";
                    return false;
                }
                string text = item.Value<string>();
                if (string.IsNullOrWhiteSpace(text))
                {
                    error = name + " item must be non-empty";
                    return false;
                }
                values.Add(text);
            }
            return true;
        }

        private static bool TryTokenLong(JToken token, out long value)
        {
            value = 0;
            try
            {
                value = token.Value<long>();
                return true;
            }
            catch (Exception)
            {
                return false;
            }
        }

        private static bool IsOneOf(string value, params string[] allowed)
        {
            foreach (var item in allowed) if (string.Equals(value, item, StringComparison.Ordinal)) return true;
            return false;
        }

        private static bool Matches(string value, string pattern)
        {
            return value != null && Regex.IsMatch(value, pattern, RegexOptions.CultureInvariant);
        }
    }
}
