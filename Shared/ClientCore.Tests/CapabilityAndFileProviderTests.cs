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
        public void SupportedRoute_True()
        {
            var c = new ClientCapability();
            Assert.True(CapabilityHandshake.IsRouteSupported(c, "/p1/encounters/current"));
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
