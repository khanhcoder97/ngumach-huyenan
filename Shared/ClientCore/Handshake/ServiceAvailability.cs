// OPC-16 O5 — deployment service availability policy.
// Distinguishes what this client can speak, what the deployment profile says is
// enabled, and what is simply unknown. It never probes a route, never turns a
// 404 into "available", and never enables an alpha gate on its own.
// Pure C#, no engine dependency. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;

namespace NguMach.Client.Core.Handshake
{
    public enum ServiceAvailabilityState
    {
        Available,
        Disabled,
        Unsupported,
        Unknown
    }

    public sealed class ServiceAvailabilityEntry
    {
        public string ServiceId { get; }
        public string DisplayNameVi { get; }
        public ServiceAvailabilityState State { get; }
        public string Gate { get; }
        public string ReasonCode { get; }
        public string ReasonVi { get; }

        internal ServiceAvailabilityEntry(
            string serviceId, string displayNameVi, ServiceAvailabilityState state,
            string gate, string reasonCode, string reasonVi)
        {
            ServiceId = serviceId;
            DisplayNameVi = displayNameVi;
            State = state;
            Gate = gate;
            ReasonCode = reasonCode;
            ReasonVi = reasonVi;
        }

        public bool IsAvailable => State == ServiceAvailabilityState.Available;
    }

    public sealed class ServiceAvailability
    {
        public IReadOnlyDictionary<string, ServiceAvailabilityEntry> Services { get; }
        public IReadOnlyList<string> AvailableServiceIds { get; }
        public IReadOnlyList<string> DisabledServiceIds { get; }

        internal ServiceAvailability(IReadOnlyDictionary<string, ServiceAvailabilityEntry> services)
        {
            Services = services;
            var available = new List<string>();
            var disabled = new List<string>();
            foreach (var pair in services)
            {
                if (pair.Value.IsAvailable) available.Add(pair.Key);
                else if (pair.Value.State == ServiceAvailabilityState.Disabled) disabled.Add(pair.Key);
            }
            available.Sort(StringComparer.Ordinal);
            disabled.Sort(StringComparer.Ordinal);
            AvailableServiceIds = new ReadOnlyCollection<string>(available);
            DisabledServiceIds = new ReadOnlyCollection<string>(disabled);
        }

        public ServiceAvailabilityEntry Get(string serviceId)
        {
            if (serviceId == null) return ServiceAvailabilityPolicy.Unsupported(null);
            ServiceAvailabilityEntry entry;
            return Services.TryGetValue(serviceId, out entry)
                ? entry
                : ServiceAvailabilityPolicy.Unsupported(serviceId);
        }

        public bool CanCall(string serviceId) => Get(serviceId).IsAvailable;
    }

    public static class ServiceAvailabilityPolicy
    {
        private const string GateAlphaBoss = "AlphaBossEnabled";
        private const string GateInventoryV2 = "AlphaInventoryV2Enabled";
        private const string GateDeathReturn = "DeathReturnEnabled";
        private const string GateQuestTalk = "QuestTalkEnabled";
        private const string GatePortal = "PortalEnabled";
        private const string GateMapViewed = "MapViewedEnabled";

        private sealed class Definition
        {
            public string Id;
            public string DisplayVi;
            public string Gate;
            public string[] Routes;
        }

        private static readonly Definition[] Definitions =
        {
            new Definition { Id = "sessions", DisplayVi = "Tạo phiên", Routes = new[] { "/p1/sessions" } },
            new Definition { Id = "world-v1", DisplayVi = "Thế giới v1", Routes = new[] { "/p1/world/{id}" } },
            new Definition { Id = "quests", DisplayVi = "Nhiệm vụ", Routes = new[] { "/p1/quests/{id}" } },
            new Definition { Id = "inventory-v1", DisplayVi = "Túi v1", Routes = new[] { "/p1/inventory/{id}" } },
            new Definition { Id = "move", DisplayVi = "Di chuyển", Routes = new[] { "/p1/move" } },
            new Definition { Id = "combat-v1", DisplayVi = "Chiến đấu v1", Routes = new[] { "/p1/combat" } },
            new Definition { Id = "world-v2", DisplayVi = "Thế giới v2", Routes = new[] { "/p1/v2/world/{id}" } },
            new Definition { Id = "combat-v2", DisplayVi = "Chiến đấu v2", Routes = new[] { "/p1/v2/combat" } },
            new Definition { Id = "events-v2", DisplayVi = "Sự kiện v2", Routes = new[] { "/p1/v2/events/{id}" } },
            new Definition
            {
                Id = "encounter", DisplayVi = "Trận boss", Gate = GateAlphaBoss,
                Routes = new[] { "/p1/encounters/current", "/p1/encounters/{id}" }
            },
            new Definition
            {
                Id = "inventory-v2", DisplayVi = "Túi 12 ô", Gate = GateInventoryV2,
                Routes = new[] { "/p1/inventory/v2/{id}", "/p1/inventory/v2/equip", "/p1/inventory/v2/unequip" }
            },
            new Definition
            {
                Id = "death-return", DisplayVi = "Hồi sinh", Gate = GateDeathReturn,
                Routes = new[] { "/p1/actor/death-return" }
            },
            new Definition
            {
                Id = "quest-talk", DisplayVi = "Nói chuyện NPC", Gate = GateQuestTalk,
                Routes = new[] { "/p1/quests/talk" }
            },
            new Definition
            {
                Id = "portal", DisplayVi = "Cổng chuyển cảnh", Gate = GatePortal,
                Routes = new[] { "/p1/world/portal" }
            },
            new Definition
            {
                Id = "map-viewed", DisplayVi = "Đánh dấu bản đồ", Gate = GateMapViewed,
                Routes = new[] { "/p1/quests/map-viewed" }
            }
        };

