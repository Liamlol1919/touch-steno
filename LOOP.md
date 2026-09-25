/loop

# ORCHESTRATE THE TWO TOUCH-STENO AGENTS THROUGH GITHUB

You are the **input-system owner** in `~/Projekte/touch-steno`. A partner agent works in
`chordtouch-research` on a **different machine**. You cannot see their filesystem. GitHub is
the only channel. Treat every GitHub issue as the shared blackboard.

## Each cycle, in order. Never stop mid-cycle.

### 1. SYNC (never skip)
```bash
cd ~/Projekte/touch-steno && git fetch origin && git status --short && git log --oneline -3
gh issue list --state open --json number,title,comments --jq '.[]|"#\(.number) \(.title)"'
gh pr list --state all --json number,title,state --jq '.[]|"PR#\(.number) [\(.state)] \(.title)"'
```
Read every issue that gained comments since your last cycle. If the partner pushed commits you
do not have, `git pull --rebase` and resolve conflicts **by keeping both sides' content** —
never `git checkout --ours` on a design document.

### 2. PLAN
Re-read the actual files, never work from memory:
`AGENTIC_META_PLAN.md` · `BINDING_CONSTRAINT.md` · `DESIGN_DECISION_FINAL.md` ·
`VERTICAL_SLICE.md` · `INTEGRATION_TARGETS.md` · `ARCHIVE.md`
Turn every open item into a flat todo. Anything referenced as "most", "important", or "etc"
must be expanded into explicit items or it is not planned.

### 3. DISPATCH IN PARALLEL — one message, many agents
Group work by **disjoint file sets** and launch every independent group simultaneously.
Never dispatch a single agent when five could run. Subagents get no shared context, so each
brief must carry: absolute target paths (≤5, no globs), the exact contract or change, the
measured facts they may rely on, the acceptance criteria, and:
**"Do not run tests, linters, or formatters. Do not commit."** You run gates once, at the end.

### 4. VERIFY — you, not them
```bash
cd ~/Projekte/touch-steno && python3 -m unittest discover -s tests 2>&1 | tail -2
cd ~/Projekte/commindv2   && python3 -m pytest -q 2>&1 | tail -2
```
Plus a **smoke test of the actual changed path** — run the thing, not just the suite. A
concept is validated only when it produced a real number. On failure: dispatch a corrective
subagent naming the exact gap, then re-verify. **Never advance on red.**

### 5. COMMIT AND PUBLISH
One focused commit per green phase, phase-named. Then `git push`. If a push is rejected,
`git pull --rebase` — never force-push.

### 6. HAND OFF TO THE PARTNER
Post one GitHub comment stating, tersely: what you measured this cycle, what you changed, what
you killed, what you did **not** verify, and the single next question only they can answer.
The partner cannot see your commits unless you tell them what to look for.

### 7. THE THREE RULES THAT MATTER MOST
- **A number without a source is a rumour.** Every figure states n, operator, session, and
  whether it is measured, simulated, or assumed.
- **Retract in place.** When you find your own number was wrong, correct the file and say so in
  the same commit. Two agents have already been burned by silently replacing a number.
- **A concept is a specification until an acceptance test has produced a verdict.** Design
  score ≠ viability. 22 candidates were generated; 0 were validated. Do not write otherwise.

### 8. WHEN TO STOP A BRANCH, NOT THE LOOP
If a branch dies, write the kill into the record with its score and its fatal measurement, and
move on. Do not resurrect a killed branch with a new name. If the loop has completed a full
cycle with nothing unmeasured left to test, say so plainly and name the one physical
measurement only the user can perform.

Begin with step 1 now.
