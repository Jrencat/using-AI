# Phase 1B Pilot Selection — v0.1 (Phase 1B-0)

> Status: DESIGNED / SELECTION ONLY. No Pilot execution has occurred. No business code has been touched. All facts below marked `REAL EVIDENCE` were directly observed via read-only tools (Read/Glob/Grep) during this phase; nothing is fabricated.

## 0. Search process (why this Pilot, not the brief's hypothetical sentence)

The brief flagged one *type* of issue to watch for ("修复实验页面刷新后左侧菜单与专题编号不匹配") but explicitly forbade forcing it. A real-evidence search was run before selecting anything:

- `docs/bug/项目bug.md` (real bug ledger, `vlims/Development/03 Code`) — read in full. All 6 entries are `✅ 已解决` (resolved); none concern menu/topic-refresh mismatch. **No open bug of the brief's hypothetical type currently exists in this ledger.**
- `Grep` for `刷新.{0,20}(不匹配|不一致|不同步|失效)` across the entire `03 Code` workspace — **zero matches**.
- Conclusion: the brief's hypothetical pattern was genuinely searched for and not found as a real open issue. Selecting it would have required fabricating a requirement, which is explicitly forbidden. The Pilot below was chosen instead, on its own evidentiary merits — it happens to sit in the *same domain area* (left-menu / `专题` state, `layout-sider.vue`, `activeProjectNo`) but is a distinct, real, already-documented task, not a stand-in for the hypothetical.

## 1. Pilot Source

- **Project**: `vilims-admin` (Vue 3 / Ant Design Vue frontend), part of the real, currently-active `vlims` LIMS workspace at `D:/code/vlims/Development/03 Code`.
- **Artifact**: `D:/code/vlims/Development/03 Code/HANDOFF.md` — a real session-handoff document (84 lines, read in full), describing a just-completed-but-unverified feature: global navigation buttons **"专题记录 / 记录模版"**.
- **Corroborating evidence gathered this phase**:
  - `Grep` for `左侧菜单|专题|刷新.*菜单|菜单.*不匹配|menu.*mismatch` across `03 Code` returned 30 real matching files including `layout-sider.vue`, `layout-quicklinks.vue`, `topic-record-modal.vue`, `router/experimentRoutes.ts` — confirms the domain area is real and structurally where HANDOFF.md says it is.
  - `Glob` on `vilims-admin/src/views/experiment/analysis-batch-worklist/components/*` returned 6 files (`MethodSnapshotEditDrawer.vue`, `MethodSnapshotTab.vue`, `PlateTab.vue`, `SequenceTab.vue`, `WorklistTab.vue`, `WorklistSampleIO.vue`) — **`TopicRecordModal.vue` (the orphan file HANDOFF.md says still needs manual deletion) is absent.** This is a real, evidence-based discrepancy between what HANDOFF.md claims is still pending and what the filesystem currently shows.
  - `git status`/`git log` on this workspace could **not** be run during this phase — the Bash safety classifier was rate-limited twice and did not recover in time. This is recorded as an open item, not glossed over: **it is not yet confirmed via version history whether the orphan file was actually deleted, or whether the Glob pattern coincidentally missed it.** This uncertainty is itself real evidence for why Repository Investigation needs an Escalation Trigger for "tooling temporarily unavailable" (see `phase-1b-scope.md` §Investigation Bound).
  - `Glob` on `openspec/changes/*` and `specs/*` at the workspace root: no active OpenSpec change exists for this feature; the most recent dated spec file is `20260821设备仪器导出v1.md`, which predates HANDOFF.md's still-open work — consistent with HANDOFF.md describing the most recent unmerged/unverified work in this project.

## 2. Pilot Structure

### A. User Intent (one real sentence)

A real user (the developer/operator of this project) would give a fresh agent session something equivalent to:

> "帮我确认 HANDOFF.md 里"专题记录 / 记录模版"这个功能的走查清单有没有做完，孤儿文件是不是已经删了，有没有别的遗留问题。"

