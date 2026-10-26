# Proposal 0001 — What an absent `visibility` means, and what a converter stamps

**Status:** proposed for AXGF 1.2 · **Resolves:** [#1](https://github.com/plkarin/axgf-spec/issues/1)
· **Changes:** the meaning of a bundle that omits `visibility`; no bundle's
validity, no schema `required` list.

## The question

1.0 §9.1 says "all entities carry a `visibility` field", but the schema
requires it nowhere (`$defs/person/properties/identity`, `$defs/link`), and
nothing says what an absent value means. Three converters gave three
answers: `members` for everyone (`tools/gedcom2axgf.py`), and nothing at all
(`tools/webtrees2axgf.py`, axgf-rs). A reader that honours the field showed
a signed-out visitor either nothing or everything, depending only on the
tool that wrote the bundle.

## The principle

**An absent value is not a value.** The same rule as 1.0 §8.2 for
confidence ("parsers MUST assume `null` (unknown), not 0.0 or 1.0"), and as
the reference application's own ([axgf-cms ADR 0003](https://github.com/plkarin/axgf-cms/blob/main/docs/adr/0003-an-absent-value-has-no-default-position.md),
"an absent value has no default position"): a visibility in a bundle is a
decision somebody made about a record. A bundle that states none has
decided nothing, and must not be read as if it had, nor be made to say it
had by a tool that did not ask.

But a reader still has to show or hide the record. So the absence gets a
**reading rule**, the least a reader may protect, rather than a **default
value** written into the data.

## Proposed text (1.2, §9.1.1 and §9.1.2)

### 9.1.1 An absent visibility

`visibility` is OPTIONAL on a person's `identity` and on a Link. Its absence
means **no visibility was stated**. It is not a value:

- A writer MUST NOT add a `visibility` the author did not choose. In
  particular, an editor that saves an unrelated change to a record MUST NOT
  write one, and a converter MUST NOT invent one (§9.1.2).
- A reader MUST give a record whose visibility is absent an *effective*
  visibility at least as restrictive as:

  | Record | Effective visibility when absent |
  |---|---|
  | Person, `identity.is_living: true` | `members` |
  | Person, `identity.is_living: false` | `public` |
  | Link | the more restrictive of its two endpoints' effective visibilities |

  A reader MAY be more restrictive — a deployment may keep every record to
  signed-in members — and MUST NOT be less.

- **Living means the recorded flag**, as in 1.1 §4.3. An implementation
  that presumes a very old person dead MAY show them as such; that
  presumption MUST NOT make their record `public`. A converter that cannot
  tell whether someone died records them as living (no death, burial or
  cremation in the source), and the rule above then fails on the side of
  privacy: a nineteenth-century ancestor with no recorded death is kept to
  members until somebody records the death or chooses a visibility.

- The rule applies to what the record shows. 1.1 §4.3–4.4 still govern a
  sensitive class, which can only be more restrictive.

`visibility` does **not** become `required`: §10.3 forbids new required
fields in a minor version, and a required field would make every converter
choose a value the source does not hold — the defect this proposal removes.

### 9.1.2 What a converter stamps

- **When the source states nothing about privacy, the converter omits
  `visibility`.** GEDCOM, by default, states nothing; the reading rule of
  §9.1.1 then applies.
- **When the source states a restriction, the converter carries it.**
  GEDCOM 5.5.1 and 7 do have one, the restriction notice `RESN`:

  | `RESN` | AXGF |
  |---|---|
  | `privacy` (data withheld for privacy) | `"private"` |
  | `confidential` (marked confidential by the user) | `"private"` |
  | `locked` (an edit lock) | no visibility: a lock is not a visibility |

- **A converter MAY take an explicit choice** from the person running it
  (for example `--visibility members`) and stamp it on every record the
  source does not restrict itself. That is then the author's decision,
  made knowingly, and the bundle records it.

### 9.2, clarified: the manifest's privacy block

`manifest.privacy` makes **assertions about the bundle**:
`contains_living_persons` summarises the persons' `is_living`;
`living_persons_redacted` says whether an export removed or redacted them.
Neither is a default for, nor an override of, any record's visibility. A
reader MUST NOT derive a record's visibility from `manifest.privacy`.

### 9.1, corrected

"All entities carry a `visibility` field" becomes: "A person's `identity`
and a Link MAY carry a `visibility` field (§9.1.1 says what its absence
means). Other entities have none in 1.x; a reader SHOULD NOT show, through a
family, an event, an occupation, a document or a source, a person the
reader may not see."

## What this changes

- **No bundle becomes invalid**, and none changes meaning where it states a
  visibility. A bundle that omits it is read the same way by every reader,
  instead of by each reader's guess.
- **`tools/gedcom2axgf.py`** stops stamping `members` on everyone: it carries
  `RESN`, omits `visibility` otherwise, and takes `--visibility` for an
  explicit choice. It also reads a burial or a cremation as a death
  (`is_living: false`), as axgf-rs 0.6.1 does, so that the living flag the
  rule leans on is less often wrong.
- **axgf-rs** already omits `visibility`; once this is accepted its
  converter carries `RESN` by the table above (0.6.1 reports RESN as left
  out until then).
- **axgf-cms** already reads an absent person visibility by this rule
  (`src/access.rs`, `person_visibility`). It reads a link's absent
  visibility as `public` (`link_visibility`), so under this proposal it
  has to follow: a link whose endpoint the reader may not see is at least
  as restricted as that person. Today, for instance, the home page's count
  of relationships includes links to persons the visitor cannot open.

## Alternatives considered

- **`members` for everyone when absent.** Safe, and a public showcase of a
  family converted from GEDCOM would show nothing to anyone, as the issue
  saw on an 866-person bundle. Too strict to be the rule every reader must
  follow; a deployment may still choose it (it is "more restrictive").
- **`public` when absent.** Publishes every living person of a converted
  file. Rejected.
- **Make it required.** Rejected above: a minor version cannot, and it would
  force converters to invent.
- **Let the manifest set a default.** Two places saying one thing is one
  place too many, and the manifest's privacy block already means something
  else (§9.2).
