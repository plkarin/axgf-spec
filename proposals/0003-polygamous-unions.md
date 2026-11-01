# Proposal 0003 — Polygamous unions: one marriage per spouse

**Status:** proposed for AXGF 1.2 · **Changes:** defines the two fields the
1.0 example of a polygamous family already uses (`union.primary_person_id`,
`union.unions[]`), adds `children[].parent_ids`, and says how a reader
reads a polygamous union. No bundle stops being valid, and nothing is
removed.

## The question

1.0 §4.2.1 names `polygamous` among the union types, and §4.2.2 shows a
polygamous family:

```json
"union": {
  "type": "polygamous",
  "primary_person_id": "uuid-patriarch",
  "unions": [
    { "spouse_id": "uuid-wife-1", "start": { "date": { "value": "1890" } }, "end": null },
    { "spouse_id": "uuid-wife-2", "start": { "date": { "value": "1895" } }, "end": null }
  ]
}
```

The schema defines neither field. It requires `union.persons`, which the
example leaves out, so the example does not validate. The reference library
keeps both fields as extras, and readers do not know them. Nothing says
which wife is a child's mother.

A reader is then left with a union of three or more persons. The reference
application read every two of them as partners, and every child of the
family as a full brother or sister of every other, so that a co-wife became
a wife and a half-brother a brother. That is what the operator asked to have
told apart from a "full" union (axgf-cms ADR 0021).

## The principle

**A polygamous union is several marriages that share one person.** Each
marriage has its own dates, its own end and its own children. The spouses
are not married to one another. The format already says so in its example:
this proposal makes the example valid and the reading explicit.

## Proposed text (1.2)

### §4.2.2 Polygamous family

A union of type `polygamous` joins one person, its **primary person**, to
each of the others, who are not married to one another.

- **`union.persons`** lists everyone: the primary person and every spouse.
  The schema requires it, and a reader that knows only `persons` still
  finds everyone in the union.
- **`union.primary_person_id`** (OPTIONAL) names the primary person. It MUST
  be one of `persons`.
- **`union.unions[]`** (OPTIONAL) holds one entry per spouse: that spouse's
  own marriage to the primary person.

  | Field | Meaning |
  |---|---|
  | `spouse_id` | REQUIRED. One of `persons`, not the primary person. |
  | `start`, `end` | As `union.start` and `union.end`, for this marriage. |
  | `status` | As `union.status`, for this marriage. |
  | `confidence`, `source_id` | As the union's, for this marriage. |

  An entry's fields stand for that marriage in place of the union's own.
- **`children[].parent_ids`** (OPTIONAL, in any union) names the persons of
  the union who are this child's parents. In a polygamous union, they are the
  primary person and the child's other parent.

```json
{
  "id": "aaaa1234-e29b-41d4-a716-446655440010",
  "type": "family",
  "axgf_version": "1.2",
  "union": {
    "type": "polygamous",
    "primary_person_id": "11111111-1111-4111-8111-111111111111",
    "persons": [
      { "person_id": "11111111-1111-4111-8111-111111111111", "role": "husband" },
      { "person_id": "22222222-2222-4222-8222-222222222222", "role": "wife" },
      { "person_id": "33333333-3333-4333-8333-333333333333", "role": "wife" }
    ],
    "unions": [
      { "spouse_id": "22222222-2222-4222-8222-222222222222",
        "start": { "date": { "value": "1890", "precision": "year" } } },
      { "spouse_id": "33333333-3333-4333-8333-333333333333",
        "start": { "date": { "value": "1895", "precision": "year" } },
        "status": "ended_by_divorce" }
    ]
  },
  "children": [
    { "person_id": "44444444-4444-4444-8444-444444444444",
      "parent_ids": ["11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"] },
    { "person_id": "55555555-5555-4555-8555-555555555555",
      "parent_ids": ["11111111-1111-4111-8111-111111111111", "33333333-3333-4333-8333-333333333333"] }
  ]
}
```

### Reading a polygamous union

1. **The primary person is married to each spouse. The spouses are
   co-spouses, never partners**: co-wives, or co-husbands.
2. **Without `primary_person_id`**, a reader MAY take the member the record
   makes plain:
   - the only member `unions[]` does not name as a spouse;
   - else the only one whose recorded `role`, then whose sex, differs from
     all the others';
   - else the first listed, where the example and the converters put them.
3. **A child's parents** are the ones `parent_ids` names. In a polygamous
   union without `parent_ids`, they are the primary person and a spouse
   the record does not name. A reader SHOULD NOT say whether two such
   children are full or half siblings.
4. **One Family per marriage.** A household recorded as one Family per
   marriage, each typed `polygamous`, reads the same way: the partners of
   one person across those Families are co-spouses. This is how GEDCOM
   records it, one `FAM` per couple.
5. **Drawing.** A reader SHOULD draw each marriage of a polygamous union
   apart from a couple's, as one of several.

[KINSHIP.md](../KINSHIP.md) §1, §3 and §11 read these rules into kinship.

### Schema (1.2)

`$defs/family/properties/union/properties` gains:

```json
"primary_person_id": { "$ref": "#/$defs/uuid" },
"unions": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["spouse_id"],
    "properties": {
      "spouse_id": { "$ref": "#/$defs/uuid" },
      "start": { "$ref": "#/$defs/family/properties/union/properties/start" },
      "end": { "$ref": "#/$defs/family/properties/union/properties/end" },
      "status": { "$ref": "#/$defs/family/properties/union/properties/status" },
      "confidence": { "$ref": "#/$defs/confidence" },
      "source_id": { "$ref": "#/$defs/uuid" }
    }
  }
}
```

and each item of `$defs/family/properties/children` gains:

```json
"parent_ids": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/uuid" } }
```

## GEDCOM

GEDCOM has no tag for a polygamous union: it records one `FAM` per couple.
A converter keeps one Family per couple, and types them `polygamous` only
when its source says so.

## What this does not change

- **A couple.** A union of another type is read as it always was, a union
  of three included.
- **1.1 bundles.** They stay valid and are read as before. The fields above
  are extras to a 1.1 reader, which keeps them.
- **`lineage`.** It still says how a child belongs to the union; `parent_ids`
  says to whom.
