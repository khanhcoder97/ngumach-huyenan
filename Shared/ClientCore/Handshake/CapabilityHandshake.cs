// OPC-15 O-C — Handshake / capability model so Muse knows which endpoints and
// classes are available before calling. Pure C#, no engine dep.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Core.Handshake
{
    public sealed class ClientCapability
    {
        public string ClientCoreVersion { get; set; } = "opc-15-0.1";
        public string ContractVersion { get; set; } = "v1";
        public string TargetFramework { get; set; } = "net8.0";
        public List<string> SupportedClasses { get; set; } = new List<string> { "CLASS_MINH_KIEM" };
        public List<string> SupportedRoutes { get; set; } = new List<string>
        {
            "/p1/sessions", "/p1/world/{id}", "/p1/quests/{id}", "/p1/inventory/{id}",
            "/p1/encounters/current", "/p1/encounters/{id}"
        };
        public bool AlphaBossEnabled { get; set; } = false; // gate OFF by default
    }

    public static class CapabilityHandshake
    {
        public static bool IsRouteSupported(ClientCapability cap, string route)
        {
            if (cap == null || string.IsNullOrEmpty(route)) return false;
            foreach (var r in cap.SupportedRoutes) if (r == route) return true;
            return false;
        }
        public static bool IsClassSupported(ClientCapability cap, string classId)
        {
            if (cap == null || string.IsNullOrEmpty(classId)) return false;
            foreach (var c in cap.SupportedClasses) if (c == classId) return true;
            return false;
        }
    }
}
