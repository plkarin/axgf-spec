# Proposal 0004 — Emblems: the picture that stands for a family

**Status:** proposed for AXGF 1.2 · **Changes:** adds `coat_of_arms` to the
document types (1.0 §5.5.2), names the role `emblem` for a family's
document, and adds `manifest.family.emblem`. No bundle stops being valid,
and nothing is removed.

## The question

Families keep pictures that stand for them, and none of them is a portrait:

- a coat of arms;
- a house mark;
- a Polish *herb*;
- a Japanese *kamon* (家紋);
- the crest a clan shares;
- the photograph a family puts at the head of its own archive.

AXGF can attach a document to a Family, in its `documents[]` (1.0 §4.2) or
in the document's `linked_to` (§5.5). Three things are missing:

- **Nothing says which of a family's pictures stands for the family.**
- **No document type fits.** A scan of a coat of arms is stored as `photo`
  or `other`.
- **The archive cannot have one.** The family the whole bundle is about,
  named in `manifest.family`, has no picture.

The reference application keeps the choice in its own extensions while it
waits (axgf-cms ADR 0022). Another reader sees a picture of the family, but
not what it is for.

## Proposed text (1.2)

### §5.5.2 Document types: `coat_of_arms`

> `coat_of_arms` — a coat of arms, a house mark, a family crest: a picture
> that stands for a family or a lineage.

### §4.2 Family: the role `emblem`

A Family's `documents[]` entry with `role: "emblem"`, or a Document whose
`linked_to` names the family with `role: "emblem"`, is the picture that
stands for that family. A family SHOULD have at most one. A reader that
finds several takes the first in the Family's `documents[]`, then in
document order.

### §3 Manifest: `family.emblem`

`manifest.family.emblem` (OPTIONAL) is the picture that stands for the
family the whole bundle is about:

```json
"family": {
  "name": "Famille Lefèvre-Morin",
  "emblem": { "document_id": "6f1c2a3b-9d4e-4f5a-8b6c-7d8e9fa0b1c2" }
}
```

The document MUST be in the bundle. A reader MAY show it wherever it shows
the family's name.

### Visibility (1.0 §9)

- **A family's emblem** is seen by whoever may see the family's people. A
  family none of whose people a reader may see keeps its emblem.
- **The manifest's emblem** is as public as the manifest's family name. A
  writer SHOULD NOT name, as the bundle's emblem, a document it would not
  show to every reader.

## Reading a 1.1 bundle

The reference application's extensions map onto these fields:

| axgf-cms (1.1) | 1.2 |
|---|---|
| `Family.extensions["axgf-cms:avatar/v1"].document_id` | that document linked with `role: "emblem"` |
| a Document `linked_to` the family with `role: "emblem"` | the same |
| `manifest.family.extensions["axgf-cms:emblem/v1"].document_id` | `manifest.family.emblem.document_id` |
| `"mode": "none"` | no emblem |

The extensions also keep a focal point (`focal`), which is a display choice
and stays the application's.

## What this does not change

- **Persons.** A person's picture is a separate matter, and the role
  `portrait` keeps its use.
- **1.1 bundles.** They stay valid and are read as before.
- **Documents.** An emblem is a Document like any other, with its sources,
  its confidence and its visibility.
