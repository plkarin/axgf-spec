<div align="center">

# AXGF — Axiom Genealogy Format

**The open genealogy data standard for the modern era**

[![Version](https://img.shields.io/badge/version-1.0_%C2%B7_1.1_draft-667eea?style=flat-square)](https://github.com/plkarin/axgf-spec)
[![License](https://img.shields.io/badge/license-CC0_1.0-43d9a2?style=flat-square)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Status](https://img.shields.io/badge/status-draft_for_review-ffd93d?style=flat-square)](https://github.com/plkarin/axgf-spec/issues)
[![Format](https://img.shields.io/badge/format-JSON_%2B_ZIP-764ba2?style=flat-square)](https://github.com/plkarin/axgf-spec/blob/main/schema/axgf-1.0.schema.json)

*GEDCOM was designed in 1984 for floppy disk exchange.*  
*AXGF is designed for 2026 — JSON-native, AI-readable, multilingual, document-embedding.*

[Specification 1.0 →](./SPEC_1.0.md) · [1.1 draft: person profile →](./SPEC_1.1.md) · [JSON Schema 1.0](./schema/axgf-1.0.schema.json) · [1.1](./schema/axgf-1.1.schema.json) · [Examples →](./examples/) · [Discuss →](https://github.com/plkarin/axgf-spec/issues)

</div>

---

## Why AXGF?

GEDCOM 5.5.1 (1999) and even GEDCOM 7 (2021) were designed around a person-centric, ASCII-first, flat-text model that cannot express genealogical reality as researchers actually encounter it:

| Problem | GEDCOM | AXGF |
|---|---|---|
| Multilingual names (Japanese, Arabic, Hebrew...) | ❌ ASCII-biased | ✅ UTF-8, per-component transliteration |
| Partial dates with uncertainty | ⚠️ limited | ✅ precision + confidence + circa |
| Multiple calendar systems | ❌ Gregorian only | ✅ 10 calendar systems |
| Border-changing place names | ❌ | ✅ `country_history[]` |
| Confidence scoring per fact | ❌ | ✅ 0.0–1.0 on every claim |
| Source conflicts | ❌ | ✅ `conflicts[]` with resolution |
| DNA sources | ❌ | ✅ typed DNA source with shared_cm |
| Documents embedded in bundle | ❌ | ✅ binary files in ZIP bundle |
| Documents known but not obtained | ❌ | ✅ `status: known_missing` |
| AI hypotheses | ❌ | ✅ first-class with status tracking |
| Relationships as first-class entities | ❌ | ✅ Link entity with temporal validity |
| Family as independent entity | ❌ | ✅ Family owns its own documents |
| Occupations as career states | ❌ | ✅ Occupation entity (not event) |
| LLM-readable narrative pages | ❌ | ✅ optional Markdown vault |
| JSON Schema validation | ❌ | ✅ draft 2020-12 |
| Git-diffable | ❌ | ✅ one file per entity |
| Physical description, health, genome, beliefs, service | ⚠️ free text (`DSCR`, `RELI`, `EDUC`, `NATI`) | ✅ 1.1: 132 attributes in 14 groups, every one a dated, sourced claim |
| Values that change over a life | ❌ one value per tag | ✅ 1.1: series — two heights, two nationalities, both kept |
| Comparable descriptions | ❌ free text | ✅ 1.1: 102 closed vocabularies — ISCED, ICD-10 chapters, Fitzpatrick, ISOGG, CEFR… |
| Sensitive data governed by class | ❌ | ✅ 1.1: health · biometrics · genomics · legal, withheld and exported per class |
| Adoptive, foster and step lineage | ⚠️ `PEDI` | ✅ 1.1: `lineage` on each child of a family |
| Typed non-family relations | ⚠️ `ASSO`/`RELA` free text | ✅ 1.1: Link `relation` vocabulary |
| 3D models, voice corpora, trained models | ❌ | ✅ 1.1: artefacts held as Documents, with consent |

---

## Core Concepts

AXGF is built around **Philosophy C**: four independent first-class entities.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   PERSON    │     │    FAMILY    │     │    EVENT    │
│             │     │              │     │             │
│ atomic unit │────▶│ structural   │────▶│ dated fact  │
│ exists alone│     │ group        │     │ N participants│
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │
       └──────────── LINK (typed relation) ─────┘
                     label · confidence · dates
```

**PERSON** — exists independently. No family or event required.  
**FAMILY** — independent structural entity with its own documents and history.  
**EVENT** — independent dated fact with N participants and typed roles.  
**LINK** — first-class typed relationship with temporal validity and confidence.

Plus: **OCCUPATION** (career state), **SOURCE** (evidence), **PLACE** (reusable geography), **DOCUMENT** (embedded binary).

---

## Quick Start

### Minimal valid person

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "type": "person",
  "axgf_version": "1.0",
  "created_at": "2026-06-15T10:00:00Z",
  "updated_at": "2026-06-15T10:00:00Z",
  "version_num": 1,
  "identity": {
    "name": {
      "display": "Jean Pierre-Léonard",
      "components": [
        { "type": "given_name",  "value": "Jean",           "order": 1 },
        { "type": "family_name", "value": "Pierre-Léonard", "order": 2 }
      ]
    },
    "gender":     { "value": "M" },
    "is_living":  false,
    "visibility": "members"
  },
  "birth": {
    "date": {
      "value": "1923-04-12",
      "calendar": "gregorian",
      "precision": "exact",
      "confidence": 0.98
    }
  }
}
```

### Japanese name with furigana

```json
{
  "identity": {
    "name": {
      "display": "田中一郎",
      "display_latin": "Ichiro Tanaka",
      "culture": "ja",
      "direction": "ltr",
      "display_order": "family_first",
      "reading": "たなか いちろう",
      "reading_system": "hiragana",
      "components": [
        { "type": "family_name", "value": "田中", "value_latin": "Tanaka",
          "reading": "たなか", "order": 1 },
        { "type": "given_name",  "value": "一郎", "value_latin": "Ichiro",
          "reading": "いちろう", "order": 2 }
      ]
    }
  }
}
```

### Hebrew name with patronymic

```json
{
  "identity": {
    "name": {
      "display": "יוסף בן-דוד כהן",
      "display_latin": "Yosef ben-David Cohen",
      "culture": "he",
      "direction": "rtl",
      "components": [
        { "type": "given_name",  "value": "יוסף",   "value_latin": "Yosef",     "order": 1 },
        { "type": "patronymic", "value": "בן-דוד", "value_latin": "ben-David",  "order": 2 },
        { "type": "family_name","value": "כהן",    "value_latin": "Cohen",      "order": 3 }
      ]
    }
  }
}
```

### Date with multiple calendars

```json
{
  "date": {
    "value": "1923-04-12",
    "calendar": "gregorian",
    "precision": "exact",
    "confidence": 0.98,
    "alternatives": [
      { "value": "大正12年4月12日", "calendar": "japanese_era", "era": "Taisho", "era_year": 12 },
      { "value": "כ״ה ניסן תרפ״ג",  "calendar": "hebrew" }
    ]
  }
}
```

### Bundle structure

```
family.axgf  (ZIP)
├── manifest.json
├── schema/axgf-1.0.schema.json   (axgf-1.1.schema.json in a 1.1 bundle)
├── persons/{uuid}.json
├── families/{uuid}.json
├── events/{uuid}.json
├── links/{uuid}.json
├── occupations/{uuid}.json
├── sources/{uuid}.json
├── places/{uuid}.json
├── documents/
│   ├── index.json
│   └── files/{uuid}.pdf
└── vault/wiki/persons/{uuid}.md   (optional, AI narrative)
```

---

## Validate a bundle

The reference library ships an `axgf` binary that runs the JSON Schema *and*
the semantic checks (dangling references, cycles, chronology):

```bash
cargo install axgf-rs
axgf validate my-family.axgf
```

To check a single entity file against the schema alone, any JSON Schema
draft 2020-12 validator will do — see [`examples/`](./examples/) for a
ready-to-run snippet.

The [`tools/`](./tools/) directory holds the converters that produce a bundle
in the first place: `gedcom2axgf.py` (GEDCOM 5.5.1 files) and
`webtrees2axgf.py` (a live webtrees database, media bytes included).

---

## Supported Calendar Systems

`gregorian` · `julian` · `hebrew` · `hijri` · `persian` · `chinese` · `ethiopian` · `japanese_era` · `republican_french` · `roman`

## Supported Name Component Types

`given_name` · `family_name` · `patronymic` · `matronymic` · `nasab` · `laqab` · `kunya` · `nisbah` · `nickname` · `alias` · `religious_name` · `pen_name`

## Event Categories

`birth` · `death` · `marriage` · `divorce` · `adoption` · `migration` · `naturalization` · `military` · `incarceration` · `name_change` · `census` · `legal` · `religious` · `social` · `historical` · `other`

## Person Profile Groups (1.1 draft)

Identity and civil status · Morphology · Biometrics · Health · Genomics · Death · Residence and nationality · Education and work · Military and honours · Legal · Belief and affiliation · Personality and behaviour · Relationships · Digital legacy — see [SPEC_1.1.md](./SPEC_1.1.md) §5.

```json
"health": {
  "blood_group": { "value": "O", "source_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f", "confidence": 0.95 },
  "blood_pressure": [
    { "value": { "systolic": 145, "diastolic": 88 },
      "date": { "value": "2010-02-03", "precision": "exact" }, "confidence": 0.9 }
  ]
}
```

---

## Roadmap

| Version | Target | Description |
|---|---|---|
| **1.0** | June 2026 | Initial public draft — core entities, i18n, confidence, documents |
| 1.1 | Q3 2026 | **Draft:** extended person profile — claims, series, closed vocabularies, sensitive classes, lineage, typed relations, digital legacy |
| 1.2 | Q4 2026 | Place authority file, Wikidata integration spec |
| 2.0 | 2027 | Binary format option, streaming support for large trees |

---

## Contributing

AXGF is an open standard. All contributions are welcome.

- 💬 **Discuss** — [GitHub Issues](https://github.com/plkarin/axgf-spec/issues)
- 🐛 **Report a spec ambiguity** — open an issue with label `spec-clarification`
- 📝 **Propose a change** — open a Pull Request against `main`
- 🌍 **Internationalization gaps** — open an issue with label `i18n`

### Governance

AXGF 1.0 is authored by Karin Pierre-Léonard and maintained in this repository, which is the authority for the format. The specification comes first; the code follows it:

- **[axgf-spec](https://github.com/plkarin/axgf-spec)** (here) — the standard and its JSON Schema. Where an implementation and this document disagree, this document wins and the implementation is the bug.
- **[axgf-lib](https://github.com/plkarin/axgf-lib)** — implements the spec as the reference library.
- **[axgf-cms](https://github.com/plkarin/axgf-cms)** — consumes the library as a reference application.

Changes to the format are made here first and only then implemented downstream. Community governance model to be defined before version 2.0.

---

## Implementations

| Project | Language | Status |
|---|---|---|
| [axgf-lib](https://github.com/plkarin/axgf-lib) | Rust | Reference library — published on crates.io as [`axgf-rs`](https://crates.io/crates/axgf-rs) |
| [axgf-cms](https://github.com/plkarin/axgf-cms) | Rust | Reference web application |
| *Your project here* | — | Open a PR to list yours |

---

## Compatibility with GEDCOM

AXGF is not a replacement for GEDCOM in legacy systems. It is a superset designed for modern use cases. Reference implementations provide:

- **GEDCOM 5.5.1 → AXGF** import
- **GEDCOM 7.0 → AXGF** import  
- **AXGF → GEDCOM 7.0** export (lossy — confidence, hypotheses, and vault are not expressible in GEDCOM)

---

## License

The AXGF specification and JSON Schema are released under **Creative Commons CC0 1.0 Universal** — effectively public domain. No copyright. No patent claims. No royalties. Implement freely in any software, commercial or open source.

```
SPDX-License-Identifier: CC0-1.0
```

---

<div align="center">

**AXGF — Axiom Genealogy Format**  
*Specification v1.0 · June 2026*  
*https://github.com/plkarin/axgf-spec*

</div>
