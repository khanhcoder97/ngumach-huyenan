using NguMach.Client.Core.Guards;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class ReceiptReplayGuardTests
    {
        private static MutationReceipt Stored() => new MutationReceipt
        {
            Key = "key-1", PayloadHash = "hash-1", QuestState = "COMPLETED",
            CoinGranted = 20, ChestGranted = 1, Applied = true
        };

        [Fact]
        public void SameKeyAndPayload_ReplaysSuccess()
        {
            Assert.Equal(ReplayVerdict.ReplaySuccess,
                ReceiptReplayGuard.Evaluate(Stored(), "key-1", "hash-1"));
        }

        [Fact]
        public void DifferentKey_Conflicts()
        {
            Assert.Equal(ReplayVerdict.Conflict,
                ReceiptReplayGuard.Evaluate(Stored(), "key-2", "hash-1"));
        }

        [Fact]
        public void DifferentPayload_Conflicts()
        {
            Assert.Equal(ReplayVerdict.Conflict,
                ReceiptReplayGuard.Evaluate(Stored(), "key-1", "hash-2"));
        }

        [Fact]
        public void NotApplied_ReturnsNotApplied()
        {
            var r = Stored(); r.Applied = false;
            Assert.Equal(ReplayVerdict.NotApplied,
                ReceiptReplayGuard.Evaluate(r, "key-1", "hash-1"));
        }

        [Fact]
        public void NullStored_ReturnsNotApplied()
        {
            Assert.Equal(ReplayVerdict.NotApplied,
                ReceiptReplayGuard.Evaluate(null, "key-1", "hash-1"));
        }
    }
}
