using UnityEngine;

namespace NguMach.Client.P1
{
    // One resource per cue. Loading this asset never references all 541 clips.
    public sealed class P1AudioCueAsset : ScriptableObject
    {
        public string cueKey;
        public AudioClip[] clips;
    }
}
