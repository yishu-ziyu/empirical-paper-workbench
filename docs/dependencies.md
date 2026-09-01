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
