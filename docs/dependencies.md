# Local dependency contract

`econpaper/` is the only product. Runtime source dependencies live in the
workspace's `dependencies/` directory, which can be overridden with
`ECONPAPER_DEPENDENCY_ROOT`.

## Retained dependency

| Name | Canonical upstream | Verified revision | Role |
|------|--------------------|-------------------|------|
| StatsPAI | <https://github.com/brycewang-stanford/StatsPAI.git> | `a98b6743cc797ddd9cc33de1772c3ea3e3f0c394` | Imported by estimation, identification, robustness, EDA, and cleaning paths |

The checkout passed `git fsck --no-dangling` before relocation. Install it
from the product root into each Python 3.12 environment that imports it:

```bash
python -m pip install -e ../dependencies/StatsPAI
```

The repository-local symbolic links are part of the upstream tree; no external
workspace path is embedded in them.

## Rejected runtime-dependency claims

- AERS revision `1c83d671dec19006aa7ce7605cb5a8980fc7b138` is not loaded by
  any product code. Identification and robustness use econpaper-owned Python
  implementations and StatsPAI.
- `stata-code` revision `bbca9fbe1b57bac3d86c307c8287ec712ce7b8e4`
  exposes a Stata execution bridge, not the translation API the product needs.
  The export path is implemented and tested inside `agent/nodes/translate_code.py`.

These repositories are historical references, not retained dependencies.

## Protected pilot image contract

`backend/Dockerfile` installs StatsPAI normally from the verified commit archive,
with the SHA256 enforced by pip's URL fragment. `pyfixest==0.60.0` and
`linearmodels==7.0` match the locally installed Card estimator dependencies.
The archive SHA256 is
`a5882d80b31b472de9e7d952c012193aada389cbb8090f6fd2886a6987f199d6`.
The build separately downloads the public Card CSV at that same commit, verifies
its bytes/column order/row count, and stores it at
`/opt/econpaper/card/data_card1995.csv`. `ECONPAPER_CARD_CSV` points there in the
image. Runtime needs no download, sibling checkout or editable installation.
The public data itself is not copied into this Git repository.

The exact manifest is `deploy/dependencies-card.json`: 3,010 rows, 34 substantive
columns plus the discarded `rownames` index; raw SHA256
`eda514228a77327ab9aa20df72b89256cdec579482fa9dbbe4e3d757748c9bf2`.
It selects `wooldridge_card_34`, including region controls, rather than the
9-column StatsPAI loader. Different extracts/specifications must not be compared
as numerical platform drift.

### Source and license decision

StatsPAI's pinned `LICENSE` is MIT; its replication script identifies the data as
the Wooldridge/Rdatasets Card extract. The [Card data documentation](https://vincentarelbundock.github.io/Rdatasets/doc/wooldridge/card.html)
credits David Card and lists 3,010 observations/34 variables. The
[wooldridge package metadata](https://raw.githubusercontent.com/cran/wooldridge/master/DESCRIPTION)
declares GPL-3 (checked 2026-09-08). Software MIT licensing does not relabel these
data. This pilot uses the public upstream extract inside the protected runtime,
retains provenance, and publishes neither a second CSV mirror nor the image.
Any later image/data redistribution requires retaining the upstream notices and
reviewing those distribution obligations before publication.

### Reproducible checks

```
# During image build; rejects changed upstream bytes before writing data:
python scripts/check_card_package.py --fetch --data-only
# In the built backend/runner image, without network or sibling mounts:
python scripts/check_card_package.py
```

The second command checks the installed distribution's source archive hash and
non-editable status, then computes actual region-control OLS (HC1) and IV
(default covariance), reporting newly calculated coefficients/standard errors.
It fails on invalid output rather than substituting reference constants. This
isolated estimator check does not establish application task completion, real
LLM generation, browser acceptance or permission isolation; those remain in the
private-pilot acceptance contract. Parent deployment instructions record source
SHA/image identity and clean build execution evidence. A backend requirements
pin does not by itself freeze all transitive dependencies or the Python base
image; retain the built image identifier and installed package inventory.

Root and frontend `.dockerignore` files exclude env files, key/certificate files,
local databases, developer dependencies and persisted research directories from
build contexts. Runtime secrets must be supplied outside Git and image layers.
