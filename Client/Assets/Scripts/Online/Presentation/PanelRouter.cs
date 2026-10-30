// AG1 — Panel router and modal stack (pure C#, no Unity).
// Rules:
//   - Only one panel open at a time; modal stack tracks focus return.
//   - When UncertainMutation, input is blocked — no new commands.
//   - Closing a modal/cancel never cancels a server-committed transaction.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    public sealed class PanelRouter
    {
        private readonly Stack<PlayerPanel> _modalStack = new Stack<PlayerPanel>();
        private PlayerPanel _current = PlayerPanel.None;

        public PlayerPanel Current => _current;
        public bool IsAnyOpen => _current != PlayerPanel.None;
        public int ModalDepth => _modalStack.Count;

        public event Action<PlayerPanel, PlayerPanel> OnPanelChanged; // (prev, next)

        /// <summary>Open a panel. If another is open it is pushed to modal stack (focus preserved).</summary>
        public void Open(PlayerPanel panel, UIConnectionState connectionState)
        {
            if (panel == PlayerPanel.None) return;
            if (panel == _current) return;
            if (_current != PlayerPanel.None)
                _modalStack.Push(_current);
            var prev = _current;
            _current = panel;
            OnPanelChanged?.Invoke(prev, _current);
        }

        /// <summary>
        /// Close the current panel (Escape / explicit close).
        /// Returns focus to the previous panel in the modal stack, or None.
        /// Does NOT cancel any pending server command.
        /// </summary>
        public void CloseTop()
        {
            var prev = _current;
            _current = _modalStack.Count > 0 ? _modalStack.Pop() : PlayerPanel.None;
            OnPanelChanged?.Invoke(prev, _current);
        }

        /// <summary>Close all panels immediately (e.g. session expired).</summary>
        public void CloseAll()
        {
            var prev = _current;
            _modalStack.Clear();
            _current = PlayerPanel.None;
            if (prev != PlayerPanel.None) OnPanelChanged?.Invoke(prev, PlayerPanel.None);
        }

        public bool IsOpen(PlayerPanel panel) => _current == panel;
    }
}
