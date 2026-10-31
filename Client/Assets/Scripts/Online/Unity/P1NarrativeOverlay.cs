using System;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UIElements;

namespace NguMach.Client.P1
{
    // Created on the HUD's injected document. Owns only its subtree; never searches/clears another UI.
    public sealed class P1NarrativeOverlay : IDisposable
    {
        private readonly P1Client client;
        private readonly P1NarrativeCatalog catalog;
        private readonly P1NarrativeFlow flow;
        private readonly VisualElement root, choices;
        private readonly Label title, body, status;
        private readonly Button next, previous, command, retry, skip;
        private CancellationToken token;
        private bool opening, dismissed, disposed, notice;
        public bool IsOpen { get { return opening || notice || flow.IsOpen; } }
        public P1NarrativeOverlay(P1Client source, UIDocument document)
        {
            client = source ?? throw new ArgumentNullException(nameof(source));
            if (document == null) throw new ArgumentNullException(nameof(document));
            var text = Resources.Load<TextAsset>("Narrative/dialogue_vi");
            if (text == null) throw new InvalidOperationException("Missing generated Narrative/dialogue_vi resource");
            catalog = new P1NarrativeCatalog(P1Wire.Decode<P1NarrativeBundle>(text.text));
            flow = new P1NarrativeFlow(client, catalog);
            root = new VisualElement { name = "gameplay-narrative" };
            root.style.position = Position.Absolute;
            root.style.left = new Length(8, LengthUnit.Percent); root.style.right = new Length(8, LengthUnit.Percent);
            root.style.top = new Length(12, LengthUnit.Percent); root.style.bottom = new Length(12, LengthUnit.Percent);
            root.style.backgroundColor = new Color(.055f, .075f, .08f, .98f);
            root.style.paddingLeft = root.style.paddingRight = 14;
            root.style.paddingTop = root.style.paddingBottom = 10;
            title = new Label(); title.style.fontSize = 20; title.style.color = new Color(.94f,.78f,.44f);
            root.Add(title);
            var scroll = new ScrollView(); scroll.style.flexGrow = 1; scroll.style.flexShrink = 1;
            body = new Label(); body.style.whiteSpace = WhiteSpace.Normal; body.style.fontSize = 18;
            body.style.color = new Color(.94f,.92f,.85f); scroll.Add(body); root.Add(scroll);
            choices = new VisualElement(); root.Add(choices);
            status = new Label(); status.style.whiteSpace = WhiteSpace.Normal; root.Add(status);
            var row = new VisualElement(); row.style.flexDirection = FlexDirection.Row; row.style.flexWrap = Wrap.Wrap;
            previous = Add(row, "Trước", () => flow.Previous());
            next = Add(row, "Đọc tiếp", () => flow.Next());
            skip = Add(row, "Tới phần giao việc", () => flow.SkipToAction());
            command = Add(row, "", () => _ = Submit(false));
            retry = Add(row, "Thử lại yêu cầu cũ", () => _ = Submit(true));
            Add(row, "Đóng · Esc", Close); root.Add(row);
            root.style.display = DisplayStyle.None; document.rootVisualElement.Add(root);
            flow.Changed += Render;
        }
        private static Button Add(VisualElement row, string text, Action action)
        { var b = new Button(action) { text = text }; b.style.minHeight = 38; b.style.marginRight = 5; row.Add(b); return b; }
        public bool CanHandle(string entityId) => !disposed && catalog.Npc(entityId, client.World?.mapId) != null;
        public async Task OpenAsync(string entityId, CancellationToken ct)
        {
            if (disposed || opening || flow.IsBusy) return;
            token = ct; opening = true; dismissed = false; notice = false; status.text = "";
            root.style.display = DisplayStyle.Flex; root.BringToFront();
            title.text = "Đang gặp nhân vật…"; body.text = "Đang đối chiếu tiến độ nhiệm vụ.";
            choices.Clear(); previous.SetEnabled(false); next.SetEnabled(false); skip.SetEnabled(false); command.SetEnabled(false); retry.SetEnabled(false);
            try
            {
                bool opened = await flow.OpenAsync(entityId, ct);
                if (!opened && !disposed && !dismissed && !ct.IsCancellationRequested)
                { notice = true; title.text = "Chưa thể trò chuyện"; body.text = "Hãy tới gần nhân vật. Nếu nhiệm vụ chưa mở hoặc dịch vụ chưa hỗ trợ, hội thoại sẽ không tự mở khóa nó."; }
            }
            catch (OperationCanceledException) { Close(); }
            catch (Exception error) { Debug.LogException(error); if (!disposed && !dismissed) { notice = true; status.text = "Không đọc được cuộc trao đổi. Hãy đồng bộ rồi thử lại."; } }
            finally { opening = false; if (!disposed) Render(); }
        }
        private async Task Submit(bool isRetry)
        {
            try { if (isRetry) await flow.RetryAsync(token); else await flow.SubmitAsync(token); }
            catch (OperationCanceledException) { if (!disposed) Render(); }
            catch (Exception error) { Debug.LogException(error); if (!disposed) status.text = "Yêu cầu chưa hoàn tất; hãy đồng bộ hoặc thử lại yêu cầu cũ."; }
        }
        public void Refresh() { if (!disposed) flow.RefreshValidity(); }
        private void Render()
        {
            if (disposed) return;
            if (!opening && !notice && !flow.IsOpen) { root.style.display = DisplayStyle.None; return; }
            if (flow.Entry == null) return;
            root.style.display = DisplayStyle.Flex;
            title.text = flow.Entry.title + " · " + flow.Npc.displayName;
            body.text = flow.ReplyText ?? flow.Page;
            status.text = flow.Error == null ? $"{flow.PageIndex + 1}/{flow.PageCount}" :
                "Yêu cầu chưa được xác nhận: " + P1Copy.Get("error." + flow.Error) +
                (string.IsNullOrEmpty(flow.CorrelationId) ? "" : " · " + flow.CorrelationId);
            choices.Clear();
            for (int i = 0; i < flow.Options.Count; i++)
            { int index = i; if (flow.Options.Count > 1) Add(choices, flow.Options[i].title, () => flow.Select(index)).SetEnabled(!flow.IsBusy); }
            if (!flow.IsCommitted && flow.Entry.replies != null)
                for (int i = 0; i < flow.Entry.replies.Length; i++)
                { int index = i; Add(choices, flow.Entry.replies[i].label, () => flow.Reply(index)).SetEnabled(!flow.IsBusy); }
            previous.SetEnabled(!flow.IsBusy && flow.PageIndex > 0); next.SetEnabled(!flow.IsBusy && flow.PageIndex + 1 < flow.PageCount);
            skip.SetEnabled(!flow.IsBusy && flow.PageIndex + 1 < flow.PageCount);
            command.text = flow.Entry.command == "ACCEPT" ? "Nhận việc" : "Giao nhận";
            command.style.display = flow.Entry.command == "NONE" || flow.IsCommitted ? DisplayStyle.None : DisplayStyle.Flex;
            command.SetEnabled(flow.CanCommand); retry.style.display = flow.CanRetry ? DisplayStyle.Flex : DisplayStyle.None; retry.SetEnabled(flow.CanRetry);
        }
        public void Close() { dismissed = true; notice = false; flow.Close(); root.style.display = DisplayStyle.None; }
        public void Dispose()
        { if (disposed) return; disposed = true; flow.Changed -= Render; flow.Dispose(); root.RemoveFromHierarchy(); }
    }
}
