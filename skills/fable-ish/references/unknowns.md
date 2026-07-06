# fable-ish Unknowns

Source: Thariq (@trq212), "A Field Guide to Fable: Finding Your Unknowns."

Verification proves the territory. This reference covers the other half:
clarifying the map before and during the work so the proof is aimed at the
right thing.

## Map and Territory

The map is what you give the agent: prompt, skills, context. The territory is
where the work lands: the codebase, the runtime, the real constraints. The gap
between them is the unknowns. Every unknown is a point where the agent must
guess intent. More work means more unknowns, and discovering them early is
cheaper than fixing them late.

Discover unknowns before, during, and after implementation, not only up front.
Planning does not remove unknowns hiding deep in implementation; an edge case
can point to solving the problem a different way altogether.

## Four Unknowns

- Known knowns: what is already in the prompt.
- Known unknowns: what you know you have not figured out yet.
- Unknown knowns: what is too obvious to write down but recognizable on sight.
- Unknown unknowns: what has not been considered at all.

Unfamiliar and deep work carries more unknown unknowns. That is where guessing
is most expensive, so that is where a discovery pass pays off most.

## Specificity Balance

- Too specific: the agent follows instructions even when a pivot fits better.
- Too vague: the agent fills gaps with generic best practices that may not fit.
- Give the starting point: experience with the problem and codebase, where the
  thinking currently stands, and what "good" would look like. Let the agent act
  as a thought partner, not only an executor.

## Techniques by Phase

Use techniques proportional to unknown-density, not by rote. Quick tasks rarely
need any. Unfamiliar or deep tasks warrant a pre-implementation pass. Prefer an
HTML artifact when a technique benefits from being visualized and reacted to.

### Before implementation

- Blind spot pass: entering an unfamiliar area, ask the agent to surface the
  unknown unknowns and teach them. State who you are and what you do not know.
- Brainstorm and prototype: for "know it when I see it" criteria, ask for
  several distinct directions (for example throwaway mockups with fake data) to
  react to before wiring anything real. Small spec changes can cause large code
  changes, so surface these early.
- Interview: ask the agent to interview you one question at a time, prioritizing
  questions whose answer would change the architecture.
- Reference: when it is hard to describe, point at it. Source code is the
  richest reference — a library, crate, or component whose semantics to
  reimplement, even across languages.
- Implementation plan: ask for a plan that leads with the decisions most likely
  to change (data models, type interfaces, user-facing flows) and buries
  mechanical refactoring.

### During implementation

- Implementation notes: keep a scratch `implementation-notes.md`. When an edge
  case forces a deviation from the plan, take the conservative option, log it
  under "Deviations," and keep going. Feed it into the next attempt.

### After implementation

- Pitch and explainer: package prototype, spec, and notes into one artifact for
  buy-in; lead with the demo. It accelerates review when others start with the
  same unknowns you did.
- Quiz: after a long session, have the agent quiz you on what actually changed
  and why, with context, before merging. Passing the quiz is the exit proof for
  "I understand this change."

## Relation to Verification

Unknown-discovery shapes the exit criterion; verification observes it. A blind
spot pass or brainstorm often reveals the real invariant to protect, which then
becomes the declared criterion in `references/workflow.md`. Do not skip the
proof because the map got clearer — clarify the map so the proof is aimed
correctly.
