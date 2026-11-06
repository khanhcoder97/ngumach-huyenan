// OPC-16 O5 — extended MMORPG service catalog tests. Services without an
// approved portable route must report Unsupported (never Available/Disabled by
// pretending a backend exists), and must not appear in the advertised route list.
// Owner: OpenCode.

using System;
using System.Linq;
using NguMach.Client.Core.Handshake;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class O5ExtendedServiceTests
    {
        private static readonly string[] ExtendedServiceIds =
        {
            "shop", "storage", "forge", "craft", "gather", "party", "guild",
            "social", "mail", "trade", "codex", "cosmetic", "buff", "activity"
        };

        [Fact]
        public void ExtendedServices_AreUnsupportedUnderEveryProfile()
        {
            var production = ServiceAvailabilityPolicy.Evaluate(
                ClientCapability.FromProfile(DeploymentProfile.ProductionOff()));
            var privateAlpha = ServiceAvailabilityPolicy.Evaluate(
                ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(
                    true, true, true, true, true, true)));

            for (int i = 0; i < ExtendedServiceIds.Length; i++)
            {
                string id = ExtendedServiceIds[i];
                var entry = production.Get(id);
                Assert.Equal(ServiceAvailabilityState.Unsupported, entry.State);
                Assert.Equal("route_not_implemented", entry.ReasonCode);
                Assert.False(entry.IsAvailable);
                Assert.False(production.CanCall(id));

                var alphaEntry = privateAlpha.Get(id);
                Assert.Equal(ServiceAvailabilityState.Unsupported, alphaEntry.State);
                Assert.Contains(id, production.UnsupportedServiceIds);
                Assert.Contains(id, privateAlpha.UnsupportedServiceIds);
            }
        }

        [Fact]
        public void ExtendedServices_NeverEnterAvailableOrDisabledAdvertisements()
        {
            var availability = ServiceAvailabilityPolicy.Evaluate(
                ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(
                    true, true, true, true, true, true)));

            for (int i = 0; i < ExtendedServiceIds.Length; i++)
            {
                Assert.DoesNotContain(ExtendedServiceIds[i], availability.AvailableServiceIds);
                Assert.DoesNotContain(ExtendedServiceIds[i], availability.DisabledServiceIds);
            }
        }

        [Fact]
        public void ExtendedServices_HaveVietnameseDisplayNamesAndNoInventedRoutes()
        {
            var cap = ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(
                true, true, true, true, true, true));
            var availability = ServiceAvailabilityPolicy.Evaluate(cap);

            Assert.Equal("Cửa hàng", availability.Get("shop").DisplayNameVi);
            Assert.Equal("Bang hội", availability.Get("guild").DisplayNameVi);
            Assert.Equal("Giao dịch", availability.Get("trade").DisplayNameVi);
            Assert.Contains("chưa có hợp đồng route", availability.Get("shop").ReasonVi);

            // The client must not claim a route it cannot call. Only the approved
            // routes are listed; the extended services stay out until a contract lands.
            Assert.DoesNotContain(cap.SupportedRoutes, r => r.IndexOf("shop", StringComparison.OrdinalIgnoreCase) >= 0);
            Assert.DoesNotContain(cap.SupportedRoutes, r => r.IndexOf("guild", StringComparison.OrdinalIgnoreCase) >= 0);
            Assert.DoesNotContain(cap.SupportedRoutes, r => r.IndexOf("mail", StringComparison.OrdinalIgnoreCase) >= 0);
        }

        [Fact]
        public void UnknownService_RemainsExplicitlyUnknownToTheClient()
        {
            var availability = ServiceAvailabilityPolicy.Evaluate(
                ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(false)));

            var entry = availability.Get("future-dungeon-finder");

            Assert.Equal(ServiceAvailabilityState.Unsupported, entry.State);
            Assert.Equal("service_unknown", entry.ReasonCode);
            Assert.Contains("không biết dịch vụ", entry.ReasonVi);
        }

        [Fact]
        public void ExistingGatedServices_StillEvaluateNormally()
        {
            var cap = ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(
                encounterEnabled: true,
                inventoryV2Enabled: true,
                deathReturnEnabled: true,
                questTalkEnabled: true,
                portalEnabled: true,
                mapViewedEnabled: true));
            var availability = ServiceAvailabilityPolicy.Evaluate(cap);

            Assert.True(availability.CanCall("quest-talk"));
            Assert.True(availability.CanCall("portal"));
            Assert.True(availability.CanCall("map-viewed"));
            Assert.True(availability.CanCall("death-return"));
            Assert.True(availability.CanCall("inventory-v2"));
            Assert.True(availability.CanCall("encounter"));
        }
    }
}
