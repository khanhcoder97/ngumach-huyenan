using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UIElements;
using NguMach.Client.P1;

public sealed class TitleBootstrap : MonoBehaviour
{
    private const string DefaultHealthUrl = "http://127.0.0.1:5000/health";
    private UIDocument document;
    private Label statusLabel;
    private string healthUrl = DefaultHealthUrl;
    private int healthTimeoutSeconds = 3;
    private int healthPollIntervalSeconds = 10;
    private string apiBaseUrl = "http://127.0.0.1:5000";
    private int apiTimeoutSeconds = 5;
    private bool onlineV2Enabled;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void CreateTitle()
    {
        if (FindFirstObjectByType<TitleBootstrap>() != null) return;

        var gameObject = new GameObject("TitleBootstrap");
        DontDestroyOnLoad(gameObject);
        var document = gameObject.AddComponent<UIDocument>();
        document.panelSettings = ScriptableObject.CreateInstance<PanelSettings>();
        gameObject.AddComponent<TitleBootstrap>();
    }

    private void Start()
    {
        EnsurePixelPerfectCamera();
        LoadClientConfig();
        document = GetComponent<UIDocument>();
        BuildTitle();
        StartCoroutine(PollHealth());
    }

    private static void EnsurePixelPerfectCamera()
    {
        var gameCamera = Camera.main != null ? Camera.main : FindFirstObjectByType<Camera>();
        if (gameCamera == null)
        {
            var cameraObject = new GameObject("PixelPerfectCamera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(0f, 0f, -10f);
            gameCamera = cameraObject.AddComponent<Camera>();
        }

        if (gameCamera.GetComponent<PixelArtCameraBootstrap>() == null)
            gameCamera.gameObject.AddComponent<PixelArtCameraBootstrap>();
        if (FindFirstObjectByType<AudioListener>() == null)
            gameCamera.gameObject.AddComponent<AudioListener>();
    }

    private void LoadClientConfig()
    {
        var configAsset = Resources.Load<TextAsset>("client-config.local") ?? Resources.Load<TextAsset>("client-config");
        if (configAsset == null || string.IsNullOrWhiteSpace(configAsset.text))
            return;

        try
        {
            var config = JsonUtility.FromJson<ClientRuntimeConfig>(configAsset.text);
            if (config == null)
                return;

            if (Uri.TryCreate(config.healthUrl, UriKind.Absolute, out var endpoint) &&
                (endpoint.Scheme == Uri.UriSchemeHttp || endpoint.Scheme == Uri.UriSchemeHttps))
                healthUrl = config.healthUrl;

            if (config.healthTimeoutSeconds is >= 1 and <= 30)
                healthTimeoutSeconds = config.healthTimeoutSeconds;
            if (config.healthPollIntervalSeconds is >= 2 and <= 120)
                healthPollIntervalSeconds = config.healthPollIntervalSeconds;
            if (!string.IsNullOrWhiteSpace(config.apiBaseUrl)) apiBaseUrl = config.apiBaseUrl;
            else apiBaseUrl = new Uri(healthUrl).GetLeftPart(UriPartial.Authority);
            onlineV2Enabled = config.onlineV2Enabled;
            if (config.apiTimeoutSeconds is >= 1 and <= 30) apiTimeoutSeconds = config.apiTimeoutSeconds;
        }
        catch (ArgumentException)
        {
            Debug.LogWarning("Client config is invalid; using the local health endpoint.");
        }
    }

    [Serializable]
    private sealed class ClientRuntimeConfig
    {
        public string healthUrl;
        public int healthTimeoutSeconds;
        public int healthPollIntervalSeconds;
        public string apiBaseUrl;
        public int apiTimeoutSeconds;
        public bool onlineV2Enabled;
    }

    private void BuildTitle()
    {
        var root = document.rootVisualElement;
        root.Clear();
        root.style.flexGrow = 1;
        root.style.minHeight = Length.Percent(100);
        root.style.flexDirection = FlexDirection.Column;
        root.style.alignItems = Align.Center;
        root.style.justifyContent = Justify.Center;
        root.style.backgroundColor = new Color(0.08f, 0.07f, 0.11f);
        root.style.color = Color.white;

        var title = new Label("Ngũ Mạch: Huyền Ấn");
        title.style.fontSize = 36;
        title.style.unityFontStyleAndWeight = FontStyle.Bold;
        title.style.color = new Color(0.91f, 0.74f, 0.40f);
        root.Add(title);

        statusLabel = new Label("Đang kết nối máy chủ…");
        statusLabel.style.marginTop = 18;
        root.Add(statusLabel);

        var startButton = new Button(BeginOnline) { text = P1Copy.Get("title.start") };
        startButton.style.marginTop = 28;
        root.Add(startButton);
    }

    private void BeginOnline()
    {
        if (GetComponent<P1OnlinePanel>() != null) return;
        StopAllCoroutines();
        var panel = gameObject.AddComponent<P1OnlinePanel>();
        panel.Open(document, apiBaseUrl, apiTimeoutSeconds, () =>
        {
            BuildTitle();
            StartCoroutine(PollHealth());
        }, onlineV2Enabled);
    }

    private IEnumerator PollHealth()
    {
        while (true)
        {
            using (var request = UnityWebRequest.Get(healthUrl))
            {
                request.timeout = healthTimeoutSeconds;
                request.SetRequestHeader("X-Correlation-ID", Guid.NewGuid().ToString("N"));
                yield return request.SendWebRequest();

                var online = request.result == UnityWebRequest.Result.Success &&
                             request.responseCode >= 200 && request.responseCode < 300;
                statusLabel.text = online ? "Máy chủ: Trực tuyến" : "Máy chủ: Ngoại tuyến";
                statusLabel.style.color = online ? new Color(0.42f, 0.83f, 0.58f) : new Color(0.91f, 0.42f, 0.38f);
            }

            yield return new WaitForSecondsRealtime(healthPollIntervalSeconds);
        }
    }
}