        public static ServiceAvailability Evaluate(ClientCapability capability)
        {
            if (capability == null) capability = ClientCapability.FromProfile(DeploymentProfile.ProductionOff());
            var services = new Dictionary<string, ServiceAvailabilityEntry>(StringComparer.Ordinal);
            for (int i = 0; i < Definitions.Length; i++)
            {
                var definition = Definitions[i];
                services[definition.Id] = Evaluate(capability, definition);
            }
            return new ServiceAvailability(new ReadOnlyDictionary<string, ServiceAvailabilityEntry>(services));
        }

        public static ServiceAvailabilityEntry Evaluate(ClientCapability capability, string serviceId)
        {
            if (serviceId == null) return Unsupported(null);
            for (int i = 0; i < Definitions.Length; i++)
                if (Definitions[i].Id == serviceId)
                    return Evaluate(capability ?? ClientCapability.FromProfile(DeploymentProfile.ProductionOff()), Definitions[i]);
            return Unsupported(serviceId);
        }

        private static ServiceAvailabilityEntry Evaluate(ClientCapability capability, Definition definition)
        {
            for (int i = 0; i < definition.Routes.Length; i++)
            {
                if (!CapabilityHandshake.IsRouteSupported(capability, definition.Routes[i]))
                {
                    return new ServiceAvailabilityEntry(definition.Id, definition.DisplayVi,
                        ServiceAvailabilityState.Unsupported, definition.Gate,
                        "client_unsupported", "Client chưa hỗ trợ route của dịch vụ này.");
                }
            }

            if (definition.Gate != null && !GateEnabled(capability, definition.Gate))
            {
                return new ServiceAvailabilityEntry(definition.Id, definition.DisplayVi,
                    ServiceAvailabilityState.Disabled, definition.Gate,
                    "alpha_gate_off", "Dịch vụ đang tắt trên máy chủ (cổng alpha chưa bật).");
            }

            bool anyRouteListed = false;
            for (int i = 0; i < definition.Routes.Length; i++)
            {
                if (CapabilityHandshake.IsRouteEnabled(capability, definition.Routes[i]))
                {
                    anyRouteListed = true;
                    break;
                }
            }

            if (anyRouteListed && !AllRoutesEnabled(capability, definition.Routes))
            {
                return new ServiceAvailabilityEntry(definition.Id, definition.DisplayVi,
                    ServiceAvailabilityState.Disabled, definition.Gate,
                    "route_not_advertised", "Máy chủ chưa công bố đủ route của dịch vụ này.");
            }

            if (anyRouteListed)
            {
                return new ServiceAvailabilityEntry(definition.Id, definition.DisplayVi,
                    ServiceAvailabilityState.Available, definition.Gate, null, "Dịch vụ đã được công bố.");
            }

            // An empty route list is not evidence that a core route is off: no
            // capability endpoint exists yet, so the profile cannot say either way.
            if (definition.Gate == null)
            {
                return new ServiceAvailabilityEntry(definition.Id, definition.DisplayVi,
                    ServiceAvailabilityState.Unknown, null,
                    "profile_unknown", "Chưa có hồ sơ triển khai; không thể xác nhận dịch vụ.");
            }

            return new ServiceAvailabilityEntry(definition.Id, definition.DisplayVi,
                ServiceAvailabilityState.Disabled, definition.Gate,
                "route_not_advertised", "Máy chủ chưa công bố route của dịch vụ này.");
        }

        private static bool AllRoutesEnabled(ClientCapability capability, string[] routes)
        {
            for (int i = 0; i < routes.Length; i++)
                if (!CapabilityHandshake.IsRouteEnabled(capability, routes[i])) return false;
            return true;
        }

        private static bool GateEnabled(ClientCapability capability, string gate)
        {
            if (gate == GateAlphaBoss) return capability.AlphaBossEnabled;
            if (gate == GateInventoryV2) return capability.AlphaInventoryV2Enabled;
            if (gate == GateDeathReturn) return capability.DeathReturnEnabled;
            if (gate == GateQuestTalk) return capability.QuestTalkEnabled;
            if (gate == GatePortal) return capability.PortalEnabled;
            if (gate == GateMapViewed) return capability.MapViewedEnabled;
            return false;
        }

        internal static ServiceAvailabilityEntry Unsupported(string serviceId)
        {
            return new ServiceAvailabilityEntry(serviceId, serviceId,
                ServiceAvailabilityState.Unsupported, null,
                "service_unknown", "Client không biết dịch vụ này.");
        }
    }
}
