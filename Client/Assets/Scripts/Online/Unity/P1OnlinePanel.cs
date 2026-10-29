using System;
using System.Globalization;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UIElements;

namespace NguMach.Client.P1
{
    // Functional P1 HUD; final pixel skin/icons are still supplied by Muse.
    [DisallowMultipleComponent]
    public sealed class P1OnlinePanel : MonoBehaviour
    {
        private UIDocument document;
        private P1Client client;
        private CancellationTokenSource life;
        private Action returnToTitle;
        private Label status, vitals, location, message, detailText, targetText;
        private VisualElement details, safeRoot, wheel;
        private Button accept, retry, sync, leave, attack;
        private readonly Button[] skills = new Button[6];
        private Vector2 touchMove, keyboardMove;
        private bool touchHeld, actionBusy, closing;
        private P1ActorPresenter presenter;
        private GameObject proxy;
        private Texture2D proxyTexture;
        private Sprite proxySprite;
        private Transform cameraTransform;
        private Vector3 originalCameraPosition;
        private P1World appliedWorld;
        private DateTimeOffset sampledServerTime;
        private float sampledAt;
        private string selectedTarget;
        private string detailMode = "quests";
        private float pollAt, listsAt;

        public void Open(UIDocument ui, string serverOrigin, int timeoutSeconds, Action onClose)
        {
            document = ui; returnToTitle = onClose;
            life = new CancellationTokenSource();
            try
            {
                client = new P1Client(new P1UnityTransport(serverOrigin, timeoutSeconds));
                Build();
                _ = StartOnline();
            }
            catch (Exception e) { Debug.LogError("P1 client initialization: " + e.Message); Close(); }
        }
        private async Task StartOnline()
        {
            actionBusy = true; Render();
            try
            {
                Show(await client.ConnectAsync(life.Token));
                if (client.World != null)
                {
                    BindActor(); ApplyWorld();
                    Show(await client.ReadQuestsAsync(life.Token));
                    Show(await client.ReadInventoryAsync(life.Token));
                }
            }
            catch (OperationCanceledException) { return; }
            catch (Exception e) { Debug.LogException(e); message.text = P1Copy.Get("error.unexpected"); }
            finally { actionBusy = false; if (!closing) Render(); }
            if (!closing && client.SessionId != null) await PollLoop();
        }
        private async Task PollLoop()
        {
            try
            {
                while (!life.IsCancellationRequested)
                {
                    if (!actionBusy && client.SessionId != null)
                    {
                        Vector2 movement = details.style.display.value == DisplayStyle.Flex ? Vector2.zero : touchHeld ? touchMove : keyboardMove;
                        if (client.State == P1ConnectionState.Ready && movement.sqrMagnitude > 0.001f)
                        {
                            Show(await client.MoveAsync(movement.x, movement.y, life.Token));
                            ApplyWorld();
                        }
                        else if (Time.realtimeSinceStartup >= pollAt)
                        {
                            pollAt = Time.realtimeSinceStartup + 0.5f;
                            Show(await client.ReadWorldAsync(life.Token)); ApplyWorld();
                            if (presenter != null) presenter.SetIdle();
                        }
                        if (Time.realtimeSinceStartup >= listsAt && !actionBusy && client.SessionId != null)
                        {
                            listsAt = Time.realtimeSinceStartup + 5;
                            Show(await client.ReadQuestsAsync(life.Token));
                            Show(await client.ReadInventoryAsync(life.Token));
                        }
                        Render();
                    }
                    await Task.Delay(100, life.Token); // No queue of old movement input behind a slow request.
                }
            }
            catch (OperationCanceledException) { }
            catch (Exception e) { Debug.LogException(e); if (!closing) message.text = P1Copy.Get("error.unexpected"); }
        }
        private void Update()
        {
            if (client == null || closing) return;
            keyboardMove = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical")).normalized;
            if (presenter != null && !touchHeld && keyboardMove.sqrMagnitude < 0.001f) presenter.SetIdle();
            if (Input.GetKeyDown(KeyCode.Alpha1)) Cast(0);
            if (Input.GetKeyDown(KeyCode.Alpha2)) Cast(1);
            if (Input.GetKeyDown(KeyCode.Alpha3)) Cast(2);
            if (Input.GetKeyDown(KeyCode.F)) AcceptQuest();
            RenderCooldowns();
        }
        private void OnApplicationFocus(bool focused) { if (!focused) { keyboardMove = touchMove = Vector2.zero; touchHeld = false; } }
        private async void RunAction(Func<Task<P1Result>> action)
        {
            if (actionBusy || closing) return;
            actionBusy = true; touchHeld = false; touchMove = keyboardMove = Vector2.zero; Render();
            try { Show(await action()); if (!closing) ApplyWorld(); }
            catch (OperationCanceledException) { }
            catch (Exception e) { Debug.LogException(e); if (!closing) message.text = P1Copy.Get("error.unexpected"); }
            finally { actionBusy = false; if (!closing) Render(); }
        }
        private void AcceptQuest()
        {
            if (client.State != P1ConnectionState.Ready) return;
            RunAction(() => client.AcceptQuestAsync("P00-01", "NPC_LYAN", life.Token));
        }
        private void Cast(int slot)
        {
            if (slot >= 3 || !skills[slot].enabledSelf) return;
            var aim = presenter == null ? Vector2.down : presenter.Facing;
            string target = slot == 0 ? null : selectedTarget;
            RunAction(() => client.CastAsync("SK-MK-0" + (slot + 1), target, aim.x, aim.y, life.Token));
        }
        private void Show(P1Result result)
        {
            if (closing || message == null) return;
            if (!result.Success)
            {
                string copy = P1Copy.Get("error." + result.Code);
                message.text = copy.StartsWith("error.", StringComparison.Ordinal) ? P1Copy.Get("error.generic") : copy;
                message.tooltip = result.Code + (result.CorrelationId == null ? "" : " · " + result.CorrelationId);
            }
            else if (client.State == P1ConnectionState.Ready) { message.text = P1Copy.Get("ui.prototype"); message.tooltip = ""; }
        }
        private void BindActor()
        {
            var actors = FindObjectsByType<PlayerController2D>(FindObjectsSortMode.None);
            GameObject actor;
            if (actors.Length == 1) actor = actors[0].gameObject;
            else
            {
                proxy = new GameObject("P1_Network_Position_Placeholder"); actor = proxy;
                proxyTexture = new Texture2D(12, 16, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
                var pixels = new Color[12 * 16];
                for (int i = 0; i < pixels.Length; i++) pixels[i] = new Color(0.38f, 0.8f, 0.75f);
                proxyTexture.SetPixels(pixels); proxyTexture.Apply();
                proxySprite = Sprite.Create(proxyTexture, new Rect(0, 0, 12, 16), new Vector2(0.5f, 0), 20);
                actor.AddComponent<SpriteRenderer>().sprite = proxySprite;
            }
            presenter = actor.AddComponent<P1ActorPresenter>(); presenter.Bind();
            if (Camera.main != null) { cameraTransform = Camera.main.transform; originalCameraPosition = cameraTransform.position; }
        }
        private void ApplyWorld()
        {
            if (client.World == null || ReferenceEquals(appliedWorld, client.World)) return;
            appliedWorld = client.World;
            if (presenter != null) presenter.Apply(appliedWorld);
            if (cameraTransform != null) cameraTransform.position = new Vector3((float)appliedWorld.self.x, (float)appliedWorld.self.y, originalCameraPosition.z);
            if (DateTimeOffset.TryParse(appliedWorld.serverTimeUtc, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var serverTime))
            { sampledServerTime = serverTime; sampledAt = Time.realtimeSinceStartup; }
        }
        private void Build()
        {
            var root = document.rootVisualElement; root.Clear();
            root.style.backgroundColor = Color.clear;
            safeRoot = new VisualElement { name = "p1-safe-root", pickingMode = PickingMode.Ignore };
            safeRoot.style.position = Position.Absolute; safeRoot.style.left = 0; safeRoot.style.top = 0; safeRoot.style.right = 0; safeRoot.style.bottom = 0;
            root.Add(safeRoot);
            var statusPanel = Panel(); statusPanel.style.left = 10; statusPanel.style.top = 10; statusPanel.style.width = 270;
            status = Text("connection.Connecting"); vitals = new Label(); location = new Label();
            statusPanel.Add(status); statusPanel.Add(vitals); statusPanel.Add(location); safeRoot.Add(statusPanel);
            var toolbar = new VisualElement(); toolbar.style.flexDirection = FlexDirection.Row; toolbar.style.flexWrap = Wrap.Wrap;
            toolbar.Add(ActionButton("ui.journal", () => ToggleDetails("quests")));
            toolbar.Add(ActionButton("ui.bag", () => ToggleDetails("inventory")));
            sync = ActionButton("ui.sync", () => RunAction(async () => { var r = await client.ReadWorldAsync(life.Token); if (!r.Success) return r;
                r = await client.ReadQuestsAsync(life.Token); return r.Success ? await client.ReadInventoryAsync(life.Token) : r; })); toolbar.Add(sync);
            retry = ActionButton("ui.retry", () => RunAction(() => client.RetryPendingAsync(life.Token))); toolbar.Add(retry);
            leave = ActionButton("ui.leave", Close); toolbar.Add(leave); statusPanel.Add(toolbar);
            message = new Label(P1Copy.Get("ui.prototype")) { enableRichText = false }; message.style.whiteSpace = WhiteSpace.Normal; statusPanel.Add(message);
            details = Panel(); details.style.left = 10; details.style.top = 180; details.style.width = 300; details.style.display = DisplayStyle.None;
            var scroll = new ScrollView(); detailText = new Label { enableRichText = false }; detailText.style.whiteSpace = WhiteSpace.Normal; scroll.Add(detailText); details.Add(scroll);
            accept = ActionButton("quest.accept", AcceptQuest); details.Add(accept); safeRoot.Add(details);
            root.RegisterCallback<GeometryChangedEvent>(evt => { details.style.maxHeight = Mathf.Max(60, evt.newRect.height - 200); UpdateSafeArea(); });
            var movement = Panel(); movement.style.left = 10; movement.style.bottom = 10; movement.style.width = 168; movement.style.height = 168;
            var axes = new[] { new Vector2(-1,1), Vector2.up, new Vector2(1,1), Vector2.left, Vector2.zero, Vector2.right, new Vector2(-1,-1), Vector2.down, new Vector2(1,-1) };
            var names = new[] { "NW", "N", "NE", "W", "·", "E", "SW", "S", "SE" };
            for (int i = 0; i < 9; i++)
            {
                var direction = axes[i].normalized; var button = new Button { text = names[i] }; button.style.position = Position.Absolute;
                button.style.left = i % 3 * 54; button.style.top = i / 3 * 54; button.style.width = 54; button.style.height = 54;
                button.RegisterCallback<PointerDownEvent>(ev => { touchMove = direction; touchHeld = true; button.CapturePointer(ev.pointerId); ev.StopPropagation(); });
                button.RegisterCallback<PointerUpEvent>(ev => { touchHeld = false; touchMove = Vector2.zero; button.ReleasePointer(ev.pointerId); ev.StopPropagation(); });
                button.RegisterCallback<PointerCaptureOutEvent>(ev => { touchHeld = false; touchMove = Vector2.zero; });
                movement.Add(button);
            }
            safeRoot.Add(movement);
            wheel = new VisualElement { pickingMode = PickingMode.Ignore }; wheel.style.position = Position.Absolute; wheel.style.right = 10; wheel.style.bottom = 10;
            wheel.style.width = 320; wheel.style.height = 320;
            // Same angles as DEC-019. Larger orbit maintains separate >=54px hit targets.
            attack = new Button { text = P1Copy.Get("skill.attack") }; Circle(attack, 230, 230, 92); attack.SetEnabled(false); attack.tooltip = P1Copy.Get("skill.basicMissing"); wheel.Add(attack);
            float[] angles = { 200, 174, 148, 122, 96, 70 };
            for (int i = 0; i < 6; i++)
            {
                int slot = i; var button = new Button(() => Cast(slot));
                button.text = P1Copy.Get("skill." + (i + 1)); button.tooltip = i >= 3 ? P1Copy.Get("skill.notReady") : button.text;
                float rad = angles[i] * Mathf.Deg2Rad; Circle(button, 230 + 144 * Mathf.Cos(rad), 230 - 144 * Mathf.Sin(rad), 54);
                skills[i] = button; wheel.Add(button);
            }
            targetText = Text("target.none"); targetText.style.position = Position.Absolute; targetText.style.right = 10; targetText.style.bottom = 330;
            safeRoot.Add(targetText); safeRoot.Add(wheel); UpdateSafeArea();
        }
        private void UpdateSafeArea()
        {
            if (safeRoot == null || Screen.width == 0 || Screen.height == 0) return;
            var r = Screen.safeArea;
            // UI panel is kept in screen pixels; world camera profile never scales the HUD.
            safeRoot.style.left = r.xMin; safeRoot.style.right = Screen.width - r.xMax;
            safeRoot.style.top = Screen.height - r.yMax; safeRoot.style.bottom = r.yMin;
        }
        private static VisualElement Panel()
        {
            var p = new VisualElement(); p.style.position = Position.Absolute; p.style.backgroundColor = new Color(0.07f,0.10f,0.12f,0.90f);
            p.style.color = new Color(0.95f,0.91f,0.84f); p.style.paddingLeft = 8; p.style.paddingRight = 8; p.style.paddingTop = 8; p.style.paddingBottom = 8;
            return p;
        }
        private static Label Text(string key) { return new Label(P1Copy.Get(key)) { enableRichText = false }; }
        private static Button ActionButton(string key, Action action) { var b = new Button(action) { text = P1Copy.Get(key) }; b.style.minHeight = 48; return b; }
        private static void Circle(Button b, float x, float y, float size)
        {
            b.style.position = Position.Absolute; b.style.left = Mathf.Round(x - size/2); b.style.top = Mathf.Round(y - size/2);
            b.style.width = size; b.style.height = size; b.style.whiteSpace = WhiteSpace.Normal; b.style.fontSize = 12;
            b.style.borderTopLeftRadius = size/2; b.style.borderTopRightRadius = size/2; b.style.borderBottomLeftRadius = size/2; b.style.borderBottomRightRadius = size/2;
        }
        private void ToggleDetails(string mode)
        { details.style.display = details.style.display.value == DisplayStyle.Flex && detailMode == mode ? DisplayStyle.None : DisplayStyle.Flex; detailMode = mode; touchHeld = false; Render(); }
        private void Render()
        {
            if (closing || client == null || status == null) return;
            status.text = P1Copy.Get("connection." + client.State);
            bool ready = client.State == P1ConnectionState.Ready && !actionBusy;
            sync.SetEnabled(!actionBusy && client.SessionId != null);
            retry.SetEnabled(!actionBusy && client.HasPendingMutation); leave.SetEnabled(!actionBusy && !client.HasPendingMutation);
            var world = client.World;
            if (world != null)
            {
                vitals.text = P1Copy.Get("hud.vitals", world.self.hp, world.self.maxHp, world.self.mp, world.self.maxMp);
                location.text = P1Copy.Get("hud.position", world.self.x, world.self.y);
                selectedTarget = null;
                foreach (var e in world.entities) if (e.kind != "NPC" && e.state != "DEAD") { selectedTarget = e.entityId; break; }
                targetText.text = selectedTarget == null ? P1Copy.Get("target.none") : P1Copy.Get("target.selected");
            }
            else { vitals.text = P1Copy.Get("hud.unavailable"); location.text = ""; selectedTarget = null; targetText.text = P1Copy.Get("target.none"); }
            var text = new StringBuilder(); bool available = false;
            if (detailMode == "quests")
            {
                foreach (var q in client.Quests)
                {
                    text.AppendLine(q.questId == "P00-01" ? P1Copy.Get("quest.title") : q.questId);
                    text.AppendLine(P1Copy.Get("quest.state." + q.state));
                    foreach (var count in q.objectiveCounters) text.AppendLine(P1Copy.Get("quest.count", count.Value));
                    if (q.questId == "P00-01" && q.state == "AVAILABLE") available = true;
                }
                if (client.Quests.Length == 0) text.Append(P1Copy.Get("quest.empty"));
            }
            else if (client.Inventory == null) text.Append(P1Copy.Get("bag.unloaded"));
            else
            {
                foreach (var i in client.Inventory.items) text.AppendLine(i.templateId + " ×" + i.stack); // Template localization mapping arrives with content bundle.
                foreach (var c in client.Inventory.currencies) text.AppendLine((c.currencyId == "COIN" ? P1Copy.Get("bag.coin") : c.currencyId) + ": " + c.amount);
                if (client.Inventory.items.Length == 0) text.AppendLine(P1Copy.Get("bag.empty"));
            }
            detailText.text = text.ToString(); accept.style.display = detailMode == "quests" ? DisplayStyle.Flex : DisplayStyle.None; accept.SetEnabled(ready && available);
            for (int i = 0; i < 6; i++) skills[i].SetEnabled(ready && i < 3 && (i == 0 || selectedTarget != null));
            RenderCooldowns();
        }
        private void RenderCooldowns()
        {
            if (client == null || skills[0] == null) return;
            for (int i = 0; i < 3; i++)
            {
                string end; double seconds = 0;
                if (client.CooldownEndsAtUtc.TryGetValue("SK-MK-0" + (i+1), out end) && sampledServerTime != default(DateTimeOffset) &&
                    DateTimeOffset.TryParse(end, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var until))
                    seconds = (until - sampledServerTime).TotalSeconds - (Time.realtimeSinceStartup - sampledAt);
                skills[i].text = P1Copy.Get("skill." + (i+1)) + (seconds > 0 ? "\n" + Math.Ceiling(seconds) + "s" : "");
                bool ready = client.State == P1ConnectionState.Ready && !actionBusy && (i == 0 || selectedTarget != null);
                skills[i].SetEnabled(ready && seconds <= 0);
            }
        }
        private void Close()
        {
            if (closing) return;
            closing = true; if (life != null) life.Cancel();
            if (presenter != null) { presenter.Release(); Destroy(presenter); }
            if (proxy != null) Destroy(proxy); if (proxySprite != null) Destroy(proxySprite); if (proxyTexture != null) Destroy(proxyTexture);
            if (cameraTransform != null) cameraTransform.position = originalCameraPosition;
            document.rootVisualElement.Clear(); returnToTitle?.Invoke(); Destroy(this);
        }
        private void OnDestroy() { closing = true; if (life != null) { life.Cancel(); life.Dispose(); } if (presenter != null) Destroy(presenter); }
    }
}
