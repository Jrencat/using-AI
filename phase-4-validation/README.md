# phase-4-validation — C1 tools (Scope Conformance)

Python 3 stdlib only. Run with `python -I`. No tool imports `harness.py` or `chain_verifier.py`. Not a verification run: there is no Agent, fixture or live run here.
Normative text: `docs/architecture/phase-4/scope-conformance-contract.md`. Locked input: `c1-negative-corpus-v3.json` + `-record.json` (143 cases).

| Tool | Role | Input → output |
| --- | --- | --- |
| `manifest_tool.py` | Walk an observed root; write a BASELINE/POST manifest (§6). No symlink follow, no ignore list, refuses to overwrite | `--root --kind --run-id --out` [POST: `--bound-manifest --bound-events --session-id`] → manifest JSON |
| `scope_checker.py` | The Contract as code. Reads only its inputs; never the workspace | `--anchor-pre --baseline --post --package --anchor-post [--claims]` → one JSON verdict object (exit 0) |
| `build_corpus.py` | Realise the abstract corpus cases as files. Reads only the corpus (never expected verdicts, never the checker) | `--corpus --out` → `OUT/<case_id>/…` + `index.json` |
| `run_corpus.py` | Verify the corpus hash against its record, build, run the checker on every case, compare with the pre-registered expected verdict | → mismatches on stdout, `--results FILE`; exit 0 only if all match, 2 if the lock fails |
| `anchor_tool.py` | Human-run: write anchor A (`pre`) / Z (`post`) per Contract §8; hashes given files only, refuses to overwrite; see `fixture/README.md` | `pre`/`post` subcommands → anchor JSON |
| `test_anchor.py` | Local tests of `anchor_tool.py` (6 tests, fake package) | — |
| `test_tools.py` | Local unit tests of the tools (10 tests) | — |

`corpus-run-results-v3.json` is the deterministic output of one run of `run_corpus.py` (no timestamps or paths).

## Implementation decisions where the Contract is silent (not new rules)

1. **Skipped rules.** Contract §10 says a rule whose inputs are unavailable "because of … a precondition failure" is skipped. Implemented as: any SC-P failure skips SC-A1/A2; an SC-P6 failure (invalid declared Task set) also skips SC-K1–K4. Needed by N22 and N46 and consistent with N19/N20.
2. **SC-C1 under precondition failure.** `changed_paths` needs only Δ, so it is still evaluated (case X07); `in_scope` needs `V`, so it is skipped when authorization was skipped.
3. **Unreadable `claims` file** is treated as no claims (the Contract defines no consequence). No corpus case covers it.
4. **Δ is computed** whenever both manifests yield usable entries, even when SC-M1 already reports FAIL.
5. **SC-E5 field lists** are taken from the schemas in §6, §8 and Appendix A; `recorded_by` is handled by the "counts as absent" rule of §8.

## Known limits

- Symlink/reparse detection in `manifest_tool.py` is implemented but the unit test that creates a real symlink is skipped when the OS denies symlink creation (it was skipped in the recorded run); the checker's symlink rules are exercised on synthetic manifests only.
- Corpus cases are synthetic files from `build_corpus.py`; `manifest_tool.py` output is checked for well-formedness only, not end-to-end against a real Agent run.
- Contract, corpus, builder and checker share one author. Trust ceiling: `TOOL_GENERATED`; not Independent Verification.
