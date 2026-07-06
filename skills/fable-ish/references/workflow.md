# fable-ish Workflow

## Mode Selection

- `quick`: simple explanation, direction check, low-risk review, or user asks for speed.
- `normal`: bounded code/docs/config changes, focused debugging, or ordinary implementation.
- `deep`: production, auth, database, migrations, deployment, broad refactor, generated artifacts, or high reliability work.
- `blocked`: destructive scope, secret exposure, irreversible remote action, missing credentials, or user decision required.

## Work Loop

For normal and deep tasks:

1. Inspect the relevant local context before editing.
2. Name the work unit as behavior, invariant, or artifact contract.
3. Choose an observable exit proof.
4. Implement the smallest coherent slice.
5. Run the narrowest relevant verification first.
6. Review likely failure scenarios.
7. Fix confirmed issues.
8. Stop only when proof passes or a concrete blocker remains.

## Review Lenses

Use these only when risk warrants:

- Changed invariant and caller/callee contract.
- Removed guards, defaults, or fallbacks.
- Empty, missing, zero, false, malformed, and legacy state.
- Concurrency, ordering, persistence, platform, and deployment differences.
- Security boundaries around auth, secrets, money, DB, and remote writes.

## Optional Subagents

Subagents are optional. Use them only for broad search, independent review, or separate modules where recall matters. Do not spawn them for small local edits.

## Continuation Discipline

Stopping early is a failure mode, not a safety feature. Field logs show premature
stops commonly fall into five buckets: over-cautious halts that never checked
existing safety nets, self-declared deferrals ("I'll finish tomorrow"),
approval gates that quietly became bottlenecks, treating a hung or dead
process as "still waiting", and stalling silently without telling anyone.

Before you stop, defer, or wrap up with work remaining, pass three questions:

1. **Is this a real technical blocker?** Check the safety nets that already
   exist (auto-compaction, backups, retries, rollback paths) before halting
   out of caution. Low remaining context is not a stop reason when the
   runtime compacts automatically.
2. **Whose call is it?** Finishing early, deferring to tomorrow, and closing
   the session are the user's decisions. Do not declare them on the user's
   behalf while unresolved goals remain. Default is to keep going.
3. **Have you said so?** If you are genuinely blocked, report the blocker
   explicitly instead of going quiet. A stall the user knows about is
   recoverable; a silent one is not.

When something stops responding, classify it before waiting on it:
**waiting** (legitimate, has a known anchor and expected duration),
**hung** (progress assumption broken — apply a time cap, then escalate), or
**dead** (process exited or is blocked on input — restart or hand to a human).
Each state has a different remedy; treating all three as "waiting" is how
multi-hour stalls happen.
