# 4. R-sources — data route table (frozen)

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


**R-sources** is the named V1 route table. Classify from confirmed design facets (outcome / treatment / title-RQ topic). First matching row wins. Ambiguous → `else` (Dataverse).

| Family | When (illustrative facets) | Where / how (plan) | Fixture may appear | External path if fixture id absent |
|---|---|---|---|---|
| `educ_wage` | schooling / educ / wage / earnings / Mincer | **IPUMS** extract landing + **wage1** (Wooldridge wage1 teaching extract) | `schooling-wages` / wage1 if present in classic-5 / fixtures | IPUMS (CPS/USA or equivalent) + Dataverse backup |
| `minwage` | minimum wage / Card–Krueger / NJ–PA employment | **ck fixture** + **Card zip** (author-published NJ–PA zip) | `ck1994_long` / `ck1994` / `minimum-wage-employment` | Card zip URL + Dataverse |
| `growth` | cross-country growth / Barro / enrollment / investment | **WDI** (World Bank World Development Indicators) + **barro** | `barro1991_growth` | WDI + Dataverse |
| `macro` | FRED-style macro series / rates / aggregates without a growth-Barro object | **FRED** | none required | FRED + Dataverse backup |
| `else` | no row above | **Dataverse** search from facets | any classic-5 hit that `design_fit`s | Dataverse (required) |

Plan text must name **where** and **how** (e.g. “search Dataverse for confirmed outcome+treatment; also list ck fixture; Card zip at the author page”). A family label without a venue is not a plan.

**Card zip** is an external reproduction path for the Card–Krueger study data. It is **not** `/demos/card` (Card 1995 teaching case) and **not** `allow_did`.

**IPUMS** and **WDI** and **FRED** are external venues. FIND-DATA lists them as `url_or_fixture` candidates. It does not scrape behind login, does not store restricted extracts, and does not skip the user’s own confirm-attach.

---
