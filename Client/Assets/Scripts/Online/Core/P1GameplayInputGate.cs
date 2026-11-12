namespace NguMach.Client.P1
{
    // Presentation-only gate; server authorization and pending commands are unaffected.
    public sealed class P1GameplayInputGate
    {
        private bool blocked;
        private bool waitingForNeutral = true;

        public bool AllowsGameplay { get { return !blocked && !waitingForNeutral; } }

        public void SetSurface(bool focused, bool paused, bool modalOpen, bool editingControl)
        {
            blocked = !focused || paused || modalOpen || editingControl;
            if (blocked) waitingForNeutral = true;
        }

        public void ObserveControls(bool movementNeutral, bool gameplayKeysReleased, bool touchReleased)
        {
            if (!blocked && movementNeutral && gameplayKeysReleased && touchReleased)
                waitingForNeutral = false;
        }

        public void Reset() { waitingForNeutral = true; }
    }
}
