// OPC-15 O-C/O5 (WO26) — Handshake / capability model so Muse can distinguish
// (a) what this portable client knows how to call from (b) what the deployed server
// actually enabled. Encounter routes are never advertised as usable while the alpha
// boss gate is OFF or the server did not advertise them. Pure C#. Owner: OpenCode.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Core.Handshake
{
    // Versioned deployment descriptor supplied by the integration host (sample/CI).
    // Qoder's server does not yet expose a capability endpoint; until it does, the
    // caller must pass an explicit profile instead of this client inventing routes.
    public sealed class DeploymentProfile
    {
        public string ProfileId { get; set; } = "production-off";
        public string ContractVersion { get; set; } = "v2";
        public bool AlphaBossEnabled { get; set; }
        public bool AlphaInventoryV2Enabled { get; set; }
        public bool DeathReturnEnabled { get; set; }
        public bool QuestTalkEnabled { get; set; }
        public bool PortalEnabled { get; set; }
        public bool MapViewedEnabled { get; set; }
        public List<string> ServerEnabledRoutes { get; set; } = new List<string>();
        public string SourceVersion { get; set; } = "unknown";

        public static DeploymentProfile ProductionOff()
        {
            return new DeploymentProfile
            {
                ProfileId = "production-off",
                AlphaBossEnabled = false,
                AlphaInventoryV2Enabled = false,
                DeathReturnEnabled = false,
                QuestTalkEnabled = false,
                PortalEnabled = false,
                MapViewedEnabled = false,
                ServerEnabledRoutes = new List<string>(),
                SourceVersion = "unknown"
            };
        }

        public static DeploymentProfile PrivateAlpha(
            bool encounterEnabled,
            bool inventoryV2Enabled = false,
            bool deathReturnEnabled = false,
            bool questTalkEnabled = false,
            bool portalEnabled = false,
            bool mapViewedEnabled = false)
        {
            // Core P1 routes are part of the private-alpha deployment itself; the
            // alpha gates below are additive opt-ins, never a replacement.
            var routes = new List<string>
            {
                "/p1/sessions", "/p1/world/{id}", "/p1/quests/{id}", "/p1/inventory/{id}",
                "/p1/move", "/p1/combat",
                "/p1/v2/world/{id}", "/p1/v2/combat", "/p1/v2/events/{id}"
            };
            if (encounterEnabled)
            {
                routes.Add("/p1/encounters/current");
                routes.Add("/p1/encounters/{id}");
            }
            if (inventoryV2Enabled)
            {
                routes.Add("/p1/inventory/v2/{id}");
                routes.Add("/p1/inventory/v2/equip");
                routes.Add("/p1/inventory/v2/unequip");
            }
            if (deathReturnEnabled) routes.Add("/p1/actor/death-return");
            if (questTalkEnabled) routes.Add("/p1/quests/talk");
            if (portalEnabled) routes.Add("/p1/world/portal");
            if (mapViewedEnabled) routes.Add("/p1/quests/map-viewed");
            return new DeploymentProfile
            {
                ProfileId = "private-alpha",
                AlphaBossEnabled = encounterEnabled,
                AlphaInventoryV2Enabled = inventoryV2Enabled,
                DeathReturnEnabled = deathReturnEnabled,
                QuestTalkEnabled = questTalkEnabled,
                PortalEnabled = portalEnabled,
                MapViewedEnabled = mapViewedEnabled,
                ServerEnabledRoutes = routes,
                SourceVersion = "private-alpha"
            };
        }
    }

    public sealed class ClientCapability
    {
        public string ClientCoreVersion { get; set; } = "opc-15-0.3";
        public string ContractVersion { get; set; } = "v2";
        public string TargetFramework { get; set; } = "net8.0";
        public string DeploymentProfileId { get; set; } = "production-off";
        public string ServerSourceVersion { get; set; } = "eb79389";
        public List<string> SupportedClasses { get; set; } = new List<string> { "CLASS_MINH_KIEM" };

        // Routes this client implementation knows how to speak. This is NOT a claim
        // that the deployed server has them enabled.
        public List<string> SupportedRoutes { get; set; } = new List<string>
        {
            "/p1/sessions", "/p1/world/{id}", "/p1/quests/{id}", "/p1/inventory/{id}",
            "/p1/move", "/p1/combat",
            "/p1/v2/world/{id}", "/p1/v2/combat", "/p1/v2/events/{id}",
            "/p1/encounters/current", "/p1/encounters/{id}",
            "/p1/inventory/v2/{id}", "/p1/inventory/v2/equip", "/p1/inventory/v2/unequip",
            "/p1/actor/death-return",
            "/p1/quests/talk", "/p1/world/portal", "/p1/quests/map-viewed"
        };

        // Routes the deployment profile says the server actually exposes.
        public List<string> ServerEnabledRoutes { get; set; } = new List<string>();

        // Alpha gates are OFF unless an explicit private profile enables them.
        public bool AlphaBossEnabled { get; set; }
        public bool AlphaInventoryV2Enabled { get; set; }
        public bool DeathReturnEnabled { get; set; }
        public bool QuestTalkEnabled { get; set; }
        public bool PortalEnabled { get; set; }
        public bool MapViewedEnabled { get; set; }

        public bool IsEncounterUsable =>
            AlphaBossEnabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/encounters/current") &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/encounters/{id}");

        public bool IsInventoryV2Usable =>
            AlphaInventoryV2Enabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/inventory/v2/{id}") &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/inventory/v2/equip") &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/inventory/v2/unequip");

        public bool IsDeathReturnUsable =>
            DeathReturnEnabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/actor/death-return");

        public bool IsTalkUsable =>
            QuestTalkEnabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/quests/talk");

        public bool IsPortalUsable =>
            PortalEnabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/world/portal");

        public bool IsMapViewedUsable =>
            MapViewedEnabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/quests/map-viewed");

        public static ClientCapability FromProfile(DeploymentProfile profile)
        {
            if (profile == null) profile = DeploymentProfile.ProductionOff();
            return new ClientCapability
            {
                DeploymentProfileId = profile.ProfileId,
                ContractVersion = profile.ContractVersion,
                ServerSourceVersion = profile.SourceVersion,
                AlphaBossEnabled = profile.AlphaBossEnabled,
                AlphaInventoryV2Enabled = profile.AlphaInventoryV2Enabled,
                DeathReturnEnabled = profile.DeathReturnEnabled,
                QuestTalkEnabled = profile.QuestTalkEnabled,
                PortalEnabled = profile.PortalEnabled,
                MapViewedEnabled = profile.MapViewedEnabled,
                ServerEnabledRoutes = new List<string>(profile.ServerEnabledRoutes ?? new List<string>())
            };
        }
    }

    public static class CapabilityHandshake
    {
        public static bool IsRouteSupported(ClientCapability cap, string route)
        {
            if (cap == null || string.IsNullOrEmpty(route) || cap.SupportedRoutes == null) return false;
            foreach (var r in cap.SupportedRoutes) if (r == route) return true;
            return false;
        }

        public static bool IsRouteEnabled(ClientCapability cap, string route)
        {
            if (cap == null || string.IsNullOrEmpty(route) || cap.ServerEnabledRoutes == null) return false;
            foreach (var r in cap.ServerEnabledRoutes) if (r == route) return true;
            return false;
        }

        // Encounter routes additionally require the private alpha boss gate.
        public static bool IsEncounterUsable(ClientCapability cap)
        {
            if (cap == null || !cap.AlphaBossEnabled) return false;
            return IsRouteEnabled(cap, "/p1/encounters/current") &&
                   IsRouteEnabled(cap, "/p1/encounters/{id}");
        }

        public static bool IsInventoryV2Usable(ClientCapability cap)
        {
            if (cap == null || !cap.AlphaInventoryV2Enabled) return false;
            return IsRouteEnabled(cap, "/p1/inventory/v2/{id}") &&
                   IsRouteEnabled(cap, "/p1/inventory/v2/equip") &&
                   IsRouteEnabled(cap, "/p1/inventory/v2/unequip");
        }

        public static bool IsDeathReturnUsable(ClientCapability cap)
        {
            if (cap == null || !cap.DeathReturnEnabled) return false;
            return IsRouteEnabled(cap, "/p1/actor/death-return");
        }

        public static bool IsTalkUsable(ClientCapability cap)
        {
            if (cap == null || !cap.QuestTalkEnabled) return false;
            return IsRouteEnabled(cap, "/p1/quests/talk");
        }

        public static bool IsPortalUsable(ClientCapability cap)
        {
            if (cap == null || !cap.PortalEnabled) return false;
            return IsRouteEnabled(cap, "/p1/world/portal");
        }

        public static bool IsMapViewedUsable(ClientCapability cap)
        {
            if (cap == null || !cap.MapViewedEnabled) return false;
            return IsRouteEnabled(cap, "/p1/quests/map-viewed");
        }

        public static bool IsClassSupported(ClientCapability cap, string classId)
        {
            if (cap == null || string.IsNullOrEmpty(classId) || cap.SupportedClasses == null) return false;
            foreach (var c in cap.SupportedClasses) if (c == classId) return true;
            return false;
        }
    }
}
