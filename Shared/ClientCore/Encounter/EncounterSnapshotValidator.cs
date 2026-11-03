// OPC-15 O1 — Strict validation for encounter snapshots. Rejects unknown properties,
// invalid enums, non-finite geometry, non-unit facing, out-of-range values.
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
        public static bool TryParse(string json, out EncounterSnapshot snapshot, out string error)
        {
            snapshot = null; error = null;
            if (string.IsNullOrWhiteSpace(json)) { error = "empty json"; return false; }
            JObject obj;
            try { obj = JObject.Parse(json); }
            catch (Exception e) { error = "json parse: " + e.Message; return false; }

            // strict: no unknown top-level properties
            var allowedTop = new HashSet<string>(StringComparer.Ordinal)
            {
                "schemaVersion","encounterId","bossLifeId","status","phase","serverTick",
                "bossHp","bossMaxHp","bossRevision","activeMove","deadlineTick","ticksRemaining",
                "registration","arena","safePads","npcId","cooldowns"
            };
            foreach (var p in obj.Properties())
                if (!allowedTop.Contains(p.Name)) { error = "unknown property: " + p.Name; return false; }

            // required
            if (obj["encounterId"] == null || string.IsNullOrWhiteSpace(obj["encounterId"].Value<string>())) { error = "missing encounterId"; return false; }
            if (obj["bossLifeId"] == null) { error = "missing bossLifeId"; return false; }
            if (obj["status"] == null) { error = "missing status"; return false; }
            if (obj["phase"] == null) { error = "missing phase"; return false; }
            if (obj["serverTick"] == null) { error = "missing serverTick"; return false; }
            if (obj["bossHp"] == null) { error = "missing bossHp"; return false; }
            if (obj["bossMaxHp"] == null) { error = "missing bossMaxHp"; return false; }
            if (obj["bossRevision"] == null) { error = "missing bossRevision"; return false; }

            // enums
            var status = obj["status"].Value<string>();
            if (status != "OPEN" && status != "DEFEATED" && status != "RESET") { error = "invalid status: " + status; return false; }
            int phase = obj["phase"].Value<int>();
            if (phase < 1 || phase > 3) { error = "invalid phase: " + phase; return false; }

            // activeMove strict
            if (obj["activeMove"] != null && obj["activeMove"].Type != JTokenType.Null)
            {
                var am = obj["activeMove"] as JObject;
                if (am == null) { error = "activeMove not object"; return false; }
                var allowedAm = new HashSet<string>(StringComparer.Ordinal) { "moveId","castId","state","stateEndsAtTick","shape" };
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
                    var allowedSh = new HashSet<string>(StringComparer.Ordinal) { "kind","center","rangeWu","radiusWu","innerRadiusWu","outerRadiusWu","angleDegrees","facingX","facingY" };
                    foreach (var p in sh.Properties()) if (!allowedSh.Contains(p.Name)) { error = "unknown shape property: " + p.Name; return false; }
                    var kind = sh["kind"] != null ? sh["kind"].Value<string>() : "cone";
                    if (kind != "cone" && kind != "circle" && kind != "annulus") { error = "invalid shape kind: " + kind; return false; }
                    // finite checks
                    foreach (var key in new[] { "rangeWu","radiusWu","innerRadiusWu","outerRadiusWu","angleDegrees","facingX","facingY" })
                    {
                        if (sh[key] != null)
                        {
                            double v = sh[key].Value<double>();
                            if (double.IsNaN(v) || double.IsInfinity(v)) { error = "non-finite " + key; return false; }
                        }
                    }
                    if (sh["center"] != null)
                    {
                        var c = sh["center"] as JObject;
                        if (c == null) { error = "center not object"; return false; }
                        foreach (var p in c.Properties()) if (p.Name != "x" && p.Name != "y") { error = "unknown center property: " + p.Name; return false; }
                    }
                    // facing normalized tolerance (if both present)
                    if (sh["facingX"] != null && sh["facingY"] != null)
                    {
                        double fx = sh["facingX"].Value<double>();
                        double fy = sh["facingY"].Value<double>();
                        double len = Math.Sqrt(fx * fx + fy * fy);
                        if (len < 0.99 || len > 1.01) { error = "facing not normalized: " + len; return false; }
                    }
                    // shape-specific
                    if (kind == "circle")
                    {
                        if (sh["radiusWu"] == null || sh["radiusWu"].Value<double>() <= 0) { error = "circle radiusWu must be > 0"; return false; }
                    }
                    if (kind == "annulus")
                    {
                        if (sh["innerRadiusWu"] == null || sh["outerRadiusWu"] == null) { error = "annulus radii required"; return false; }
                        double ir = sh["innerRadiusWu"].Value<double>();
                        double or = sh["outerRadiusWu"].Value<double>();
                        if (ir < 0 || ir >= or) { error = "annulus innerRadius must be < outerRadius"; return false; }
                    }
                    if (kind == "cone")
                    {
                        if (sh["rangeWu"] != null && sh["rangeWu"].Value<double>() <= 0) { error = "cone rangeWu must be > 0"; return false; }
                        if (sh["angleDegrees"] != null)
                        {
                            double a = sh["angleDegrees"].Value<double>();
                            if (a <= 0 || a > 360) { error = "cone angleDegrees must be in (0,360]"; return false; }
                        }
                    }
                    // id pattern for encounterId already checked; no id in shape
                }
            }

            // parse via Newtonsoft (strict-ish via settings)
            var settings = new JsonSerializerSettings { MissingMemberHandling = MissingMemberHandling.Ignore };
            try { snapshot = JsonConvert.DeserializeObject<EncounterSnapshot>(json, settings); }
            catch (Exception e) { error = "deserialize: " + e.Message; return false; }
            if (snapshot == null) { error = "null snapshot"; return false; }
            if (snapshot.Extra != null && snapshot.Extra.Count > 0)
            {
                error = "unknown top-level property: " + string.Join(",", snapshot.Extra.Keys);
                return false;
            }
            // activeMove extra check
            if (snapshot.ActiveMove != null)
            {
                // re-parse activeMove extras via JObject already done above; ensure stateEndsAtTick >= serverTick if present
                if (snapshot.ActiveMove.StateEndsAtTick != 0 && snapshot.ActiveMove.StateEndsAtTick < snapshot.ServerTick)
                { error = "stateEndsAtTick < serverTick"; return false; }
            }
            // ticksRemaining consistency
            if (snapshot.TicksRemaining.HasValue && snapshot.DeadlineTick.HasValue)
            {
                long calc = snapshot.DeadlineTick.Value - snapshot.ServerTick;
                if (calc < 0) calc = 0;
                if (snapshot.TicksRemaining.Value != calc) { error = "ticksRemaining mismatch"; return false; }
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
                if (sh.Kind == MoveShapeKind.Circle)
                {
                    if (!sh.RadiusWu.HasValue || sh.RadiusWu.Value <= 0) { reason = "circle radiusWu must be > 0"; return false; }
                }
                if (sh.Kind == MoveShapeKind.Annulus)
                {
                    if (!sh.InnerRadiusWu.HasValue || !sh.OuterRadiusWu.HasValue) { reason = "annulus radii required"; return false; }
                    if (sh.InnerRadiusWu.Value < 0 || sh.InnerRadiusWu.Value >= sh.OuterRadiusWu.Value) { reason = "annulus inner < outer"; return false; }
                }
                if (sh.Kind == MoveShapeKind.Cone)
                {
                    if (sh.RangeWu <= 0) { reason = "cone rangeWu must be > 0"; return false; }
                    if (sh.AngleDegrees.HasValue && (sh.AngleDegrees.Value <= 0 || sh.AngleDegrees.Value > 360)) { reason = "cone angleDegrees invalid"; return false; }
                }
                double len = Math.Sqrt(sh.FacingX * sh.FacingX + sh.FacingY * sh.FacingY);
                if (len < 0.99 || len > 1.01) { reason = "facing not normalized"; return false; }
                if (double.IsNaN(sh.FacingX) || double.IsInfinity(sh.FacingX) || double.IsNaN(sh.FacingY) || double.IsInfinity(sh.FacingY)) { reason = "non-finite facing"; return false; }
            }
            return true;
        }
    }
}
