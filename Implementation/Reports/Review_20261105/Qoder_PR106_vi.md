# Review Qoder PR106 — 05/11/2026

Pin cb4f4759ea5d3c3e59e7250f34ad387507e1e1d8. Isolated D:/Project/NGUMACHHUYENAN-review-qoder-latest-20261105. HOLD merge until measured lifecycle/escort issues fixed. Do not replace integration's dialoguev3 with older branch text.

1. Confirmed live-character loss: PlayerLifeLedger.cs:137 evicts after256othercharacters deaths, independent of active/reconnected actor lifetime. Reproducer before_churn=2 → after_256_other_deaths=1; old_death_retained=False. DeathReturn.cs:239 similarly bounds committed receipts, requiring audit of historical-key safety underapproveddecision. Keep lifeVersion/death identity with livecharacter; reclaim only through defined owner expiry/persistence, not arbitrary unrelated churn.
2. Actual fullalpha HTTP FAIL: P00-04waveA0/3deaths, attempts12. Server logged escortSTARTED, noCHECKPOINT_COMMITTED/WAVE_ACTIVATED. e2e_p1.py:1907 readiness checks state rather than authoritative healthState/targetable, so BLOCKED may be treated as alive. Exact movement/tick stall cause remains unproven; fix actual domain/runner and reproduce publicHTTP, not private helper grants.
3. AlphaEscortService.TryGetNpcPosition has no productioncaller: onlyself-checks. World/HTTP projection stillshowsstaticLyAn. Codex must not simulate NPCescortlocally. Publish owner-scopedposition fromdomain through audited readmodel/worldprojection, preserving canonical actor/life/map/floor/instanceIDs and isolation.
4. P00-05 ends afterboss+fragment: CLASS_CONFIRM objectiveTALK stillhasnoNPCtalkroute. C1/portal notfullplayable. Supply an additivecontract/routepacket andrealHTTPclassconfirmationguard (ownerquestACTIVE, boss+fragment committed, validNPC/range/map, exactlyonce), not client-sidecompletion.

Measured: ReleasebuildPASS4nullablewarnings; self-check556PASS0FAIL (Consolequeue modeWait avoids truncating output); contracts31schemas/31examplesPASS; privateactualdeathHTTP17checksPASS; fullalphaHTTPFAIL above. Ownedservers5196/5197 stopped. No nativeGodotfulltutorialacceptance. CooldownHTTPsecondlethalwithin3sec notmeasured, coveredinprocessonly.

Alpha defs are separate Examples/QuestDefinitionAlpha, canonicalBLOCKED unchanged; wireLOCKED. Runtime6exactALPHAIDs work, rescue projectsINTERACTABLE, wavehazard isnotaninteractiontarget. Profilesremainprivate/productionOFF. New7contentrows ≠30supportedHTTPskills: onlyMK01/02/03 wired; otherrowscatalog-only. Shops/guild/consumabletables arepolicyfoundation, notenabledbackendservices.

Evidence/reproduceroutsideproject: D:/Project/NGUMACHHUYENAN-tools/review-qoder-latest-20261105, including life-eviction.log, alpha-p00-http.log, alpha-server.log andrun-alpha-review.ps1. Read exactlogs before claimingrootcause.
