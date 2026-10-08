# using-AI Harness

Local capture/seal/verify aid and minimal state CLI. It is not a Protocol implementation or an Agent runtime. Python standard library only.

- Location: `harness/` (entry point `python harness/harness.py ...`, run from the repo root).
- Default run root: `harness/runs/RUN-<id>/` (gitignored; sealed packages contain raw Runtime transcript slices and are not committed). Override with `--root <directory>`, placed before the subcommand.
- Phase 2 run IDs use the `PH2-` prefix. Historical Phase 1D evidence lives outside this repo and is not touched.

## Operator sequence

1. Before the Agent starts, locate its live Claude Code session JSONL and record the exact session ID. Run `python harness/harness.py start --run-id <id> --probe-id <probe> --session-id <session> --source <session.jsonl>`. The source must end at a complete JSONL row.
2. Give the Agent only the relevant state commands. Its CLI calls are visible in the original Runtime transcript. The Agent must not receive write access to the operator's manifest or sealed package. The CLI accepts state submissions; acceptance does not establish that the Agent's investigation was correct.
3. Gate commands (`gate-observe`, `gate-status`, `gate-close`) are operator-side. `gate-observe --run-id <id> --question-id <id> --duration <seconds>` is started before the Agent's real `AskUserQuestion`; `gate-status --run-id <id> --gate-id <tool_use_id>` records a query through the current byte watermark; `gate-close --state cancelled|timeout --reason <reason>` is an operator cutoff, never a Human answer. A synchronous AskUserQuestion blocks the Agent turn; this tool does not make it asynchronous.
4. At the declared cutoff, the operator runs `seal --run-id <id>`. This snapshots the raw Runtime byte slice, hashes it and the append-only state log, and writes the manifest. `verify --run-id <id>` checks package integrity. `inspect-order --run-id <id>` compares Task CLI receipts with the first Runtime Edit.

The package contains `run.json` (RUN_START), `events.jsonl`, `runtime.jsonl` (original bytes within the run boundary), and `manifest.json` (RUN_END). A SHA-256 seal detects later changes but does not prove the operator or host was immutable. `capture_status=INCOMPLETE` forbids negative inferences from absent Runtime events; a clean capture is reported as `COMPLETE_WITHIN_BOUNDARY`. Agent `evidence.md` is never imported as trusted evidence.

Runtime rows without a `sessionId` are exempt only if they are known metadata types (`file-history-snapshot`, `file-history-delta`) carrying no tool blocks; any other row without a `sessionId` is a capture gap.

## State commands

`question-create --run-id <id> --id <PD-...> --requirement-ref <ref> --severity <Critical|Important|Non-Critical> --context <text>`

`question-transition --run-id <id> --id <PD-...> --state <ANSWERED|ASSUMED|BLOCKED|INVALID>`

`assumption-create --run-id <id> --id <ASSUM-...> --origin-question-id <PD-...> --content <text> --default-behavior <text> --impact <text> --confidence <text>`

`task-create --run-id <id> --id <task-id> --requirement-ref <ref> --priority <P0|P1|P2> --scope <paths...> [--assumption-dep <ASSUM-id>...]`

`task-routing --run-id <id> --id <task-id> --routing <SIMPLE|MODERATE|COMPLEX|HIGH-RISK> --reason <text>`

`task-transition --run-id <id> --id <task-id> --state <ELIGIBLE|BLOCKED>` requests a Task transition. ELIGIBLE is refused (exit 1, rejection recorded, Task becomes BLOCKED) if priority is P2 or any `assumption-dep` is ISOLATED. A new Assumption is ISOLATED on creation.

`query --run-id <id> question|assumption|task|gate <id>` returns current recorded state and full event history. This CLI does not decide Requirement readiness, allowed Scope, Human responses, investigation support, or Runtime capture completeness; those need independent confirmation.

## Tests

From `harness/`: `python test_harness.py -v` and `python test_chain_verifier.py -v`. `python chain_verifier.py <run-dir> [--claim ID=STATE]` is a read-only State Chain verifier that shares no code with `harness.py`. Tests use temporary, synthetic JSONL only.