This is not fabricated — it restates, in first-person intent form, exactly the real pending items HANDOFF.md's own "验证情况" and "待确认/后续" sections already document as unresolved.

### B. Expected Outcome

Concretely, by the end of the Pilot:

1. Each of HANDOFF.md's 6 manual browser-walkthrough checklist items (§"验证情况", lines 68-74) has a Pass/Fail/Cannot-verify result with cited Evidence.
2. The orphan-file question ("待手动清理" — `analysis-batch-worklist/components/TopicRecordModal.vue`) is resolved with real Evidence (git history or an authorized filesystem check), not left at the current `Glob`-only inference.
3. Any discrepancy between HANDOFF.md's claimed pending state and the actual current repo state is surfaced as a new `Question`, not silently resolved either way.
4. If, and only if, walkthrough uncovers a genuine defect, that becomes a new tagged `Question`/`Task` candidate for a human to authorize — the Pilot itself does not silently patch business logic (this mirrors the Legacy self-heal boundary preserved in `legacy-mapping.md` §2 item 5).
5. A final report is produced (human-readable, not code) stating PASS/FAIL/RISK_PENDING per item, each with an Evidence citation and trust tier.

### C. Investigation Surface (categories, not a presupposed file list)

Per the brief's instruction not to presuppose files in advance, the Pilot's actual execution should **independently re-derive** the surface below via bounded investigation — the file names listed here are what this phase's own investigation already surfaced (from HANDOFF.md + Grep/Glob) and serve as a **ground-truth check**: if Phase 1B's independent Requirement-Intelligence investigation converges on substantially the same surface without being handed HANDOFF.md verbatim, that is itself validating evidence for Requirement Intelligence (see `phase-1b-scope.md` §Investigation Bound and §7).

| Category | What to check | Already-known real evidence (for cross-check only) |
|---|---|---|
| Page entry | Where do the two buttons render, and under what condition? | `layout-quicklinks.vue` — `v-if="userStore.activeProjectNo"` |
| Routing | Where does "记录模版" navigate? | `router` entry for `TemplateSelect` |
| State source | What global state gates visibility / supplies the topic number? | `userStore.activeProjectNo` (Pinia store) |
| API / data source | What backend call populates the modal tree? | `getDynamicMenu({currentCode:'UN2026000481', projectNo})`, backend `UnitServiceImpl.setDynamicUnit` |
| Related components | What else was touched or extracted? | `menuNav.ts` (new), `topic-record-modal.vue` (new), `layout-sider.vue` (refactored import), `analysis-batch-worklist/index.vue` (rolled back) |
| Related tests | Any automated coverage? | None found — only `npx eslint --no-fix` was run (manual, prior session); no unit/e2e test currently exists for this feature |
| Project conventions | Does the new component follow existing patterns? | HANDOFF.md states naming/position "对齐 `change-password-modal.vue`"; `:visible=` (not `:open=`) per project's existing `a-modal` convention |
| Orphan / dead code | Is anything left over from the earlier (rejected) implementation? | `analysis-batch-worklist/components/TopicRecordModal.vue` — HANDOFF.md says still pending deletion; this phase's `Glob` found it **absent**, unconfirmed by git history |

### D. Risk Classification

**MODERATE**, with cited evidence, per `routing.md` §2:

- Not `SIMPLE`: the change is not confined to one file — it touches a **global, all-pages-rendered** layout component (`layout-quicklinks.vue`) and a shared store field (`userStore.activeProjectNo`), so a regression has broader blast radius than a single-page change.
- Not `COMPLEX`/`HIGH-RISK`: no schema change, no backend modification (HANDOFF.md explicitly: "未跑 `mvn compile`（无后端改动，纯前端功能）"), fully reversible (pure frontend, no data mutation, no money/permission/irreversibility per `protocol.md` §6 hard-override categories), and the riskiest design decision (menu-tree synchronization) was **already explicitly decided and reversed by the real user** during the prior session (HANDOFF.md §"已批准计划文件" item 6) — i.e., the Critical-severity business/UX decision is already closed, not open.
- One caveat worth flagging: the feature *did* go through two user-driven position/behavior corrections already (page-local → global; sync → no-sync) — a real signal of correctness-sensitivity in this exact domain area, even though the remaining Pilot work is verification, not design.

