<div align="center">

# AXGF — Axiom Genealogy Format

**The open genealogy data standard for the modern era**

[![Version](https://img.shields.io/badge/version-1.0-667eea?style=flat-square)](https://gitlab.com/leonardkarin/axgf-spec)
[![License](https://img.shields.io/badge/license-CC0_1.0-43d9a2?style=flat-square)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Status](https://img.shields.io/badge/status-draft_for_review-ffd93d?style=flat-square)](https://gitlab.com/leonardkarin/axgf-spec/-/issues)
[![Format](https://img.shields.io/badge/format-JSON_%2B_ZIP-764ba2?style=flat-square)](https://gitlab.com/leonardkarin/axgf-spec/blob/main/schema/axgf-1.0.schema.json)

*GEDCOM was designed in 1984 for floppy disk exchange.*  
*AXGF is designed for 2026 — JSON-native, AI-readable, multilingual, document-embedding.*

[Specification →](./SPEC_1.0.md) · [JSON Schema →](./schema/axgf-1.0.schema.json) · [Examples →](./examples/) · [Discuss →](https://gitlab.com/leonardkarin/axgf-spec/-/issues)

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
├── schema/axgf-1.0.schema.json
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

```bash
pip install jsonschema
python tools/validate.py my-family.axgf
```

---

## Supported Calendar Systems

`gregorian` · `julian` · `hebrew` · `hijri` · `persian` · `chinese` · `ethiopian` · `japanese_era` · `republican_french` · `roman`

## Supported Name Component Types

`given_name` · `family_name` · `patronymic` · `matronymic` · `nasab` · `laqab` · `kunya` · `nisbah` · `nickname` · `alias` · `religious_name` · `pen_name`

## Event Categories

`birth` · `death` · `marriage` · `divorce` · `adoption` · `migration` · `naturalization` · `military` · `incarceration` · `name_change` · `census` · `legal` · `religious` · `social` · `historical` · `other`

---

## Roadmap

| Version | Target | Description |
|---|---|---|
| **1.0** | June 2026 | Initial public draft — core entities, i18n, confidence, documents |
| 1.1 | Q3 2026 | Community feedback integration, DNA sources refinement |
| 1.2 | Q4 2026 | Place authority file, Wikidata integration spec |
| 2.0 | 2027 | Binary format option, streaming support for large trees |

---

## Contributing

AXGF is an open standard. All contributions are welcome.

- 💬 **Discuss** — [GitLab Issues](https://gitlab.com/plkarin/axgf-spec/-/issues)
- 🐛 **Report a spec ambiguity** — open an issue with label `spec-clarification`
- 📝 **Propose a change** — open a Merge Request against `main`
- 🌍 **Internationalization gaps** — open an issue with label `i18n`

### Governance

AXGF 1.0 is authored by Karin Pierre-Léonard as part of the [ax-genealogy](https://gitlab.com/plkarin/ax-genealogy) project. Community governance model to be defined before version 2.0.

---

## Implementations

| Project | Language | Status |
|---|---|---|
| [ax-genealogy](https://gitlab.com/plkarin/ax-genealogy) | Rust + React | Reference implementation |
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

**AXGF — Ancestral Exchange and Genealogy Format**  
*Specification v1.0 · June 2026*  
*https://gitlab.com/plkarin/axgf-spec*

</div>
