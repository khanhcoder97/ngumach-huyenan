// CinemaOverlay — Fullscreen cinematic sequence overlay.
// Rules:
//   - Safe 16:9 / 20:9 presentation with black letterboxing.
//   - Skipping does not pause shared world and does not grant offline rewards.
//   - Clear harness disclaimer when video Muse media contract is pending.
// Owner: Antigravity Remote — Issue #85.

using System;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class CinemaOverlay : MonoBehaviour
    {
        private CinemaPresenter _presenter;
        private UIDocument _doc;

        private VisualElement _root;
        private Label _titleLabel;
        private Label _disclaimerLabel;
        private Label _subtitleLabel;
        private ProgressBar _progressBar;
        private Button _skipBtn;

        public CinemaPresenter Presenter => _presenter;

        public void Initialize(UIDocument doc = null)
        {
            _doc = doc ?? _doc;
            if (_presenter == null)
            {
                _presenter = new CinemaPresenter();
                _presenter.OnChanged += Render;
            }
            if (_root == null) BuildUI();
            else AttachToDocument();
        }

        private void BuildUI()
        {
            _root = new VisualElement();
            _root.style.position = Position.Absolute;
            _root.style.left = _root.style.right = _root.style.top = _root.style.bottom = 0;
            _root.style.backgroundColor = new Color(0.02f, 0.03f, 0.04f, 0.98f);
            _root.style.display = DisplayStyle.None;
            _root.style.justifyContent = Justify.SpaceBetween;
            _root.style.paddingLeft = _root.style.paddingRight = _root.style.paddingTop = _root.style.paddingBottom = 24;

            // Top bar
            var topBar = new VisualElement();
            topBar.style.flexDirection = FlexDirection.Row;
            topBar.style.justifyContent = Justify.SpaceBetween;

            var titleBox = new VisualElement();
            _titleLabel = new Label("PHÂN CẢNH ĐIỆN ẢNH");
            _titleLabel.style.fontSize = 18;
            _titleLabel.style.color = new Color(0.95f, 0.88f, 0.65f);
            _titleLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            titleBox.Add(_titleLabel);

            _disclaimerLabel = new Label("(Preview Harness — Video Muse runtime contract not yet integrated)");
            _disclaimerLabel.style.fontSize = 11;
            _disclaimerLabel.style.color = new Color(0.7f, 0.7f, 0.7f);
            titleBox.Add(_disclaimerLabel);
            topBar.Add(titleBox);

            _skipBtn = new Button(() => _presenter?.Skip()) { text = "Bỏ qua [Esc/Space]" };
            _skipBtn.style.minWidth = 120;
            _skipBtn.style.minHeight = 36;
            topBar.Add(_skipBtn);
            _root.Add(topBar);

            // Center area (cinematic placeholder)
            var centerBox = new VisualElement();
            centerBox.style.flexGrow = 1;
            centerBox.style.alignItems = Align.Center;
            centerBox.style.justifyContent = Justify.Center;

            var frameBox = new VisualElement();
            frameBox.style.width = 640;
            frameBox.style.height = 360;
            frameBox.style.backgroundColor = new Color(0.06f, 0.08f, 0.10f, 1f);
            frameBox.style.borderTopWidth = frameBox.style.borderBottomWidth = frameBox.style.borderLeftWidth = frameBox.style.borderRightWidth = 1;
            frameBox.style.borderTopColor = frameBox.style.borderBottomColor = frameBox.style.borderLeftColor = frameBox.style.borderRightColor = new Color(0.2f, 0.25f, 0.3f);
            frameBox.style.alignItems = Align.Center;
            frameBox.style.justifyContent = Justify.Center;

            var frameText = new Label("Muse Pixel-Art Cinematic Frame\nLogical: 640x360 (16:9) Safe Layer");
            frameText.style.color = new Color(0.4f, 0.5f, 0.6f);
            frameText.style.unityTextAlign = TextAnchor.MiddleCenter;
            frameBox.Add(frameText);
            centerBox.Add(frameBox);
            _root.Add(centerBox);

            // Bottom subtitle & progress area
            var bottomBox = new VisualElement();
            bottomBox.style.alignItems = Align.Center;
            bottomBox.style.marginBottom = 10;

            _subtitleLabel = new Label();
            _subtitleLabel.style.fontSize = 15;
            _subtitleLabel.style.color = Color.white;
            _subtitleLabel.style.unityFontStyleAndWeight = FontStyle.Bold;
            _subtitleLabel.style.backgroundColor = new Color(0f, 0f, 0f, 0.7f);
            _subtitleLabel.style.paddingLeft = _subtitleLabel.style.paddingRight = 16;
            _subtitleLabel.style.paddingTop = _subtitleLabel.style.paddingBottom = 6;
            _subtitleLabel.style.marginBottom = 12;
            _subtitleLabel.style.whiteSpace = WhiteSpace.Normal;
            _subtitleLabel.style.unityTextAlign = TextAnchor.MiddleCenter;
            bottomBox.Add(_subtitleLabel);

            _progressBar = new ProgressBar();
            _progressBar.style.width = 640;
            _progressBar.style.height = 8;
            bottomBox.Add(_progressBar);

            _root.Add(bottomBox);

            AttachToDocument();
        }

        private void AttachToDocument()
        {
            if (_doc == null || _root == null) return;
            if (_root.parent != _doc.rootVisualElement)
            {
                _root.RemoveFromHierarchy();
                _doc.rootVisualElement.Add(_root);
            }
        }

        public void PlayScene(string sceneId)
        {
            if (_presenter == null) return;
            _presenter.Play(sceneId);
        }

        private void Update()
        {
            if (_presenter == null || !_presenter.State.IsPlaying) return;

            _presenter.Update(Time.deltaTime);

            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.Space))
            {
                _presenter.Skip();
            }
        }

        private void Render()
        {
            if (_presenter == null || _root == null) return;

            var s = _presenter.State;
            if (s.IsPlaying || s.Phase == CinemaPlaybackPhase.Fallback)
            {
                _root.style.display = DisplayStyle.Flex;
                _titleLabel.text = s.Title ?? "PHÂN CẢNH ĐIỆN ẢNH";
                _disclaimerLabel.text = s.FallbackNote ?? "";
                _subtitleLabel.text = s.CurrentSubtitle ?? "";
                _progressBar.value = s.ProgressNormalized * 100f;
            }
            else
            {
                _root.style.display = DisplayStyle.None;
            }
        }

        private void OnDestroy()
        {
            if (_presenter != null)
            {
                _presenter.OnChanged -= Render;
                _presenter.Close();
            }
            if (_root != null && _root.parent != null)
            {
                _root.parent.Remove(_root);
            }
        }
    }
}
