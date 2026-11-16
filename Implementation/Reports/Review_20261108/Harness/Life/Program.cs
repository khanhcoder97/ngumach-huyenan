using System;
using Server.Health.Gameplay.Combat;
var lives = new PlayerLifeLedger();
lives.RecordDamageCommit("CHR_REVIEW_ALIVE", 10, 0, 7, DateTimeOffset.UtcNow);
lives.RecordResurrectionCommit("CHR_REVIEW_ALIVE", 0, 5);
Console.WriteLine("before_churn=" + lives.LifeVersion("CHR_REVIEW_ALIVE"));
for (int i=0; i < PlayerLifeLedger.Capacity; i++) lives.RecordDamageCommit("CHR_OTHER_" + i, 10, 0, 1, DateTimeOffset.UtcNow);
Console.WriteLine("after_256_other_deaths=" + lives.LifeVersion("CHR_REVIEW_ALIVE"));
Console.WriteLine("old_death_retained=" + (lives.LatestDeath("CHR_REVIEW_ALIVE") != null));
