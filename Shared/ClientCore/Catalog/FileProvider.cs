// OPC-15 O-B — File/stream provider abstraction so the catalog loader can run
// against Godot's (or any) filesystem without UnityEngine.Resources.Load.
// Pure C#. The loader itself already accepts text; this adds DI-friendly access.

using System;
using System.IO;

namespace NguMach.Client.Core.Catalog
{
    public interface IFileProvider
    {
        bool Exists(string path);
        string ReadAllText(string path);
    }

    public sealed class InMemoryFileProvider : IFileProvider
    {
        private readonly Func<string, string> _reader;
        public InMemoryFileProvider(Func<string, string> reader) { _reader = reader ?? throw new ArgumentNullException(nameof(reader)); }
        public bool Exists(string path) { try { return _reader(path) != null; } catch { return false; } }
        public string ReadAllText(string path) { return _reader(path); }
    }

    public sealed class PhysicalFileProvider : IFileProvider
    {
        public bool Exists(string path) { return File.Exists(path); }
        public string ReadAllText(string path) { return File.ReadAllText(path); }
    }

    public static class CatalogLoader
    {
        // Loads catalog text from a provider; returns null + error on failure (never throws).
        public static bool TryLoad(IFileProvider provider, string path, out string text, out string error)
        {
            text = null; error = null;
            if (provider == null) { error = "no file provider"; return false; }
            if (string.IsNullOrEmpty(path)) { error = "empty path"; return false; }
            if (!provider.Exists(path)) { error = "catalog file not found: " + path; return false; }
            try { text = provider.ReadAllText(path); }
            catch (Exception e) { error = "read failed: " + e.Message; return false; }
            if (string.IsNullOrEmpty(text)) { error = "empty catalog"; return false; }
            return true;
        }
    }
}
