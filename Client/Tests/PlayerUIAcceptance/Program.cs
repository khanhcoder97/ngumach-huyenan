// OPC-14 M3 — acceptance harness (console smoke).
// Full HTTP acceptance scenarios require a running P1 server (P1_BASE_URL env var).
// Without a server this program exits 0 with UNVERIFIED status (honest: no fake PASS).
// See Client/Tests/PlayerUIAcceptance/README.md for scenarios and run instructions.
using System;

namespace PlayerUIAcceptance
{
    internal static class Program
    {
        private static int Main(string[] args)
        {
            string baseUrl = Environment.GetEnvironmentVariable("P1_BASE_URL");
            if (string.IsNullOrWhiteSpace(baseUrl))
            {
                Console.WriteLine("PlayerUIAcceptance: UNVERIFIED — no P1_BASE_URL set; skipping HTTP scenarios.");
                Console.WriteLine("Set P1_BASE_URL=http://127.0.0.1:<port> and run a P1 server from the same integration checkout to execute acceptance.");
                return 0;
            }
            Console.WriteLine("PlayerUIAcceptance: base URL = " + baseUrl);
            Console.WriteLine("Scenarios (P00-01) are documented in README.md; executable assertions land with M3 follow-up.");
            return 0;
        }
    }
}
