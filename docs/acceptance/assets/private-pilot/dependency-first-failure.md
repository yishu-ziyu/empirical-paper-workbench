# First clean dependency build failure

Observed 2026-09-08 in the isolated Docker ARM64 build; original local log:
`/tmp/econpaper-private-pilot-build.log` (retained, not overwritten).

The first build reached `pip install -r requirements.txt`, built StatsPAI
successfully, then failed compiling the `multimark._binding` C extension:

```
error: [Errno 2] No such file or directory: 'gcc'
ERROR: Failed building wheel for multimark
Successfully built StatsPAI
Failed to build multimark
```

This is an image build-tool omission in the pyfixest → maketables → multimark
dependency chain. It is not a Card execution or runner terminal-state failure
and does not diagnose issue #34.

Fix: install build-essential only in a Docker dependency build stage, install
Python dependencies into `/install`, and copy that installation into a fresh
runtime stage based on the same Python image. The runtime stage does not inherit
the compiler/toolchain layer. Also removed an undefined base `$PYTHONPATH`
reference reported by Docker; the intended application import paths are explicit.

No retry was run before changing the build prerequisite. The corrected clean
build, container compiler-absence check, installed package inventory and real
Card check remain separate subsequent evidence; this note does not claim they
passed.

## Second build: transport failure

Source cae4aeb; apt trixie-updates InRelease over HTTP returned 502. The signature error was a consequence of the failed fetch. Changed the official Debian source transport to HTTPS, preserving signature verification; no package bypass or automatic retry loop. Raw local log: `/tmp/econpaper-private-pilot-build-cae4aeb.log`. This infrastructure fetch failure is unrelated to Card issue #34.
