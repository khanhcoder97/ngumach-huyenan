using UnityEngine;
using UnityEngine.Rendering.Universal;

/// <summary>
/// Applies the project's locked pixel grid to the primary gameplay camera.
/// Keep this component on the camera rather than creating camera settings in UI code.
/// </summary>
[RequireComponent(typeof(Camera))]
[DisallowMultipleComponent]
public sealed class PixelArtCameraBootstrap : MonoBehaviour
{
    public const int ReferenceWidth = 640;
    public const int ReferenceHeight = 360;
    public const int PixelsPerUnit = 20;

    [SerializeField] private Camera targetCamera;
    [SerializeField] private PixelPerfectCamera pixelPerfectCamera;

    private void Reset()
    {
        ResolveComponents();
        ApplySettings();
    }

    private void Awake()
    {
        ResolveComponents();
        ApplySettings();
    }

    private void ResolveComponents()
    {
        if (targetCamera == null)
            targetCamera = GetComponent<Camera>();

        if (pixelPerfectCamera == null)
            pixelPerfectCamera = GetComponent<PixelPerfectCamera>();

        if (pixelPerfectCamera == null)
            pixelPerfectCamera = gameObject.AddComponent<PixelPerfectCamera>();
    }

    private void ApplySettings()
    {
        if (targetCamera == null || pixelPerfectCamera == null)
            return;

        targetCamera.orthographic = true;
        targetCamera.allowHDR = false;
        targetCamera.allowMSAA = false;
        targetCamera.allowDynamicResolution = false;
        pixelPerfectCamera.assetsPPU = PixelsPerUnit;
        pixelPerfectCamera.refResolutionX = ReferenceWidth;
        pixelPerfectCamera.refResolutionY = ReferenceHeight;
        pixelPerfectCamera.gridSnapping = PixelPerfectCamera.GridSnapping.PixelSnapping;
        // None preserves extra horizontal world visibility on wide screens.
        pixelPerfectCamera.cropFrame = PixelPerfectCamera.CropFrame.None;
    }
}
