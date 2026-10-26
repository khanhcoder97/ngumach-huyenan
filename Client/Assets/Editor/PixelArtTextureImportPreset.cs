#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

/// <summary>
/// Enforces lossless point-sampled sprite imports for project art folders.
/// Put source art under Assets/Art or Assets/UI/Art to receive these defaults.
/// </summary>
public sealed class PixelArtTextureImportPreset : AssetPostprocessor
{
    private const string ArtRoot = "Assets/Art/";
    private const string UiArtRoot = "Assets/UI/Art/";

    private void OnPreprocessTexture()
    {
        if (!assetPath.StartsWith(ArtRoot, System.StringComparison.OrdinalIgnoreCase) &&
            !assetPath.StartsWith(UiArtRoot, System.StringComparison.OrdinalIgnoreCase))
            return;

        var importer = (TextureImporter)assetImporter;
        importer.textureType = TextureImporterType.Sprite;
        importer.spritePixelsPerUnit = 20;
        importer.filterMode = FilterMode.Point;
        importer.textureCompression = TextureImporterCompression.Uncompressed;
        importer.mipmapEnabled = false;
        importer.alphaIsTransparency = true;
        importer.wrapMode = TextureWrapMode.Clamp;
        importer.npotScale = TextureImporterNPOTScale.None;
        importer.isReadable = false;
    }
}
#endif
