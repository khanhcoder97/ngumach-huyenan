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
        public string ContractVersion { get; set; } = "v1";
        public bool AlphaBossEnabled { get; set; }
        public List<string> ServerEnabledRoutes { get; set; } = new List<string>();
        public string SourceVersion { get; set; } = "unknown";

        public static DeploymentProfile ProductionOff()
        {
            return new DeploymentProfile
            {
                ProfileId = "production-off",
                AlphaBossEnabled = false,
                ServerEnabledRoutes = new List<string>(),
                SourceVersion = "unknown"
            };
        }

        public static DeploymentProfile PrivateAlpha(bool encounterEnabled)
        {
            return new DeploymentProfile
            {
                ProfileId = "private-alpha",
                AlphaBossEnabled = encounterEnabled,
                ServerEnabledRoutes = encounterEnabled
                    ? new List<string> { "/p1/encounters/current", "/p1/encounters/{id}" }
                    : new List<string>(),
                SourceVersion = "private-alpha"
            };
        }
    }

    public sealed class ClientCapability
    {
        public string ClientCoreVersion { get; set; } = "opc-15-0.2";
        public string ContractVersion { get; set; } = "v1";
        public string TargetFramework { get; set; } = "net8.0";
        public string DeploymentProfileId { get; set; } = "production-off";
        public string ServerSourceVersion { get; set; } = "unknown";
        public List<string> SupportedClasses { get; set; } = new List<string> { "CLASS_MINH_KIEM" };

        // Routes this client implementation knows how to speak. This is NOT a claim
        // that the deployed server has them enabled.
        public List<string> SupportedRoutes { get; set; } = new List<string>
        {
            "/p1/sessions", "/p1/world/{id}", "/p1/quests/{id}", "/p1/inventory/{id}",
            "/p1/encounters/current", "/p1/encounters/{id}"
        };

        // Routes the deployment profile says the server actually exposes.
        public List<string> ServerEnabledRoutes { get; set; } = new List<string>();

        // Alpha gate is OFF unless an explicit private profile enables it.
        public bool AlphaBossEnabled { get; set; }

        public bool IsEncounterUsable =>
            AlphaBossEnabled &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/encounters/current") &&
            CapabilityHandshake.IsRouteEnabled(this, "/p1/encounters/{id}");

        public static ClientCapability FromProfile(DeploymentProfile profile)
        {
            if (profile == null) profile = DeploymentProfile.ProductionOff();
            return new ClientCapability
            {
                DeploymentProfileId = profile.ProfileId,
                ContractVersion = profile.ContractVersion,
                ServerSourceVersion = profile.SourceVersion,
                AlphaBossEnabled = profile.AlphaBossEnabled,
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

        public static bool IsClassSupported(ClientCapability cap, string classId)
        {
            if (cap == null || string.IsNullOrEmpty(classId) || cap.SupportedClasses == null) return false;
            foreach (var c in cap.SupportedClasses) if (c == classId) return true;
            return false;
        }
    }
}
