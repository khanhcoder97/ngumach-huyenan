using NguMach.Client.Core.Catalog;
using NguMach.Client.Core.Handshake;
using System;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class CapabilityHandshakeTests
    {
        [Fact]
        public void SupportedClass_True()
        {
            var c = new ClientCapability();
            Assert.True(CapabilityHandshake.IsClassSupported(c, "CLASS_MINH_KIEM"));
        }

        [Fact]
        public void UnsupportedClass_False()
        {
            var c = new ClientCapability();
            Assert.False(CapabilityHandshake.IsClassSupported(c, "CLASS_FIRE_MAGE"));
        }

        [Fact]
        public void SupportedRoute_IsClientKnowledgeOnly()
        {
            var c = new ClientCapability();
            Assert.True(CapabilityHandshake.IsRouteSupported(c, "/p1/encounters/current"));
            Assert.True(CapabilityHandshake.IsRouteSupported(c, "/p1/encounters/{id}"));
            // Knowing the route does not claim the deployed server enabled it.
            Assert.False(CapabilityHandshake.IsRouteEnabled(c, "/p1/encounters/current"));
            Assert.False(CapabilityHandshake.IsRouteEnabled(c, "/p1/encounters/{id}"));
            Assert.False(c.IsEncounterUsable);
        }

        [Fact]
        public void UnsupportedRoute_False()
        {
            var c = new ClientCapability();
            Assert.False(CapabilityHandshake.IsRouteSupported(c, "/p1/nope"));
        }

        [Fact]
        public void NullCapability_False()
        {
            Assert.False(CapabilityHandshake.IsClassSupported(null, "x"));
            Assert.False(CapabilityHandshake.IsRouteSupported(null, "x"));
            Assert.False(CapabilityHandshake.IsRouteEnabled(null, "x"));
            Assert.False(CapabilityHandshake.IsEncounterUsable(null));
        }

        [Fact]
        public void DefaultProfile_IsProductionOff()
        {
            var cap = ClientCapability.FromProfile(DeploymentProfile.ProductionOff());
            Assert.Equal("production-off", cap.DeploymentProfileId);
            Assert.False(cap.AlphaBossEnabled);
            Assert.Empty(cap.ServerEnabledRoutes);
            Assert.False(cap.IsEncounterUsable);
            Assert.False(CapabilityHandshake.IsEncounterUsable(cap));
        }

        [Fact]
        public void PrivateAlpha_DistinguishesServerEnabledFromClientSupported()
        {
            var off = ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(false));
            Assert.False(off.AlphaBossEnabled);
            Assert.False(off.IsEncounterUsable);
            Assert.False(CapabilityHandshake.IsRouteEnabled(off, "/p1/encounters/current"));
            Assert.True(CapabilityHandshake.IsRouteSupported(off, "/p1/encounters/current"));

            var on = ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(true));
            Assert.True(on.AlphaBossEnabled);
            Assert.True(CapabilityHandshake.IsRouteEnabled(on, "/p1/encounters/current"));
            Assert.True(CapabilityHandshake.IsRouteEnabled(on, "/p1/encounters/{id}"));
            Assert.True(on.IsEncounterUsable);
            Assert.True(CapabilityHandshake.IsEncounterUsable(on));
        }

        [Fact]
        public void AlphaGateOnButRouteMissing_IsNotUsable()
        {
            var cap = ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(true));
            cap.ServerEnabledRoutes.Remove("/p1/encounters/{id}");
            Assert.False(cap.IsEncounterUsable);
            Assert.False(CapabilityHandshake.IsEncounterUsable(cap));
        }

        [Fact]
        public void AlphaGateOffWithRoutes_IsNotUsable()
        {
            var cap = new ClientCapability
            {
                AlphaBossEnabled = false,
                ServerEnabledRoutes = new System.Collections.Generic.List<string>
                {
                    "/p1/encounters/current", "/p1/encounters/{id}"
                }
            };
            Assert.False(cap.IsEncounterUsable);
            Assert.False(CapabilityHandshake.IsEncounterUsable(cap));
        }
    }

    public class FileProviderTests
    {
        [Fact]
        public void PhysicalProvider_RoundTrip()
        {
            var dir = System.IO.Path.GetTempPath();
            var p = System.IO.Path.Combine(dir, "cc_test_" + Guid.NewGuid().ToString("N") + ".txt");
            System.IO.File.WriteAllText(p, "hello");
            try
            {
                var prov = new PhysicalFileProvider();
                Assert.True(prov.Exists(p));
                Assert.Equal("hello", prov.ReadAllText(p));
                Assert.False(prov.Exists(p + ".nope"));
            }
            finally { System.IO.File.Delete(p); }
        }

        [Fact]
        public void InMemoryProvider_Reads()
        {
            var prov = new InMemoryFileProvider(path => path == "cat" ? "content" : null);
            Assert.True(prov.Exists("cat"));
            Assert.Equal("content", prov.ReadAllText("cat"));
            Assert.False(prov.Exists("missing"));
        }

        [Fact]
        public void CatalogLoader_MissingFile_Fails()
        {
            var prov = new InMemoryFileProvider(_ => null);
            Assert.False(CatalogLoader.TryLoad(prov, "nope", out var text, out var err));
            Assert.Null(text);
            Assert.False(string.IsNullOrEmpty(err));
        }

        [Fact]
        public void CatalogLoader_EmptyPath_Fails()
        {
            var prov = new InMemoryFileProvider(_ => "x");
            Assert.False(CatalogLoader.TryLoad(prov, "", out _, out var err));
            Assert.False(string.IsNullOrEmpty(err));
        }

        [Fact]
        public void CatalogLoader_NullProvider_Fails()
        {
            Assert.False(CatalogLoader.TryLoad(null, "p", out _, out var err));
            Assert.False(string.IsNullOrEmpty(err));
        }

        [Fact]
        public void CatalogLoader_Success_Reads()
        {
            var prov = new InMemoryFileProvider(_ => "payload");
            Assert.True(CatalogLoader.TryLoad(prov, "p", out var text, out var err));
            Assert.Equal("payload", text);
            Assert.Null(err);
        }
    }
}
