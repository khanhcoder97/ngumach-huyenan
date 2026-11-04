// OPC-15 O1 (WO26) — Strict validation for encounter snapshots per reference payload.
// Pure C#. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace NguMach.Client.Core.Encounter
{
    public static class EncounterSnapshotValidator
    {
        private static readonly HashSet<string> AllowedTop = new HashSet<string>(StringComparer.Ordinal)
        {
            "schemaVersion","encounterId","questId","bossRecordId","bossEntityId","bossLifeId",
            "bossRevision","status","phase","bossHp","bossMaxHp","serverTick",
            "registeredCharacterIds","activeMove","moveCooldownRemainingTicks",
            "phaseGuardRemainingTicks","wipeCountdownTicks","arena","safePads",
            "phaseNpc","trialNpcVisible"
        };

        public static bool TryParse(string json, out EncounterSnapshot snapshot, out string error)
        {
            snapshot = null; error = null;
            if (string.IsNullOrWhiteSpace(json)) { error = "empty json"; return false; }
            JObject obj;
            try { obj = JObject.Parse(json); }
            catch (Exception e) { error = "json parse: " + e.Message; return false; }

            foreach (var p in obj.Properties())
                if (!AllowedTop.Contains(p.Name)) { error = "unknown property: " + p.Name; return false; }

            // required
            foreach (var req in new[] { "encounterId","bossLifeId","status","phase","bossHp","bossMaxHp","serverTick","registeredCharacterIds" })
                if (obj[req] == null) { error = "missing " + req; return false; }

            if (string.IsNullOrWhiteSpace(obj["encounterId"].Value<string>())) { error = "missing encounterId"; return false; }
            var status = obj["status"].Value<string>();
            if (status != "OPEN" && status != "DEFEATED" && status != "RESET") { error = "invalid status: " + status; return false; }
            int phase = obj["phase"].Value<int>();
            if (phase < 1 || phase > 3) { error = "invalid phase: " + phase; return false; }
            if (obj["bossLifeId"].Value<long>() <= 0) { error = "invalid bossLifeId"; return false; }

            // activeMove strict
            if (obj["activeMove"] != null && obj["activeMove"].Type != JTokenType.Null)
            {
                var am = obj["activeMove"] as JObject;
                if (am == null) { error = "activeMove not object"; return false; }
                var allowedAm = new HashSet<string>(StringComparer.Ordinal) { "moveId","castId","state","ticksRemaining","stateEndsAtTick","shape","targetLock" };
                foreach (var p in am.Properties()) if (!allowedAm.Contains(p.Name)) { error = "unknown activeMove property: " + p.Name; return false; }
                if (am["state"] != null)
                {
                    var st = am["state"].Value<string>();
                    if (st != "TELEGRAPH" && st != "IMPACT" && st != "RECOVERY") { error = "invalid move state: " + st; return false; }
                }
                if (am["shape"] != null && am["shape"].Type != JTokenType.Null)
                {
                    var sh = am["shape"] as JObject;
                    if (sh == null) { error = "shape not object"; return false; }
                    var allowedSh = new HashSet<string>(StringComparer.Ordinal) { "kind","centerXWu","centerYWu","angleDegrees","rangeWu","radiusWu","innerRadiusWu","outerRadiusWu","facingX","facingY" };
                    foreach (var p in sh.Properties()) if (!allowedSh.Contains(p.Name)) { error = "unknown shape property: " + p.Name; return false; }
                    var kind = sh["kind"] != null ? sh["kind"].Value<string>() : null;
                    if (kind == null) { error = "missing shape kind"; return false; }
                    if (kind != "CONE" && kind != "CIRCLE" && kind != "ANNULUS" &&
                        kind != "cone" && kind != "circle" && kind != "annulus") { error = "invalid shape kind: " + kind; return false; }
                    foreach (var key in new[] { "centerXWu","centerYWu","angleDegrees","rangeWu","radiusWu","innerRadiusWu","outerRadiusWu","facingX","facingY" })
                    {
                        if (sh[key] != null && sh[key].Type != JTokenType.Null)
                        {
                            double v = sh[key].Value<double>();
                            if (double.IsNaN(v) || double.IsInfinity(v)) { error = "non-finite " + key; return false; }
                        }
                    }
                    if (sh["facingX"] != null && sh["facingY"] != null)
                    {
                        double fx = sh["facingX"].Value<double>();
                        double fy = sh["facingY"].Value<double>();
                        double len = Math.Sqrt(fx * fx + fy * fy);
                        if (len < 0.99 || len > 1.01) { error = "facing not normalized: " + len; return false; }
                    }
                }
            }

            // arena strict
            if (obj["arena"] != null && obj["arena"].Type != JTokenType.Null)
            {
                var a = obj["arena"] as JObject;
                if (a == null) { error = "arena not object"; return false; }
                var allowedA = new HashSet<string>(StringComparer.Ordinal) { "shape","centerXWu","centerYWu","radiusWu" };
                foreach (var p in a.Properties()) if (!allowedA.Contains(p.Name)) { error = "unknown arena property: " + p.Name; return false; }
            }

            // safePads strict
            if (obj["safePads"] != null && obj["safePads"].Type != JTokenType.Null)
            {
                var arr = obj["safePads"] as JArray;
                if (arr == null) { error = "safePads not array"; return false; }
                foreach (var item in arr)
                {
                    var sp = item as JObject;
                    if (sp == null) { error = "safePad not object"; return false; }
                    var allowedSp = new HashSet<string>(StringComparer.Ordinal) { "centerXWu","centerYWu","radiusWu","applies" };
                    foreach (var p in sp.Properties()) if (!allowedSp.Contains(p.Name)) { error = "unknown safePad property: " + p.Name; return false; }
                }
            }

            // phaseNpc strict
            if (obj["phaseNpc"] != null && obj["phaseNpc"].Type != JTokenType.Null)
            {
                var pn = obj["phaseNpc"] as JObject;
                if (pn == null) { error = "phaseNpc not object"; return false; }
                var allowedPn = new HashSet<string>(StringComparer.Ordinal) { "npcId","xWu","yWu","active" };
                foreach (var p in pn.Properties()) if (!allowedPn.Contains(p.Name)) { error = "unknown phaseNpc property: " + p.Name; return false; }
            }

            // moveCooldownRemainingTicks strict (object of number)
            if (obj["moveCooldownRemainingTicks"] != null && obj["moveCooldownRemainingTicks"].Type != JTokenType.Null)
            {
                var mc = obj["moveCooldownRemainingTicks"] as JObject;
                if (mc == null) { error = "moveCooldownRemainingTicks not object"; return false; }
            }

            var settings = new JsonSerializerSettings { MissingMemberHandling = MissingMemberHandling.Ignore };
            try { snapshot = JsonConvert.DeserializeObject<EncounterSnapshot>(json, settings); }
            catch (Exception e) { error = "deserialize: " + e.Message; return false; }
            if (snapshot == null) { error = "null snapshot"; return false; }
            if (snapshot.Extra != null && snapshot.Extra.Count > 0)
            {
                error = "unknown top-level property: " + string.Join(",", snapshot.Extra.Keys);
                return false;
            }
            // ticksRemaining consistency if present
            if (snapshot.ActiveMove != null && snapshot.ActiveMove.TicksRemaining != 0 && snapshot.ActiveMove.StateEndsAtTick != 0)
            {
                long calc = snapshot.ActiveMove.StateEndsAtTick - snapshot.ServerTick;
                if (calc < 0) calc = 0;
                // ticksRemaining in activeMove is the move's own; not strictly equal to stateEndsAtTick-serverTick? reference: ticksRemaining 18, stateEndsAtTick 2018, serverTick 2000 => 18. So must match.
                if (snapshot.ActiveMove.TicksRemaining != calc) { error = "ticksRemaining mismatch"; return false; }
            }
            return true;
        }

        public static bool IsValid(EncounterSnapshot s, out string reason)
        {
            reason = null;
            if (s == null) { reason = "null"; return false; }
            if (string.IsNullOrWhiteSpace(s.EncounterId)) { reason = "missing encounterId"; return false; }
            if (s.BossLifeId <= 0) { reason = "invalid bossLifeId"; return false; }
            if (s.BossMaxHp <= 0) { reason = "invalid bossMaxHp"; return false; }
            if (s.BossHp < 0 || s.BossHp > s.BossMaxHp) { reason = "bossHp out of range"; return false; }
            if (s.PhaseRaw < 1 || s.PhaseRaw > 3) { reason = "invalid phase"; return false; }
            if (s.StatusRaw != "OPEN" && s.StatusRaw != "DEFEATED" && s.StatusRaw != "RESET") { reason = "invalid status"; return false; }
            if (s.ActiveMove != null && s.ActiveMove.Shape != null)
            {
                var sh = s.ActiveMove.Shape;
                // kind case-insensitive
                var kind = sh.KindRaw;
                if (string.IsNullOrEmpty(kind)) kind = "cone";
                if (kind != "cone" && kind != "circle" && kind != "annulus" &&
                    kind != "CONE" && kind != "CIRCLE" && kind != "ANNULUS") { reason = "invalid kind"; return false; }
                double len = Math.Sqrt(sh.FacingX * sh.FacingX + sh.FacingY * sh.FacingY);
                if (len < 0.99 || len > 1.01) { reason = "facing not normalized"; return false; }
                if (double.IsNaN(sh.FacingX) || double.IsInfinity(sh.FacingX) || double.IsNaN(sh.FacingY) || double.IsInfinity(sh.FacingY)) { reason = "non-finite facing"; return false; }
            }
            return true;
        }
    }
}
