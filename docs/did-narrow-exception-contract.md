# DiD narrow-exception contract — catalog `allow_did` deprecated

Status: **superseded as source of truth**  
Superseded by: `docs/infer-design-contract.md` §7 (DECIDE-6, task `FM-E-BUILD-INFER-DESIGN-1`)  
Product line: **formal econpaper only**

DECIDE-5 A froze `allow_did` default false and allowed a title/catalog gate (Card–Krueger / minwage TITLE/TOPIC or catalog identity `minimum-wage-employment` / `ck1994` / `ck1994_long`) to set true. Form `method=did` was not the setter.

**DECIDE-6 withdraws catalog identity and catalog-token `allow_did` as the unlock.** DID-BE-gate must not treat those tokens as DiD permission. Catalog id alone cannot open DiD. OLS remains the default elsewhere.

Current gate (this recut): DiD is allowed only from **confirmed** `session.design.method=did` (or `norm_method` equivalent) **plus** treated×period presence on that design. TITLE/TOPIC propose stays INF-BE-propose; this gate only reads the confirmed object.

Missing treated×period on a confirmed DiD design is a hard-block **hook** (`confirmed_did_method` / `did_interaction_missing`). DID-BE-spec owns force + 409 from that hook. This file does not own the setter.

Do not revive `catalog_identity_allows`, `MINWAGE_ENTRY_IDS`, or `entry.allow_did` as the setter.