### E. Expected Routing

- **Protocol primitives used**: `Requirement` (intent = "verify and close out"), `Question` (for the orphan-file discrepancy and any walkthrough failures), `Evidence` (Glob/eslint/git outputs, eventual browser-walkthrough confirmation), `Evaluation` (per checklist item, per HANDOFF.md's "待确认" items), `Human Gate` (triggered at minimum for: (1) the orphan-file deletion itself — already real evidence exists this was blocked once by tooling policy, "Bash rm 被拒绝执行"; (2) any walkthrough item that fails; (3) the final non-test Claim sign-off, per Human Decision #4 in `human-decisions.md`).
- **Legacy stages skippable**: Stage 1 (QA generation) is effectively already done — HANDOFF.md **is** a closed requirement/QA record in substance, not something to redo from scratch; Stage 2 (Spec) likewise doesn't need a fresh document since this is verification of already-decided scope, not new feature design. Stage 3/4 (OpenSpec/Tasks) are unnecessary ceremony for a bounded verification pass. Stage 5 (implementation) is out of scope for this Pilot entirely — no code is meant to change except possibly the one already-blocked orphan-file deletion, gated by Human Gate. Stage 6 (testing) is exactly the 6-item walkthrough — kept, not skipped. Stage 7 (audit/archive) maps to the Pilot's final report.
- **Risk controls that must be preserved**: no silently "fixing" a failing walkthrough item by inventing business logic (Legacy self-heal boundary, `legacy-mapping.md` §2 item 5); no marking the orphan file deleted/not-deleted without real Evidence ≥ `RUNTIME_GENERATED` (a `Glob`-absence alone is `RUNTIME_GENERATED` but weak — corroborating `git log`/`git status` would raise confidence, not yet obtained); any actual file deletion requires Human Gate, matching the real precedent already set (`Bash rm` was previously refused).
- **Situations that must trigger a Human Gate**: any walkthrough item fails; the orphan-file question cannot be resolved by investigation alone; any newly discovered issue outside the documented scope (e.g. backend impact, despite HANDOFF.md's claim of none).

### F. Evidence Required to Claim Completion

| Claim | Minimum Evidence tier required | Status today |
|---|---|---|
| "Orphan file is gone" | `RUNTIME_GENERATED` (Glob) obtained ✅; `TOOL_GENERATED`/`INDEPENDENT_VERIFICATION` (git log confirming a deletion commit, or explicit human confirmation) still needed | Partially collected, not sufficient for `PASS` per `evidence.md` §2 rule as currently gathered (single Glob absence isn't corroborated) |
| "No new lint errors introduced" | `TOOL_GENERATED` (fresh `eslint --no-fix` run) | Prior run exists (per HANDOFF.md, from an earlier session) — **stale**, must be re-run fresh during the Pilot, not assumed still valid |
| "6-item walkthrough passes" | `HUMAN_VERIFICATION` (or `INDEPENDENT_VERIFICATION` if a scripted/automated browser check substitutes — undecided, see `human-decisions.md`) | Not collected — explicitly the main open item |
| "Requirement is correctly understood" (no misread of HANDOFF.md's scope) | `HUMAN_VERIFICATION` per Human Decision #4 (`human-decisions.md`) | Not yet confirmed by the human |

No claim above may be reported as `PASS` on `SELF_REPORT` evidence alone, per `protocol.md` §5.6 and `evidence.md` §2 (frozen, unchanged in this phase).
