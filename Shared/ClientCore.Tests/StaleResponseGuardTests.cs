using System;
using NguMach.Client.Core.Guards;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class StaleResponseGuardTests
    {
        [Fact]
        public void ActiveSession_AcceptsMatchingResponse()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-1", 5);
            g.BeginRequest("req-1");
            Assert.True(g.IsApplicable("sess-1", "req-1", 5));
        }

        [Fact]
        public void OldSessionResponse_IsRejected()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-new", 2);
            Assert.False(g.IsApplicable("sess-old", "req-1", 1));
        }

        [Fact]
        public void OldRequestId_IsRejected()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-1", 1);
            g.BeginRequest("req-new");
            Assert.False(g.IsApplicable("sess-1", "req-old", 1));
        }

        [Fact]
        public void GenerationMismatch_IsRejected()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-1", 7);
            Assert.False(g.IsApplicable("sess-1", null, 6));
        }

        [Fact]
        public void NoActiveSession_RejectsEverything()
        {
            var g = new StaleResponseGuard();
            Assert.False(g.IsApplicable("sess-1", "req-1", 1));
        }

        [Fact]
        public void EndSession_ClearsActive()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-1", 1);
            g.EndSession();
            Assert.False(g.IsApplicable("sess-1", null, 1));
            Assert.Null(g.Active);
        }

        [Fact]
        public void NewerRevision_Wins()
        {
            Assert.True(StaleResponseGuard.IsNewerRevision(5, 3));
            Assert.False(StaleResponseGuard.IsNewerRevision(3, 5));
            Assert.False(StaleResponseGuard.IsNewerRevision(3, 3));
        }
    }
}
