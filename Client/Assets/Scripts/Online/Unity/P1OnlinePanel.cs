using System;
using System.Globalization;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    // Functional P1 HUD; final pixel skin/icons are still supplied by Muse.
    [DisallowMultipleComponent]
    public sealed class P1OnlinePanel : MonoBehaviour
    {
        private UIDocument document;
        private P1Client client;
        private P1AudioPlayer audioPlayer;
        private P1PlayerUIHook playerUIHook;
        private CancellationTokenSource life;
        private Action returnToTitle;
        private Label status, vitals, location, message, detailText, targetText, combatText;
        private VisualElement details, safeRoot, wheel, audioPanel;
        private Button accept, retry, sync, leave, attack, journalButton, bagButton, audioButton;
        private Button detailOpener;
        private Button interact, cycleTarget;
        private readonly P1GameplayInputGate inputGate = new P1GameplayInputGate();
        private readonly Button[] skills = new Button[6];
        private Vector2 touchMove, keyboardMove;
        private bool touchHeld, actionBusy, closing, applicationPaused;
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
        private string interactionTarget;
        private string detailMode = "quests";
        private float pollAt, listsAt;
        private EventCallback<GeometryChangedEvent> layoutChanged;

        public void Open(UIDocument ui, string serverOrigin, int timeoutSeconds, Action onClose, bool useWorldV2 = false)
        {
            document = ui; returnToTitle = onClose;
            life = new CancellationTokenSource();
            try
            {
                client = new P1Client(new P1UnityTransport(serverOrigin, timeoutSeconds), useWorldV2: useWorldV2);
                audioPlayer = gameObject.AddComponent<P1AudioPlayer>(); audioPlayer.Initialize();
                Build();
                playerUIHook = GetComponent<P1PlayerUIHook>();
                if (playerUIHook != null) playerUIHook.Initialize(new P1ClientAdapter(client), document);
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
                        RefreshInputSurface();
                        Vector2 movement = inputGate.AllowsGameplay ? (touchHeld ? touchMove : keyboardMove) : Vector2.zero;
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
                        if (client.UseWorldV2 && client.WorldV2 != null && !actionBusy && client.SessionId != null)
                            Show(await client.ReadEventsAsync(life.Token));
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
            RefreshInputSurface();
            if (!Application.isFocused || applicationPaused) { ClearHeldInput(); RenderCooldowns(); return; }
            if (Input.GetKeyDown(KeyCode.Escape) && ModalOpen)
            {
                if (playerUIHook != null && playerUIHook.IsAnyPanelOpen) playerUIHook.CloseTopPanel();
                else if (audioPanel.style.display.value == DisplayStyle.Flex) ToggleAudio();
                else ToggleDetails(detailMode);
                ClearHeldInput(); RenderCooldowns(); return;
            }
            keyboardMove = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical")).normalized;
            bool hotkeysReleased = !Input.GetKey(KeyCode.Alpha1) && !Input.GetKey(KeyCode.Alpha2) &&
                !Input.GetKey(KeyCode.Alpha3) && !Input.GetKey(KeyCode.F) && !Input.GetKey(KeyCode.E) &&
                !Input.GetKey(KeyCode.Space) && !Input.GetKey(KeyCode.Tab);
            // Intents were cleared on close/focus loss; physical held pointers still need release.
            bool pointersReleased = !touchHeld && Input.touchCount == 0 && !Input.GetMouseButton(0);
            inputGate.ObserveControls(keyboardMove.sqrMagnitude < 0.001f, hotkeysReleased, pointersReleased);
            if (presenter != null && !touchHeld && keyboardMove.sqrMagnitude < 0.001f) presenter.SetIdle();
            if (inputGate.AllowsGameplay)
            {
                if (Input.GetKeyDown(KeyCode.Alpha1)) Cast(0);
                if (Input.GetKeyDown(KeyCode.Alpha2)) Cast(1);
                if (Input.GetKeyDown(KeyCode.Alpha3)) Cast(2);
                if (Input.GetKeyDown(KeyCode.F)) AcceptQuest();
                if (Input.GetKeyDown(KeyCode.E)) Interact();
                if (Input.GetKeyDown(KeyCode.Space)) BasicAttack();
                if (Input.GetKeyDown(KeyCode.Tab)) CycleTarget();
            }
            RenderCooldowns();
        }
        private bool ModalOpen { get { return details != null && details.style.display.value == DisplayStyle.Flex ||
            audioPanel != null && audioPanel.style.display.value == DisplayStyle.Flex ||
            (playerUIHook != null && playerUIHook.IsAnyPanelOpen); } }
        private void ClearHeldInput() { keyboardMove = touchMove = Vector2.zero; touchHeld = false; }
        private void RefreshInputSurface()
        {
            var focused = document == null ? null : document.rootVisualElement.panel?.focusController?.focusedElement;
            bool editing = focused is TextField || focused is Slider || focused is SliderInt;
            inputGate.SetSurface(Application.isFocused, applicationPaused, ModalOpen, editing);
            if (!inputGate.AllowsGameplay) ClearHeldInput();
        }
        private void OnApplicationFocus(bool focused)
        { if (!focused) { inputGate.Reset(); ClearHeldInput(); } }
        private void OnApplicationPause(bool paused)
        { applicationPaused = paused; if (paused) { inputGate.Reset(); ClearHeldInput(); } }
        private async void RunAction(Func<Task<P1Result>> action)
        {
            if (actionBusy || closing) return;
            actionBusy = true; touchHeld = false; touchMove = keyboardMove = Vector2.zero; Render();
            try { Show(await action(), true); if (!closing) ApplyWorld(); }
            catch (OperationCanceledException) { }
            catch (Exception e) { Debug.LogException(e); if (!closing) message.text = P1Copy.Get("error.unexpected"); }
            finally { actionBusy = false; if (!closing) Render(); }
        }
        private void AcceptQuest()
        {
            if (client.State != P1ConnectionState.Ready) return;
            var q = Array.Find(client.Quests, item => item.questId == "P00-01");
            if (q == null) return;
            if (q.state == "AVAILABLE") RunAction(() => client.AcceptQuestAsync("P00-01", "NPC_LYAN", life.Token));
            else if (q.state == "READY_TO_TURN_IN") RunAction(() => client.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", life.Token));
        }
        private void Interact()
        {
            RefreshInputSurface();
            if (!inputGate.AllowsGameplay || interact == null || !interact.enabledSelf || interactionTarget == null) return;
            string id = interactionTarget; RunAction(() => client.InteractAsync(id, life.Token));
        }
        private void BasicAttack()
        {
            RefreshInputSurface();
            if (!inputGate.AllowsGameplay || attack == null || !attack.enabledSelf || selectedTarget == null) return;
            var aim = presenter == null ? Vector2.down : presenter.Facing;
            string target = selectedTarget; RunAction(() => client.BasicAttackAsync(target, aim.x, aim.y, life.Token));
        }
        private static bool Hostile(P1Entity entity)
        { return (entity.kind == "MOB" || entity.kind == "BOSS") && (entity.targetable.HasValue
            ? entity.targetable.Value && entity.healthState == "ALIVE"
            : entity.hp > 0 && entity.state != "DEAD"); }
        private void CycleTarget()
        {
            RefreshInputSurface(); if (!inputGate.AllowsGameplay || client.World == null) return;
            var targets = Array.FindAll(client.World.entities, Hostile);
            if (targets.Length == 0) { selectedTarget = null; return; }
            Array.Sort(targets, (a, b) => string.CompareOrdinal(a.entityId, b.entityId));
            int index = Array.FindIndex(targets, e => e.entityId == selectedTarget);
            selectedTarget = targets[(index + 1) % targets.Length].entityId; Render();
        }
        private void Cast(int slot)
        {
            RefreshInputSurface();
            if (!inputGate.AllowsGameplay || slot < 0 || slot >= 3 || !skills[slot].enabledSelf) return;
            var aim = presenter == null ? Vector2.down : presenter.Facing;
            string target = slot == 0 ? null : selectedTarget;
            audioPlayer.LocalUi("SFX/UI/confirm");
            RunAction(() => client.CastAsync("SK-MK-0" + (slot + 1), target, aim.x, aim.y, life.Token));
        }
        private void Show(P1Result result, bool userAction = false)
        {
            if (closing || message == null) return;
            audioPlayer.ObserveWorld(client.SessionId, client.World);
            foreach (var notice in client.DrainAudioNotices()) audioPlayer.ConfirmedNotice(notice);
            foreach (var e in client.DrainPresentationEvents())
                if (combatText != null) combatText.text = P1Copy.Get("combat." + e.type);
            if (!result.Success)
            {
                if (userAction) audioPlayer.LocalUi("SFX/UI/error");
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
            journalButton = ActionButton("ui.journal", () => { if (playerUIHook != null) playerUIHook.OpenPanel(PlayerPanel.QuestJournal); else ToggleDetails("quests"); }, null); toolbar.Add(journalButton);
            bagButton = ActionButton("ui.bag", () => { if (playerUIHook != null) playerUIHook.OpenPanel(PlayerPanel.Inventory); else ToggleDetails("inventory"); }, null); toolbar.Add(bagButton);
            audioButton = ActionButton("ui.audio", ToggleAudio, null); toolbar.Add(audioButton);
            sync = ActionButton("ui.sync", () => RunAction(async () => { var r = await client.ReadWorldAsync(life.Token); if (!r.Success) return r;
                r = await client.ReadQuestsAsync(life.Token); return r.Success ? await client.ReadInventoryAsync(life.Token) : r; })); toolbar.Add(sync);
            retry = ActionButton("ui.retry", () => RunAction(() => client.RetryPendingAsync(life.Token))); toolbar.Add(retry);
            leave = ActionButton("ui.leave", Close, null); toolbar.Add(leave); statusPanel.Add(toolbar);
            message = new Label(P1Copy.Get("ui.prototype")) { enableRichText = false }; message.style.whiteSpace = WhiteSpace.Normal; statusPanel.Add(message);
            details = Panel(); details.style.left = 10; details.style.top = 180; details.style.width = 300; details.style.display = DisplayStyle.None;
            var scroll = new ScrollView(); detailText = new Label { enableRichText = false }; detailText.style.whiteSpace = WhiteSpace.Normal; scroll.Add(detailText); details.Add(scroll);
            accept = ActionButton("quest.accept", AcceptQuest); details.Add(accept); safeRoot.Add(details);
            audioPanel = Panel(); audioPanel.style.left = 10; audioPanel.style.top = 180; audioPanel.style.width = 300; audioPanel.style.display = DisplayStyle.None;
            var audioScroll = new ScrollView();
            audioScroll.Add(Text(audioPlayer.Ready ? "audio.ready" : "audio.unavailable"));
            var mute = new Toggle(P1Copy.Get("audio.mute")); mute.SetValueWithoutNotify(audioPlayer.Settings.muted);
            mute.style.minHeight = 48; mute.RegisterValueChangedCallback(ev => audioPlayer.Settings.muted = ev.newValue); audioScroll.Add(mute);
            foreach (string bus in new[] { "Master", "Music", "Ambience", "SFX", "UI" })
            {
                string selectedBus = bus;
                var slider = new Slider(P1Copy.Get("audio.bus." + bus), 0, 100); slider.value = (float)(audioPlayer.Settings.GetGain(bus) * 100);
                slider.style.minHeight = 48; slider.RegisterValueChangedCallback(ev => audioPlayer.Settings.SetGain(selectedBus, ev.newValue / 100.0)); audioScroll.Add(slider);
            }
            audioScroll.Add(ActionButton("audio.close", ToggleAudio, null)); audioPanel.Add(audioScroll); safeRoot.Add(audioPanel);
            layoutChanged = evt => { details.style.maxHeight = audioPanel.style.maxHeight = Mathf.Max(60, evt.newRect.height - 200); UpdateSafeArea(); };
            root.RegisterCallback(layoutChanged);
            var movement = Panel(); movement.style.left = 10; movement.style.bottom = 10; movement.style.width = 168; movement.style.height = 168;
            var axes = new[] { new Vector2(-1,1), Vector2.up, new Vector2(1,1), Vector2.left, Vector2.zero, Vector2.right, new Vector2(-1,-1), Vector2.down, new Vector2(1,-1) };
            var names = new[] { "NW", "N", "NE", "W", "·", "E", "SW", "S", "SE" };
            for (int i = 0; i < 9; i++)
            {
                var direction = axes[i].normalized; var button = new Button { text = names[i] }; button.style.position = Position.Absolute;
                button.style.left = i % 3 * 54; button.style.top = i / 3 * 54; button.style.width = 54; button.style.height = 54;
                button.RegisterCallback<PointerDownEvent>(ev => { RefreshInputSurface();
                    if (!inputGate.AllowsGameplay || client.State != P1ConnectionState.Ready || actionBusy) { ev.StopPropagation(); return; }
                    touchMove = direction; touchHeld = true; button.CapturePointer(ev.pointerId); ev.StopPropagation(); });
                button.RegisterCallback<PointerUpEvent>(ev => { touchHeld = false; touchMove = Vector2.zero; button.ReleasePointer(ev.pointerId); ev.StopPropagation(); });
                button.RegisterCallback<PointerCaptureOutEvent>(ev => { touchHeld = false; touchMove = Vector2.zero; });
                movement.Add(button);
            }
            safeRoot.Add(movement);
            wheel = new VisualElement { pickingMode = PickingMode.Ignore }; wheel.style.position = Position.Absolute; wheel.style.right = 10; wheel.style.bottom = 10;
            wheel.style.width = 320; wheel.style.height = 320;
            // Same angles as DEC-019. Larger orbit maintains separate >=54px hit targets.
            attack = new Button(BasicAttack) { text = P1Copy.Get("skill.attack") }; Circle(attack, 230, 230, 92); attack.SetEnabled(false); attack.tooltip = P1Copy.Get("skill.basicMissing"); wheel.Add(attack);
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
            var context = Panel(); context.style.right = 10; context.style.bottom = 360; context.style.width = 220;
            cycleTarget = ActionButton("target.cycle", CycleTarget, null); context.Add(cycleTarget);
            interact = ActionButton("world.interact", Interact, null); context.Add(interact);
            combatText = new Label { enableRichText = false }; context.Add(combatText); safeRoot.Add(context);
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
        private Button ActionButton(string key, Action action, string cue = "SFX/UI/confirm")
        { var b = new Button(() => { if (cue != null) audioPlayer.LocalUi(cue); action(); }) { text = P1Copy.Get(key) }; b.style.minHeight = 48; return b; }
        private static void Circle(Button b, float x, float y, float size)
        {
            b.style.position = Position.Absolute; b.style.left = Mathf.Round(x - size/2); b.style.top = Mathf.Round(y - size/2);
            b.style.width = size; b.style.height = size; b.style.whiteSpace = WhiteSpace.Normal; b.style.fontSize = 12;
            b.style.borderTopLeftRadius = size/2; b.style.borderTopRightRadius = size/2; b.style.borderBottomLeftRadius = size/2; b.style.borderBottomRightRadius = size/2;
        }
        private void ToggleDetails(string mode)
        {
            bool open = !(details.style.display.value == DisplayStyle.Flex && detailMode == mode);
            detailOpener = mode == "quests" ? journalButton : bagButton;
            details.style.display = open ? DisplayStyle.Flex : DisplayStyle.None; audioPanel.style.display = DisplayStyle.None;
            audioPlayer.LocalUi(open ? "SFX/UI/panel_open" : "SFX/UI/panel_close"); audioPlayer.SaveSettings();
            detailMode = mode; inputGate.Reset(); ClearHeldInput(); RefreshInputSurface(); Render();
            if (open) { details.focusable = true; details.Focus(); } else detailOpener?.Focus();
        }
        private void ToggleAudio()
        {
            bool open = audioPanel.style.display.value != DisplayStyle.Flex;
            audioPanel.style.display = open ? DisplayStyle.Flex : DisplayStyle.None; details.style.display = DisplayStyle.None;
            audioPlayer.LocalUi(open ? "SFX/UI/panel_open" : "SFX/UI/panel_close"); audioPlayer.SaveSettings();
            inputGate.Reset(); ClearHeldInput(); RefreshInputSurface();
            if (open) { audioPanel.focusable = true; audioPanel.Focus(); } else audioButton?.Focus();
        }
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
                var target = Array.Find(world.entities, e => e.entityId == selectedTarget && Hostile(e));
                if (target == null) { target = Array.Find(world.entities, Hostile); selectedTarget = target?.entityId; }
                targetText.text = target == null ? P1Copy.Get("target.none") : P1Copy.Get("target.vitals", target.hp, target.maxHp);
                interactionTarget = null; double nearest = 25; // <=5WU interaction range, server revalidates.
                foreach (var e in world.entities)
                {
                    if ((e.kind != "INTERACTABLE" && e.kind != "GATHER_NODE") || e.availability != "AVAILABLE") continue;
                    double distance = (e.x - world.self.x) * (e.x - world.self.x) + (e.y - world.self.y) * (e.y - world.self.y);
                    if (distance <= nearest) { nearest = distance; interactionTarget = e.entityId; }
                }
            }
            else { vitals.text = P1Copy.Get("hud.unavailable"); location.text = ""; selectedTarget = null; interactionTarget = null; targetText.text = P1Copy.Get("target.none"); }
            var text = new StringBuilder(); bool available = false, turnIn = false;
            if (detailMode == "quests")
            {
                foreach (var q in client.Quests)
                {
                    text.AppendLine(q.questId == "P00-01" ? P1Copy.Get("quest.title") : P1Copy.Get("quest.unknown"));
                    text.AppendLine(P1Copy.Get("quest.state." + q.state));
                    foreach (var count in q.objectiveCounters) text.AppendLine(P1Copy.Get("quest.count", count.Value));
                    if (q.questId == "P00-01" && q.state == "AVAILABLE") available = true;
                    if (q.questId == "P00-01" && q.state == "READY_TO_TURN_IN") turnIn = true;
                }
                if (client.Quests.Length == 0) text.Append(P1Copy.Get("quest.empty"));
            }
            else if (client.Inventory == null) text.Append(P1Copy.Get("bag.unloaded"));
            else
            {
                foreach (var i in client.Inventory.items)
                {
                    string key = "item." + i.templateId; string name = P1Copy.Get(key);
                    text.AppendLine((name == key ? P1Copy.Get("bag.unknownItem") : name) + " ×" + i.stack);
                }
                foreach (var c in client.Inventory.currencies) text.AppendLine((c.currencyId == "COIN" ? P1Copy.Get("bag.coin") : P1Copy.Get("bag.otherCurrency")) + ": " + c.amount);
                if (client.Inventory.items.Length == 0) text.AppendLine(P1Copy.Get("bag.empty"));
            }
            if (client.LastTurnIn != null && !client.LastTurnIn.rewards.xp.applied) text.AppendLine(P1Copy.Get("quest.xpPending"));
            detailText.text = text.ToString(); accept.style.display = detailMode == "quests" ? DisplayStyle.Flex : DisplayStyle.None;
            accept.text = P1Copy.Get(turnIn ? "quest.turnIn" : "quest.accept"); accept.SetEnabled(ready && (available || turnIn));
            interact.SetEnabled(ready && inputGate.AllowsGameplay && client.UseWorldV2 && interactionTarget != null);
            cycleTarget.SetEnabled(inputGate.AllowsGameplay && client.UseWorldV2 && world != null);
            for (int i = 0; i < 6; i++) skills[i].SetEnabled(ready && inputGate.AllowsGameplay && i < 3 &&
                (!client.UseWorldV2 || i == 2) && (i == 0 || selectedTarget != null));
            RenderCooldowns();
        }
        private void RenderCooldowns()
        {
            if (client == null || skills[0] == null) return;
            bool basicReady = client.UseWorldV2 && client.State == P1ConnectionState.Ready && client.World != null && client.World.self.hp > 0 && !actionBusy && inputGate.AllowsGameplay && selectedTarget != null;
            string basicEnd;
            if (client.CooldownEndsAtUtc.TryGetValue("BASIC_ATTACK", out basicEnd) && sampledServerTime != default(DateTimeOffset) &&
                DateTimeOffset.TryParse(basicEnd, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var basicUntil))
                basicReady &= (basicUntil - sampledServerTime).TotalSeconds - (Time.realtimeSinceStartup - sampledAt) <= 0;
            attack.SetEnabled(basicReady); attack.tooltip = P1Copy.Get(client.UseWorldV2 ? "skill.attack" : "skill.basicMissing");
            for (int i = 0; i < 3; i++)
            {
                string end; double seconds = 0;
                if (client.CooldownEndsAtUtc.TryGetValue("SK-MK-0" + (i+1), out end) && sampledServerTime != default(DateTimeOffset) &&
                    DateTimeOffset.TryParse(end, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal, out var until))
                    seconds = (until - sampledServerTime).TotalSeconds - (Time.realtimeSinceStartup - sampledAt);
                skills[i].text = P1Copy.Get("skill." + (i+1)) + (seconds > 0 ? "\n" + Math.Ceiling(seconds) + "s" : "");
                bool ready = client.State == P1ConnectionState.Ready && client.World != null && client.World.self.hp > 0 && !actionBusy && inputGate.AllowsGameplay && (i == 0 || selectedTarget != null);
                bool mechanicsAvailable = !client.UseWorldV2 || i == 2; // Basic/MK03 are the reviewed tick subset; guard/dash mechanics follow.
                skills[i].tooltip = P1Copy.Get(mechanicsAvailable ? "skill." + (i+1) : "skill.mechanicPending");
                skills[i].SetEnabled(ready && mechanicsAvailable && seconds <= 0);
            }
        }
        private void Close()
        {
            if (closing) return;
            closing = true; if (playerUIHook != null) { playerUIHook.CloseAllPanels(); playerUIHook.Dispose(); } if (life != null) life.Cancel();
            if (audioPlayer != null) { audioPlayer.enabled = false; Destroy(audioPlayer); }
            if (presenter != null) { presenter.Release(); Destroy(presenter); }
            if (proxy != null) Destroy(proxy); if (proxySprite != null) Destroy(proxySprite); if (proxyTexture != null) Destroy(proxyTexture);
            if (cameraTransform != null) cameraTransform.position = originalCameraPosition;
            if (layoutChanged != null) { document.rootVisualElement.UnregisterCallback(layoutChanged); layoutChanged = null; }
            document.rootVisualElement.Clear(); returnToTitle?.Invoke(); Destroy(this);
        }
        private void OnDestroy()
        {
            closing = true;
            if (audioPlayer != null) { audioPlayer.enabled = false; Destroy(audioPlayer); }
            if (document != null && layoutChanged != null) document.rootVisualElement.UnregisterCallback(layoutChanged);
            if (life != null) { life.Cancel(); life.Dispose(); }
            if (presenter != null) Destroy(presenter);
            if (proxy != null) Destroy(proxy); if (proxySprite != null) Destroy(proxySprite); if (proxyTexture != null) Destroy(proxyTexture);
        }
    }
}
