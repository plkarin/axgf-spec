# AXGF — Axiom Genealogy Format
## Specification Version 1.0
**Status**: Draft for Public Review  
**Date**: June 2026  
**Authors**: Karin Pierre-Léonard (ax-genealogy project)  
**License**: Creative Commons CC0 1.0 Universal (public domain)  
**Repository**: https://gitlab.com/leonardkarin/axgf-spec  
**MIME Type**: `application/vnd.axgf+zip`  
**File Extension**: `.axgf`

---

## Abstract

AXGF (Axiom Genealogy Format) is an open specification for the exchange, storage, and preservation of genealogical data. It is designed to overcome the fundamental limitations of GEDCOM — the prevailing genealogy interchange format created in the 1980s — by providing a modern, JSON-native, multilingual, AI-readable, and document-embedding format that models genealogical reality with precision and cultural sensitivity.

AXGF is structured around **Philosophy C**: four independent first-class entities (Person, Family, Event, Link) plus supporting structures (Occupation, Source, Place, Document), connected by typed relationships with confidence scores, temporal validity, and cultural context.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Bundle Structure](#2-bundle-structure)
3. [Manifest](#3-manifest)
4. [Core Entities](#4-core-entities)
   - 4.1 [Person](#41-person)
   - 4.2 [Family](#42-family)
   - 4.3 [Event](#43-event)
   - 4.4 [Link](#44-link)
   - 4.5 [Occupation](#45-occupation)
5. [Supporting Structures](#5-supporting-structures)
   - 5.1 [Name](#51-name)
   - 5.2 [Date](#52-date)
   - 5.3 [Place](#53-place)
   - 5.4 [Source](#54-source)
   - 5.5 [Document](#55-document)
6. [Internationalization](#6-internationalization)
7. [AI Integration](#7-ai-integration)
8. [Confidence Model](#8-confidence-model)
9. [Privacy Model](#9-privacy-model)
10. [Versioning](#10-versioning)
11. [Compatibility](#11-compatibility)
12. [Validation](#12-validation)
13. [Examples](#13-examples)
14. [Changelog](#14-changelog)

---

## 1. Design Principles

### 1.1 Core Philosophy

**P1 — Four independent first-class entities**  
Person, Family, Event, and Link are structurally independent. No entity owns another. A Family exists independently of its members. An Event exists independently of its participants. A Link exists independently of the entities it connects.

**P2 — Links are entities**  
Relationships between entities are themselves entities with their own identity, temporal validity, confidence score, and source. A relationship can be created, updated, questioned, and invalidated without deleting history.

**P3 — Confidence is mandatory**  
Every factual claim carries a confidence score between 0.0 and 1.0. A fact without a confidence score is incomplete. This enables AI systems to reason about uncertainty and humans to prioritize verification work.

**P4 — Bi-temporality**  
Every fact carries two time dimensions: *valid_time* (when the fact was true in the world) and *transaction_time* (when it was recorded in the dataset). These are distinct and both matter for genealogical integrity.

**P5 — Source-first**  
Every factual claim should reference at least one source. Unsourced claims are permitted but explicitly marked as such.

**P6 — Documents are first-class**  
Documents (photos, certificates, letters, audio, video) are first-class entities that can be embedded in the bundle as binary files and linked to any other entity.

**P7 — Universal multilingual support**  
UTF-8 is mandatory. Every name component carries a Latin transliteration. Dates support multiple calendar systems. Places carry country history for border changes.

**P8 — AI-native**  
The format is designed to be directly readable and writable by large language models. The optional vault section embeds Markdown narrative pages per entity for LLM consumption.

**P9 — Extensible without breaking**  
Unknown fields must be preserved and not cause parsing errors. Extensions use namespaced keys (`x-{vendor}-{field}`).

**P10 — Open and unencumbered**  
This specification is released under CC0. No royalties, no patent claims, no restrictions.

---

## 2. Bundle Structure

An AXGF bundle is a ZIP archive with the `.axgf` extension containing UTF-8 encoded JSON files and optionally binary document files.

```
family.axgf                    (ZIP archive)
├── manifest.json              REQUIRED
├── schema/
│   └── axgf-1.0.schema.json   REQUIRED — JSON Schema for validation
├── persons/
│   └── {uuid}.json            One file per person
├── families/
│   └── {uuid}.json            One file per family
├── events/
│   └── {uuid}.json            One file per event
├── links/
│   └── {uuid}.json            One file per link
├── occupations/
│   └── {uuid}.json            One file per occupation
├── sources/
│   └── {uuid}.json            One file per source
├── places/
│   └── {uuid}.json            One file per place
├── documents/
│   ├── index.json             Document metadata index
│   └── files/
│       └── {uuid}.{ext}       Binary document files
└── vault/                     OPTIONAL — AI narrative pages
    └── wiki/
        ├── persons/
        │   └── {uuid}.md
        ├── families/
        │   └── {uuid}.md
        └── events/
            └── {uuid}.md
```

### 2.1 Naming Rules

- All entity files are named `{uuid}.json` using lowercase UUID v4
- Binary files are named `{uuid}.{ext}` where ext is the actual file extension
- All paths are case-sensitive
- No directory nesting beyond what is specified above

### 2.2 Partial Bundles

A valid AXGF bundle MAY contain only a subset of entity types. A bundle with only `persons/` and no `families/` is valid. Parsers MUST handle missing directories gracefully.

### 2.3 Encoding

All JSON files MUST be encoded in UTF-8 without BOM. Line endings are LF (`\n`). JSON files MUST be valid per RFC 8259.

---

## 3. Manifest

The manifest is the entry point of every AXGF bundle. It MUST be present.

```json
{
  "axgf": "1.0",
  "created_at": "2026-06-15T10:00:00Z",
  "updated_at": "2026-06-15T14:30:00Z",
  "generator": {
    "name": "ax-genealogy",
    "version": "1.0.0",
    "url": "https://ax-genealogy.example.com"
  },
  "family": {
    "name": "Famille Pierre-Léonard",
    "description": "Lignée Pierre-Léonard — La Réunion → France métropolitaine",
    "primary_culture": "fr",
    "primary_place": "La Réunion, France",
    "time_span": {
      "earliest": "1850",
      "latest": "2026"
    }
  },
  "stats": {
    "persons": 142,
    "families": 38,
    "events": 289,
    "links": 67,
    "occupations": 54,
    "sources": 103,
    "places": 47,
    "documents": 215
  },
  "checksums": {
    "algorithm": "sha256",
    "manifest": "a3f8c2d1...",
    "persons_dir": "b7e9f1a3...",
    "documents_index": "c5d2a8f9..."
  },
  "privacy": {
    "contains_living_persons": true,
    "living_persons_redacted": false,
    "gdpr_compliant": true
  },
  "license": {
    "type": "private",
    "note": "Family use only. Not for redistribution."
  },
  "compatibility": {
    "gedcom_source": "5.5.1",
    "gedcom_export": "7.0"
  }
}
```

---

## 4. Core Entities

All core entities share these mandatory base fields:

```json
{
  "id": "uuid-v4",
  "type": "person | family | event | link | occupation",
  "axgf_version": "1.0",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601",
  "version_num": 1,
  "created_by": "string",
  "tags": ["string"]
}
```

---

### 4.1 Person

A Person is the atomic genealogical entity. It exists independently of any family or event. A person with no known information is valid (unknown ancestor placeholder).

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "type": "person",
  "axgf_version": "1.0",
  "created_at": "2026-05-01T10:00:00Z",
  "updated_at": "2026-06-10T14:00:00Z",
  "version_num": 3,
  "created_by": "admin@ax-genealogy.local",

  "identity": {
    "name": {
      "display": "Jean Pierre-Léonard",
      "display_latin": "Jean Pierre-Léonard",
      "culture": "fr",
      "direction": "ltr",
      "display_order": "given_first",
      "components": [
        {
          "type": "given_name",
          "value": "Jean",
          "value_latin": "Jean",
          "order": 1
        },
        {
          "type": "family_name",
          "value": "Pierre-Léonard",
          "value_latin": "Pierre-Leonard",
          "order": 2
        }
      ]
    },
    "names": [
      {
        "type": "birth",
        "display": "Jean-Baptiste Pierre-Léonard",
        "components": [
          { "type": "given_name",  "value": "Jean-Baptiste", "order": 1 },
          { "type": "family_name", "value": "Pierre-Léonard","order": 2 }
        ],
        "source_id": "src-001",
        "confidence": 0.95,
        "valid_from": "1923-04-12",
        "valid_until": "1950-01-01",
        "note": "Nom porté à la naissance, simplifié plus tard"
      }
    ],
    "gender": {
      "value": "M",
      "note": "Valeurs: M, F, NB (non-binary), U (unknown)"
    },
    "is_living": false,
    "visibility": "members"
  },

  "birth": {
    "date": {
      "value": "1923-04-12",
      "calendar": "gregorian",
      "precision": "exact",
      "circa": false,
      "confidence": 0.98
    },
    "place_id": "place-001",
    "confidence": 0.98,
    "source_id": "src-001",
    "event_id": "evt-birth-jean"
  },

  "death": {
    "date": {
      "value": "1987-03-03",
      "calendar": "gregorian",
      "precision": "exact",
      "circa": false,
      "confidence": 0.99
    },
    "place_id": "place-paris-14",
    "cause": null,
    "confidence": 0.99,
    "source_id": "src-002",
    "event_id": "evt-death-jean"
  },

  "bio": "Instituteur retraité, fondateur de l'école du village en 1948. Décoré de l'ordre du Mérite en 1972.",
  "notes": "Possible lien avec la famille Pierre de Saint-Pierre à investiguer.",

  "documents": [
    {
      "document_id": "doc-001",
      "role": "birth_certificate",
      "note": "Acte de naissance original"
    },
    {
      "document_id": "doc-002",
      "role": "photo",
      "date": "1955",
      "note": "Photo de mariage"
    }
  ],

  "ai": {
    "vault_page": "vault/wiki/persons/550e8400.md",
    "embedding_model": "nomic-embed-text",
    "embedding_updated_at": "2026-06-10T14:22:00Z",
    "hypotheses": [
      {
        "id": "hyp-001",
        "claim": "Possible frère de Pierre Pierre-Léonard (1920-?)",
        "confidence": 0.87,
        "status": "pending",
        "evidence": "Même patronyme, même commune de naissance, période compatible",
        "created_at": "2026-06-01T08:00:00Z",
        "reviewed_at": null,
        "reviewed_by": null
      }
    ]
  },

  "meta": {
    "version_num": 3,
    "versions": [
      {
        "version_num": 1,
        "changed_at": "2026-05-01T10:00:00Z",
        "changed_by": "admin@ax-genealogy.local",
        "note": "Import initial"
      },
      {
        "version_num": 2,
        "changed_at": "2026-05-15T14:00:00Z",
        "changed_by": "contributor@family.local",
        "note": "Ajout date de décès"
      }
    ]
  },

  "extensions": {
    "x-axgenealogy-dedup-score": 0.0,
    "x-axgenealogy-generation": 2
  }
}
```

#### 4.1.1 Person — Unknown Placeholder

A valid person with no known information:

```json
{
  "id": "unknown-father-jean",
  "type": "person",
  "axgf_version": "1.0",
  "identity": {
    "name": {
      "display": "[Père inconnu]",
      "components": []
    },
    "gender": { "value": "U" },
    "is_living": false,
    "visibility": "members"
  },
  "bio": null,
  "notes": "Père biologique de Jean Pierre-Léonard — identité inconnue",
  "ai": {
    "hypotheses": [
      {
        "id": "hyp-002",
        "claim": "Pourrait être Auguste Moreau d'après registre paroissial 1922",
        "confidence": 0.32,
        "status": "pending"
      }
    ]
  }
}
```

---

### 4.2 Family

A Family is a structural entity grouping persons in a recognized union with or without children. It exists independently of its members and can have its own documents, events, and history.

```json
{
  "id": "family-001",
  "type": "family",
  "axgf_version": "1.0",
  "created_at": "2026-05-01T10:00:00Z",

  "name": "Famille Pierre-Léonard — Branche Jean",
  "description": "Union de Jean Pierre-Léonard et Élise Bernard, Paris 1948",

  "union": {
    "type": "marriage",
    "status": "ended_by_death",
    "persons": [
      { "person_id": "uuid-jean",  "role": "spouse" },
      { "person_id": "uuid-elise", "role": "spouse" }
    ],
    "start": {
      "date": { "value": "1948-06-15", "calendar": "gregorian", "precision": "exact" },
      "place_id": "place-paris-14",
      "event_id": "evt-marriage-jean-elise"
    },
    "end": {
      "date": { "value": "1987-03-03", "calendar": "gregorian" },
      "reason": "death_of_spouse",
      "note": "Fin par décès de Jean"
    },
    "confidence": 0.99,
    "source_id": "src-003"
  },

  "children": [
    { "person_id": "uuid-robert",  "birth_order": 1, "confidence": 0.99 },
    { "person_id": "uuid-laurent", "birth_order": 2, "confidence": 0.99 },
    { "person_id": "uuid-karin",   "birth_order": 3, "confidence": 0.99 }
  ],

  "documents": [
    { "document_id": "doc-photo-famille-1955", "role": "family_photo" },
    { "document_id": "doc-acte-mariage",       "role": "marriage_certificate" }
  ],

  "notes": "Famille installée à Paris après la migration de 1943. Maison familiale au 12 rue des Fleurs, Paris 14e.",

  "ai": {
    "vault_page": "vault/wiki/families/family-001.md"
  }
}
```

#### 4.2.1 Union Types

| Type | Description |
|---|---|
| `marriage` | Union légalement reconnue |
| `civil_union` | PACS, civil partnership |
| `cohabitation` | Union libre documentée |
| `religious_only` | Mariage religieux sans enregistrement civil |
| `polygamous` | Union polygame (historique) |
| `unknown` | Type d'union inconnu |

#### 4.2.2 Polygamous Family

```json
{
  "id": "family-polygamous-001",
  "type": "family",
  "union": {
    "type": "polygamous",
    "primary_person_id": "uuid-patriarch",
    "unions": [
      {
        "spouse_id": "uuid-wife-1",
        "start": { "date": { "value": "1890" } },
        "end": null
      },
      {
        "spouse_id": "uuid-wife-2",
        "start": { "date": { "value": "1895" } },
        "end": null
      }
    ]
  },
  "children": []
}
```

---

### 4.3 Event

An Event is an independent dated fact that may involve any number of persons, families, or places with typed roles.

```json
{
  "id": "evt-marriage-jean-elise",
  "type": "event",
  "axgf_version": "1.0",
  "created_at": "2026-05-01T10:00:00Z",

  "category": "marriage",
  "subcategory": "civil",

  "date": {
    "value": "1948-06-15",
    "calendar": "gregorian",
    "precision": "exact",
    "circa": false,
    "confidence": 0.99
  },

  "place_id": "place-paris-14",

  "participants": [
    { "entity_type": "person", "entity_id": "uuid-jean",
      "role": "spouse_1", "confidence": 0.99 },
    { "entity_type": "person", "entity_id": "uuid-elise",
      "role": "spouse_2", "confidence": 0.99 },
    { "entity_type": "person", "entity_id": "uuid-andre",
      "role": "witness",  "confidence": 0.90 },
    { "entity_type": "family", "entity_id": "family-001",
      "role": "created",  "confidence": 0.99 }
  ],

  "description": "Mariage civil suivi d'une cérémonie religieuse à l'église Saint-Pierre le lendemain.",

  "documents": [
    { "document_id": "doc-acte-mariage", "role": "primary_source" }
  ],

  "confidence": 0.99,
  "source_id": "src-003",

  "ai": {
    "vault_page": "vault/wiki/events/evt-marriage-jean-elise.md"
  }
}
```

#### 4.3.1 Event Categories

| Category | Subcategories |
|---|---|
| `birth` | `registered`, `unregistered` |
| `death` | `natural`, `accident`, `conflict`, `execution`, `unknown` |
| `marriage` | `civil`, `religious`, `civil_and_religious`, `customary` |
| `divorce` | `legal`, `separation`, `annulment` |
| `adoption` | `legal`, `informal` |
| `migration` | `emigration`, `immigration`, `internal`, `forced` |
| `naturalization` | — |
| `military` | `enlistment`, `discharge`, `decoration`, `combat`, `prisoner` |
| `incarceration` | `prison`, `deportation`, `internment` |
| `name_change` | `legal`, `marriage`, `religious` |
| `census` | — |
| `legal` | `will`, `inheritance`, `contract`, `trial` |
| `religious` | `baptism`, `confirmation`, `bar_mitzvah`, `conversion` |
| `social` | `excommunication`, `banishment`, `honor` |
| `historical` | `war`, `epidemic`, `famine`, `disaster` |
| `other` | — |

---

### 4.4 Link

A Link is a typed, directed, first-class relationship between any two entities. It is independent of both entities and persists even if one entity is modified.

```json
{
  "id": "link-001",
  "type": "link",
  "axgf_version": "1.0",
  "created_at": "2026-05-10T08:00:00Z",

  "from": {
    "entity_type": "person",
    "entity_id": "uuid-jean"
  },
  "to": {
    "entity_type": "person",
    "entity_id": "uuid-jules"
  },

  "label": "parrain",
  "label_reverse": "filleul",
  "category": "spiritual",

  "bidirectional": false,

  "valid_from": {
    "date": { "value": "1950-03-15", "precision": "exact" },
    "event_id": "evt-baptism-jules"
  },
  "valid_until": null,

  "confidence": 0.85,
  "source_id": "src-005",
  "note": "Mentionné dans lettre familiale de 1952",

  "visibility": "members"
}
```

#### 4.4.1 Link Categories

| Category | Examples |
|---|---|
| `spiritual` | parrain, marraine, directeur spirituel |
| `professional` | employeur, apprenti, associé, mentor |
| `social` | ami, voisin, correspondant |
| `legal` | tuteur, mandataire, témoin |
| `medical` | médecin de famille, sage-femme |
| `educational` | instituteur, élève |
| `conflict` | rival, ennemi |
| `other` | label libre |

---

### 4.5 Occupation

An Occupation is a state (not a punctual event) attached to a person, describing their professional activity during a period.

```json
{
  "id": "occ-001",
  "type": "occupation",
  "axgf_version": "1.0",
  "created_at": "2026-05-01T10:00:00Z",

  "person_id": "uuid-jean",

  "title": "Instituteur",
  "title_latin": "Primary school teacher",
  "title_normalized": "teacher",

  "employer": {
    "name": "École publique de Saint-Denis",
    "place_id": "place-001"
  },

  "place_id": "place-001",

  "valid_from": {
    "date": { "value": "1948", "precision": "year" }
  },
  "valid_until": {
    "date": { "value": "1978", "precision": "year" }
  },

  "confidence": 0.90,
  "source_id": "src-006",
  "note": "Fondateur de l'école selon archives municipales"
}
```

---

## 5. Supporting Structures

### 5.1 Name

The Name structure is used wherever a named entity appears. It is designed to handle all world naming systems.

```json
{
  "display": "田中一郎",
  "display_latin": "Ichiro Tanaka",
  "culture": "ja",
  "direction": "ltr",
  "display_order": "family_first",
  "reading": "たなか いちろう",
  "reading_system": "hiragana",
  "components": [
    {
      "type": "family_name",
      "value": "田中",
      "value_latin": "Tanaka",
      "reading": "たなか",
      "order": 1
    },
    {
      "type": "given_name",
      "value": "一郎",
      "value_latin": "Ichiro",
      "reading": "いちろう",
      "order": 2
    }
  ]
}
```

#### 5.1.1 Name Component Types

| Type | Description | Example cultures |
|---|---|---|
| `given_name` | First name, personal name | Universal |
| `family_name` | Surname, last name | Universal |
| `patronymic` | Name derived from father | RU, IS, AR, GE |
| `matronymic` | Name derived from mother | IS, some ES |
| `nasab` | Genealogical chain in name | AR |
| `laqab` | Honorific epithet | AR, FA |
| `kunya` | Teknonymic name | AR |
| `nisbah` | Origin-based name | AR |
| `nickname` | Informal name | Universal |
| `alias` | Alternative name | Universal |
| `religious_name` | Name taken at conversion/ordination | Universal |
| `pen_name` | Pseudonym | Universal |

#### 5.1.2 Reading Systems

| Value | Description |
|---|---|
| `hiragana` | Japanese hiragana |
| `katakana` | Japanese katakana |
| `pinyin` | Chinese romanization |
| `jyutping` | Cantonese romanization |
| `ipa` | International Phonetic Alphabet |
| `revised_romanization` | Korean romanization |

---

### 5.2 Date

The Date structure supports partial dates, multiple calendar systems, and uncertainty.

```json
{
  "value": "1923-04-12",
  "calendar": "gregorian",
  "precision": "exact",
  "circa": false,
  "confidence": 0.98,
  "note": "Date from birth certificate",
  "alternatives": [
    {
      "value": "大正12年4月12日",
      "calendar": "japanese_era",
      "era": "Taisho",
      "era_year": 12
    },
    {
      "value": "כ״ה ניסן תרפ״ג",
      "calendar": "hebrew"
    }
  ],
  "range": null
}
```

#### 5.2.1 Date Precision Values

| Value | Meaning | Example |
|---|---|---|
| `exact` | Full date known | `1923-04-12` |
| `month` | Month and year known | `1923-04` |
| `year` | Year only | `1923` |
| `decade` | Approximate decade | `1920s` |
| `quarter_century` | ~25 year range | `early 1920s` |
| `century` | Century only | `19th century` |
| `unknown` | Date unknown | — |

#### 5.2.2 Calendar Systems

| Value | Description |
|---|---|
| `gregorian` | Standard international (default) |
| `julian` | Julian calendar (pre-reform) |
| `hebrew` | Jewish calendar (Anno Mundi) |
| `hijri` | Islamic lunar calendar |
| `persian` | Solar Hijri calendar |
| `chinese` | Traditional Chinese lunisolar |
| `ethiopian` | Ethiopian calendar |
| `japanese_era` | Japanese imperial era system |
| `republican_french` | French Revolutionary calendar |
| `roman` | Roman AUC calendar |

#### 5.2.3 Date Range

For events with uncertain date ranges:

```json
{
  "range": {
    "earliest": { "value": "1920", "precision": "year" },
    "latest":   { "value": "1925", "precision": "year" },
    "note": "Birth between 1920 and 1925 based on census records"
  }
}
```

---

### 5.3 Place

A Place is a reusable geographic entity with multilingual names and country history for border changes.

```json
{
  "id": "place-001",
  "type": "place",
  "axgf_version": "1.0",

  "names": [
    { "lang": "fr", "value": "Saint-Denis",          "is_primary": true },
    { "lang": "cr", "value": "Saint-Denis",          "is_primary": false },
    { "lang": "en", "value": "Saint-Denis, Réunion", "is_primary": false }
  ],

  "type": "city",
  "region": "La Réunion",
  "country_current": "FR",

  "coordinates": {
    "lat": -20.8823,
    "lon": 55.4504,
    "precision": "city_center"
  },

  "country_history": [
    { "country": "FR", "from": null, "until": null,
      "note": "French territory since 1638" }
  ],

  "identifiers": {
    "wikidata": "Q47045",
    "geonames": "935264",
    "insee": "97411"
  },

  "note": "Capital of Réunion island"
}
```

#### 5.3.1 Place Types

`continent`, `country`, `region`, `department`, `city`, `village`, `district`, `street`, `building`, `farm`, `island`, `historical`, `unknown`

---

### 5.4 Source

A Source is an evidence record that justifies factual claims. Every fact should reference at least one source.

```json
{
  "id": "src-001",
  "type": "source",
  "axgf_version": "1.0",
  "created_at": "2026-05-01T10:00:00Z",

  "title": "Acte de naissance n°47 — Jean Pierre-Léonard",
  "source_type": "birth_certificate",
  "reliability": "primary",
  "confidence": 0.98,
  "status": "verified",

  "repository": {
    "name": "Archives départementales de La Réunion",
    "location": "Saint-Denis, La Réunion",
    "url": "https://archives.reunion.fr",
    "reference": "5MI/47/1923/0047"
  },

  "date": { "value": "1923-04-12", "precision": "exact" },
  "place_id": "place-001",

  "document_id": "doc-001",

  "conflicts": [
    {
      "source_id": "src-009",
      "field": "birthdate",
      "this_value": "1923-04-12",
      "conflict_value": "1923-04-15",
      "resolution": "this_preferred",
      "resolution_note": "Original civil register preferred over family Bible"
    }
  ],

  "transcription": "Le douze avril mil neuf cent vingt-trois...",
  "language": "fr",
  "script": "latin",

  "note": "Original document held at departmental archives. Microfilm copy also available."
}
```

#### 5.4.1 Source Types

`birth_certificate`, `death_certificate`, `marriage_certificate`, `census`, `baptism_record`, `burial_record`, `will`, `land_record`, `military_record`, `immigration_record`, `naturalization`, `passport`, `photograph`, `letter`, `diary`, `newspaper`, `oral_tradition`, `dna`, `family_bible`, `gravestone`, `published_genealogy`, `other`

#### 5.4.2 Reliability Levels

| Value | Description |
|---|---|
| `primary` | Created at the time of the event by a participant |
| `secondary` | Created after the event or by a non-participant |
| `derivative` | Transcription, index, or abstract of a primary source |
| `authored` | Published work citing other sources |
| `oral` | Oral tradition or interview |
| `unknown` | Reliability not assessed |

#### 5.4.3 DNA Source

```json
{
  "id": "src-dna-001",
  "source_type": "dna",
  "dna": {
    "test_provider": "23andMe",
    "test_type": "autosomal",
    "test_date": "2024-03-15",
    "kit_id": "anonymized",
    "match": {
      "person_id": "uuid-cousin",
      "shared_cm": 847,
      "shared_percent": 12.5,
      "predicted_relationship": "first_cousin",
      "confidence": 0.92
    }
  }
}
```

---

### 5.5 Document

A Document is a binary or textual artifact that can be embedded in the bundle and linked to any entity.

```json
{
  "id": "doc-001",
  "type": "document",
  "axgf_version": "1.0",
  "created_at": "2026-05-01T10:00:00Z",

  "filename": "acte-naissance-jean-1923.pdf",
  "mime_type": "application/pdf",
  "document_type": "birth_certificate",
  "status": "present",

  "file": {
    "path": "documents/files/doc-001.pdf",
    "size_bytes": 1048576,
    "sha256": "a3f8c2d1e4b5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1"
  },

  "date": { "value": "1923-04-12", "precision": "exact" },
  "place_id": "place-001",
  "language": "fr",

  "linked_to": [
    { "entity_type": "person", "entity_id": "uuid-jean",  "role": "subject" },
    { "entity_type": "source", "entity_id": "src-001",    "role": "evidence" },
    { "entity_type": "event",  "entity_id": "evt-birth-jean", "role": "record" }
  ],

  "ocr": {
    "text": "Le douze avril mil neuf cent vingt-trois...",
    "confidence": 0.94,
    "language": "fr",
    "engine": "tesseract-5"
  },

  "ai": {
    "summary": "Birth certificate for Jean Pierre-Léonard, born 12 April 1923 in Saint-Denis.",
    "suggested_links": [
      {
        "entity_type": "person",
        "entity_id": "uuid-jean",
        "confidence": 0.97,
        "reason": "Name and date match exactly"
      }
    ]
  },

  "caption": "Acte de naissance — Jean Pierre-Léonard — 1923",
  "note": "Légèrement endommagé en bas de page, date lisible"
}
```

#### 5.5.1 Document Status

| Value | Description |
|---|---|
| `present` | File is embedded in the bundle |
| `referenced` | File exists but not embedded (external URL) |
| `known_missing` | Document is known to exist but not obtained |
| `lost` | Document is known to have been destroyed |
| `unknown` | Existence uncertain |

#### 5.5.2 Document Types

`photo`, `birth_certificate`, `death_certificate`, `marriage_certificate`, `census_page`, `baptism_record`, `military_record`, `will`, `land_record`, `letter`, `diary`, `newspaper_clipping`, `gravestone_photo`, `family_tree_drawing`, `audio`, `video`, `other`

---

## 6. Internationalization

### 6.1 Encoding

- All JSON files MUST be UTF-8 encoded (RFC 8259)
- No BOM (Byte Order Mark)
- All scripts are supported: Latin, Cyrillic, Hebrew, Arabic, CJK, Devanagari, etc.

### 6.2 Language Codes

Language codes follow BCP 47: `fr`, `en`, `de`, `ja`, `he`, `ar`, `ru`, `zh`, `es`, `pl`, etc.

### 6.3 Text Direction

| Value | Description |
|---|---|
| `ltr` | Left-to-right (Latin, Cyrillic, CJK) |
| `rtl` | Right-to-left (Hebrew, Arabic, Persian) |

### 6.4 Latin Transliteration

Every name component SHOULD provide `value_latin` for interoperability. When not available, implementors SHOULD use ISO 9 (Cyrillic), ISO 233 (Arabic), ALA-LC (Hebrew), or Hepburn (Japanese) romanization systems.

### 6.5 Country Codes

ISO 3166-1 alpha-2 codes: `FR`, `DE`, `JP`, `IL`, `RU`, `AR`, `GB`, etc.

Historical states that predate ISO codes use agreed extended codes:
- `SU` — Soviet Union
- `DD` — East Germany  
- `YU` — Yugoslavia
- `CS` — Czechoslovakia
- `OT` — Ottoman Empire (unofficial, for genealogical use)

---

## 7. AI Integration

### 7.1 Vault Section

The optional `vault/` directory contains Markdown narrative pages per entity, designed for direct consumption by large language models.

**vault/wiki/persons/{uuid}.md format:**

```markdown
# Jean Pierre-Léonard [id:550e8400]

**Birth**: 12 April 1923 (exact) — Saint-Denis, Réunion  
**Death**: 3 March 1987 — Paris 14e, France  
**Generation**: 2 (from known root)

## Identity
- Gender: Male
- Birth name: Jean-Baptiste Pierre-Léonard (source: birth certificate 1923)

## Direct Relations
- Son of: Henri Pierre-Léonard [id:uuid-henri] (1880–1952)
- Son of: Marguerite Fontaine [id:uuid-marguerite] (1885–1960)
- Husband of: Élise Bernard [id:uuid-elise] — from 1948
- Father of: Robert [id:...], Laurent [id:...], Karin [id:...]

## Affiliations
- Godfather of: Jules Martin [id:uuid-jules] (from 1950)

## Occupations
- Primary school teacher (1948–1978) — Saint-Denis, Réunion

## AI Hypotheses
> ⚠ PENDING — Possible sibling: Pierre Pierre-Léonard (1920-?) — score: 0.87
> Evidence: same surname, same birthplace, compatible parents

## Notes
Founder of the village school according to municipal archives.

---
*v3 — generated 2026-06-10 — axgf vault*
```

### 7.2 Hypothesis Status

| Value | Description |
|---|---|
| `pending` | Generated by AI, awaiting human review |
| `confirmed` | Validated by a human contributor |
| `rejected` | Rejected as false positive |
| `investigating` | Under active investigation |

### 7.3 Embedding Metadata

Implementations may store vector embedding metadata per entity:

```json
{
  "ai": {
    "embedding_model": "nomic-embed-text",
    "embedding_updated_at": "2026-06-10T14:22:00Z",
    "embedding_dimensions": 1536
  }
}
```

---

## 8. Confidence Model

### 8.1 Scale

All confidence values are floating point numbers between 0.0 and 1.0 inclusive.

| Range | Interpretation |
|---|---|
| 0.95 – 1.00 | Certain — primary source, multiple corroborating sources |
| 0.80 – 0.94 | High — primary source with minor uncertainty |
| 0.60 – 0.79 | Medium — secondary source or single primary source |
| 0.40 – 0.59 | Low — oral tradition, indirect evidence |
| 0.20 – 0.39 | Speculative — hypothesis, single indirect clue |
| 0.00 – 0.19 | Uncertain — AI inference only, no source |

### 8.2 Inheritance

When a confidence value is omitted, parsers MUST assume `null` (unknown), not 0.0 or 1.0.

### 8.3 Conflicting Sources

When two sources give different values for the same field, both values and sources MUST be recorded. The `conflicts[]` array in Source captures this explicitly.

---

## 9. Privacy Model

### 9.1 Visibility Levels

All entities carry a `visibility` field:

| Value | Description |
|---|---|
| `public` | Visible to all, including anonymous users |
| `members` | Visible to authenticated family members |
| `contributors` | Visible to contributors and admins only |
| `private` | Visible to admins only |

### 9.2 Living Persons

Persons with `is_living: true` are subject to privacy restrictions. Implementations MUST support redaction of living persons in exported bundles. The manifest MUST declare `contains_living_persons` and `living_persons_redacted`.

### 9.3 Sensitive Links

Links involving sensitive relationships (illegitimate children, private affiliations) SHOULD use `visibility: "private"` or `visibility: "contributors"`.

---

## 10. Versioning

### 10.1 Entity Versioning

Every entity carries `version_num` (integer, starting at 1). Each modification increments the version. The `meta.versions[]` array records the change history.

### 10.2 Format Versioning

The `axgf` field in the manifest and in each entity specifies the format version. This specification defines version `"1.0"`.

### 10.3 Backward Compatibility

Future versions of AXGF MUST be backward compatible with parsers for older versions. New required fields MUST NOT be added in minor versions. Unknown fields MUST be preserved.

### 10.4 Extension Fields

Custom fields use the `x-{vendor}-{field}` convention within the `extensions` object:

```json
{
  "extensions": {
    "x-myapp-internal-id": "12345",
    "x-myapp-sync-status": "pending"
  }
}
```

---

## 11. Compatibility

### 11.1 GEDCOM Import

Implementations providing GEDCOM import SHOULD map:

| GEDCOM Tag | AXGF Field |
|---|---|
| `INDI` | `person` entity |
| `FAM` | `family` entity |
| `NAME` | `person.identity.name` |
| `BIRT/DATE` | `person.birth.date` |
| `BIRT/PLAC` | `person.birth.place_id` |
| `DEAT/DATE` | `person.death.date` |
| `HUSB/WIFE` | `family.union.persons[]` |
| `CHIL` | `family.children[]` |
| `SOUR` | `source` entity |
| `OBJE` | `document` entity |
| `NOTE` | `person.notes` |

### 11.2 GEDCOM Export

Implementations providing GEDCOM 7 export SHOULD support the inverse mapping.

---

## 12. Validation

### 12.1 JSON Schema

Every bundle MUST include `schema/axgf-1.0.schema.json`. Conformant parsers SHOULD validate entities against this schema before importing.

### 12.2 Mandatory Fields

**Person**: `id`, `type`, `axgf_version`, `identity.name.display`, `identity.gender`, `identity.is_living`  
**Family**: `id`, `type`, `axgf_version`, `union.type`, `union.persons`  
**Event**: `id`, `type`, `axgf_version`, `category`, `date`  
**Link**: `id`, `type`, `axgf_version`, `from`, `to`, `label`  
**Manifest**: `axgf`, `created_at`, `stats`

### 12.3 UUID Format

All `id` fields MUST be lowercase UUID v4: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`

---

## 13. Examples

### 13.1 Minimal Valid Person

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
        { "type": "given_name",  "value": "Jean",            "order": 1 },
        { "type": "family_name", "value": "Pierre-Léonard",  "order": 2 }
      ]
    },
    "gender":    { "value": "M" },
    "is_living": false,
    "visibility": "members"
  }
}
```

### 13.2 Minimal Valid Manifest

```json
{
  "axgf": "1.0",
  "created_at": "2026-06-15T10:00:00Z",
  "updated_at": "2026-06-15T10:00:00Z",
  "stats": {
    "persons": 1,
    "families": 0,
    "events": 0,
    "links": 0
  }
}
```

---

## 14. Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-06-15 | Initial public draft |

---

## Appendix A — Design Decisions

**Why JSON and not YAML?**  
JSON has zero parsing ambiguity (no Norway problem), is natively supported in PostgreSQL, and is directly readable by all LLMs and APIs. YAML's advantages (comments, readability) do not outweigh its parsing complexity for a genealogy interchange format.

**Why is Family an independent entity?**  
A family has its own documents, history, and existence that transcends its members. A family unit known to have existed (based on census records) may have members whose identities are unknown. Making Family independent allows modeling partial knowledge without placeholder persons.

**Why are Links first-class entities?**  
A relationship between two people has its own temporal validity, confidence level, source, and history. By making links first-class, we can track when a relationship was established, when it ended, what the evidence is, and how confident we are — all without modifying either connected entity.

**Why is confidence mandatory?**  
Genealogical data is inherently uncertain. A format that does not model uncertainty forces implementors to pretend all facts are equally reliable, which is epistemically false. Mandatory confidence scores enable AI systems to reason about what needs verification.

---

*AXGF Specification 1.0 — June 2026*  
*Released under Creative Commons CC0 1.0 Universal*  
*https://gitlab.com/leonardkarin/axgf-spec*
