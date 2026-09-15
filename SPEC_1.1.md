# AXGF — Axiom Genealogy Format
## Specification Version 1.1 — Extended Person Profile
**Status**: Draft for Public Review  
**Date**: September 2026  
**Authors**: Karin Pierre-Léonard (ax-genealogy project)  
**License**: Creative Commons CC0 1.0 Universal (public domain)  
**Repository**: https://github.com/plkarin/axgf-spec  
**Schema**: [`schema/axgf-1.1.schema.json`](./schema/axgf-1.1.schema.json)  
**Extends**: [AXGF 1.0](./SPEC_1.0.md)

---

## Abstract

AXGF 1.1 lets a bundle carry a complete profile of an individual: how they were registered, what their body was like, how they spoke, their health and genome, how they died, where they lived, what they learned and earned, how they served, what they believed, how they behaved, and the digital artefacts made from them.

It is **additive**. Every conformant 1.0 bundle is a valid 1.1 bundle, nothing in 1.0 changes meaning, and a 1.0 reader that preserves unknown fields (1.0 P9) loses nothing by passing a 1.1 bundle through.

Three rules carry the whole extension, and matter more than the attributes they are applied to:

1. **Every attribute is a claim** — dated, sourced and rated with the shapes 1.0 already uses for every fact (§3).
2. **Anything that changes in a lifetime is a series, not a scalar** (§3.2).
3. **Wherever the possible answers can be known in advance, they are a closed vocabulary** defined here, so that two implementations store the same word for the same thing; where they cannot, the value is free text (§5, §6).

It also names four **sensitive classes** — health, biometrics, genomics and legal — so that every implementation can withhold, export and audit the same data by the same rule rather than each inventing its own (§4).

---

## Table of Contents

1. [Scope](#1-scope)
2. [Versioning and Compatibility](#2-versioning-and-compatibility)
3. [Claims and Shared Shapes](#3-claims-and-shared-shapes)
4. [Sensitive Classes](#4-sensitive-classes)
5. [Attribute Groups](#5-attribute-groups)
   - 5.1 [Identity and civil status](#51-identity-and-civil-status)
   - 5.2 [Morphology](#52-morphology)
   - 5.3 [Biometrics](#53-biometrics)
   - 5.4 [Health](#54-health)
   - 5.5 [Genomics](#55-genomics)
   - 5.6 [Death](#56-death)
   - 5.7 [Residence and nationality](#57-residence-and-nationality)
   - 5.8 [Education and work](#58-education-and-work)
   - 5.9 [Military and honours](#59-military-and-honours)
   - 5.10 [Legal](#510-legal)
   - 5.11 [Belief and affiliation](#511-belief-and-affiliation)
   - 5.12 [Personality and behaviour](#512-personality-and-behaviour)
   - 5.13 [Relationships](#513-relationships)
   - 5.14 [Digital legacy](#514-digital-legacy)
6. [Vocabulary Index](#6-vocabulary-index)
7. [Validation](#7-validation)
8. [Complete Example](#8-complete-example)
9. [Changelog](#9-changelog)
- [Appendix A — Design Decisions](#appendix-a--design-decisions)

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be read as described in RFC 2119.

---

## 1. Scope

### 1.1 What 1.1 adds

- Twelve attribute blocks on **Person**: `civil_status`, `morphology`, `biometrics`, `health`, `genomics`, `residence`, `education`, `military`, `legal`, `belief`, `personality` and `digital_legacy`, and new attributes inside the existing `identity`, `birth` and `death` blocks.
- `lineage` on **Family** `children[]`, `relation` on **Link** and `position` on **Occupation**, which together make every relationship in §5.13 expressible without putting relationships on the person.
- The four sensitive classes, a per-person `identity.class_visibility`, and `manifest.privacy.withheld_classes`.
- 102 closed vocabularies, all enumerated in the schema.

### 1.2 What 1.1 does not change

Bundle layout, entity identity, dates, places, sources, documents, confidence, visibility, versioning of entities and every 1.0 vocabulary are unchanged. Where a 1.0 field already records something in the attribute groups — a birth date, a nickname, an occupation, a spouse — 1.1 says where, and adds nothing beside it: a fact recorded in two places is a fact that will one day disagree with itself.

### 1.3 Groups are an organisation, not a structure

§5 is organised into fourteen groups, and an implementation SHOULD present them in this order under these names, so that a contributor learns one organisation that holds in every tool. The groups do not map one-to-one onto JSON: most are a block on Person, *Identity and civil status* spans three blocks, *Death* extends the 1.0 `death` block, and *Relationships* lives entirely on Family and Link. Each group's table gives the path of every attribute.

---

## 2. Versioning and Compatibility

### 2.1 Declaring 1.1

- A bundle that contains any 1.1 attribute MUST declare `"axgf": "1.1"` in its manifest.
- An entity that carries any 1.1 attribute MUST declare `"axgf_version": "1.1"`. An entity that carries none MAY keep `"1.0"`: its content is 1.0 content, and nothing obliges a writer to relabel it.
- An entity MUST NOT declare a version newer than its bundle's manifest.
- A writer that adds a 1.1 attribute to a 1.0 bundle raises the manifest to `"1.1"` in the same write, exactly as it refreshes `stats`. A writer MUST NOT lower a manifest's version.

### 2.2 Reading

A 1.1 reader MUST accept both `"1.0"` and `"1.1"`. A 1.0 reader will refuse a `"1.1"` manifest if it gates on version, as 1.0 §10 permits; one that does not will see the 1.1 blocks as unknown fields and, under 1.0 P9, preserve them.

### 2.3 The schema file

A 1.1 bundle carries `schema/axgf-1.1.schema.json` in place of `schema/axgf-1.0.schema.json` (1.0 §2). The 1.1 schema is a superset: the only 1.0 constraints it widens are the two version fields, and every conformant 1.0 entity is valid under it. (Conformant matters in one corner: 1.0 reserves unprefixed field names to the specification and puts vendor data under `extensions` (1.0 §10.4), so a 1.0 entity that had used a name such as `health` on its own account was already outside 1.0 and may fail here.)

Every attribute in the schema carries two annotations that validators ignore and implementations may read:

| Keyword | Meaning |
|---|---|
| `x-axgf-class` | The attribute's sensitive class (§4). Absent when it has none. |
| `x-axgf-unit` | The unit a number is recorded in (§3.4). |

---

## 3. Claims and Shared Shapes

### 3.1 The claim

Every 1.1 attribute holds claims. A claim is one statement about the person, with its evidence:

```json
{
  "value": 158,
  "date": { "value": "1950", "precision": "year" },
  "source_id": "9b2f0d1e-3c4a-4b5d-8e6f-7a8b9c0d1e2f",
  "confidence": 0.9,
  "note": "Conscription register, height column."
}
```

| Field | Required | Shape | Meaning |
|---|---|---|---|
| `value` | yes | per attribute | What is claimed. A scalar, or an object whose fields the attribute defines. |
| `date` | no | `axgf_date` (1.0 §5.2) | The moment the claim describes: when the height was measured, the sacrament received, the annotation written. |
| `valid_from` | no | `{ date, event_id }` | The start of a period the claim holds for, in the shape 1.0 Link and Occupation use. |
| `valid_until` | no | `{ date, event_id }` | The end of that period. |
| `source_id` | no | uuid | The Source the claim rests on (1.0 P5). |
| `event_id` | no | uuid | An Event the claim was recorded at or derives from. |
| `confidence` | no | 0.0–1.0 | 1.0 §8. Absent means unknown, never 0 or 1 (1.0 §8.2). |
| `note` | no | string | Free text: the source's own wording, a unit it was converted from, a doubt. |

There is no second shape. The date, source and confidence of a 1.1 claim are the date, source and confidence of every 1.0 fact, so a reader that renders one renders the other.

A claim's `value` MUST NOT be empty: a claim that there is nothing to say is not written. An attribute that is unknown is absent.

### 3.2 Single claims and series

Each attribute is one of two kinds, stated in its group's table:

- **single** — one claim object. Used only for what is fixed at birth or by one event and cannot take another value later in the same life: sex at birth, birth time, blood group, haplogroups, skin phototype.
- **series** — an array of claims. Used for **anything that can change in a lifetime**: weight, address, nationality, hair colour, blood pressure, income, and most of the body. A height measured at twenty and again at fifty-six is two facts, not one fact revised, and the series keeps both.

A series is ordered by nothing but its dates; writers SHOULD keep it in date order and readers MUST NOT rely on it. An undated entry is still an entry.

The line is drawn at *change*, not at *frequency of record*. Eye spacing is recorded once in most lives and is still a series, because a child's and an adult's are different facts.

### 3.3 Disagreeing sources

For a **series**, two sources that disagree are two entries, each with its source and confidence. For a **single** claim, the preferred value is the claim and the disagreement is recorded where 1.0 already records it: in the Source's `conflicts[]` (1.0 §5.4, §8.3), with `field` set to the attribute's path — `health.blood_group`.

### 3.4 Units

Every numeric attribute has one fixed unit, given in its table and in the schema as `x-axgf-unit`: centimetres, kilograms, hertz, millimetres of mercury. A writer converts, and says in `note` what the source actually wrote — "5 ft 2 in". Fixed units are a closed vocabulary of one: nobody has to guess whether 62 is inches or kilograms.

Laboratory results are the one exception, because two unit conventions are both in legitimate daily use; there, the unit is a field drawn from UCUM (§5.4).

### 3.5 Shared shapes

| Shape | Definition |
|---|---|
| `coordinates` | `{ "lat", "lon", "precision" }`, the shape of 1.0 Place `coordinates`, with `lat` and `lon` required. |
| `time_of_day` | Local time as the source records it: `HH:MM` or `HH:MM:SS`. A time zone, where it matters, goes in `note`. |
| `language_tag` | A BCP 47 tag with optional script, region and variant subtags — `pl`, `zh-Hant`, `pl-PL`, `de-CH-1901` — or `und` when the language cannot be determined. 1.0's narrower `bcp47_lang` is unchanged. |
| `currency_code` | An ISO 4217 alphabetic code, current or historic: `PLN`, `PLZ`, `DEM`. |
| `country` | A closed vocabulary: the 249 ISO 3166-1 alpha-2 codes, plus the historical codes of 1.0 §6.5 (`SU`, `DD`, `YU`, `CS`, `OT`). |
| `artefact` | A reference to a Document holding an artefact, below. |

#### 3.5.1 Artefact references

Some attributes hold things, not facts: a fingerprint card, a voice corpus, a mesh. Their value is a reference to a Document (1.0 §5.5), never the bytes inline and never a URL on its own:

```json
{
  "value": {
    "document_id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
    "artefact_type": "voice_corpus",
    "format": "FLAC",
    "generator": null,
    "derived_from_id": null,
    "consent": "given_by_estate"
  },
  "date": { "value": "2021", "precision": "year" },
  "confidence": 0.95
}
```

| Field | Required | Meaning |
|---|---|---|
| `document_id` | yes | The Document. Its `status` (1.0 §5.5.1) says whether the bundle holds the file. |
| `artefact_type` | yes | From the vocabulary below; each attribute allows only the types that belong to it. |
| `format` | no | The file format by its usual name: `OBJ`, `PLY`, `FLAC`, `GGUF`. |
| `generator` | no | The software, device or model that produced it. |
| `derived_from_id` | no | Another Document this one was made from — a rig from a mesh, a model from a corpus. |
| `consent` | no | Whether the person, or after their death whoever could, consented to the artefact being made and kept. |

The Document itself uses `document_type: "other"` unless 1.0's vocabulary already names it (`audio`, `video`); the artefact's type is on the reference, where it can be as specific as the attribute needs.

#### 3.5.2 Shared vocabularies

**`laterality`** — Laterality

| Term | Meaning |
|---|---|
| `left` | The left side. |
| `right` | The right side. |
| `both` | Both sides, or not separable. |

**`body_region`** — Body region

| Term | Meaning |
|---|---|
| `head` | Head, excluding the face. |
| `face` | Face. |
| `neck` | Neck. |
| `left_shoulder` | Left shoulder. |
| `right_shoulder` | Right shoulder. |
| `left_arm` | Left arm, from shoulder to wrist. |
| `right_arm` | Right arm, from shoulder to wrist. |
| `left_hand` | Left hand and fingers. |
| `right_hand` | Right hand and fingers. |
| `chest` | Chest. |
| `abdomen` | Abdomen. |
| `upper_back` | Upper back. |
| `lower_back` | Lower back. |
| `pelvis` | Pelvis, hips and groin. |
| `left_leg` | Left leg, from hip to ankle. |
| `right_leg` | Right leg, from hip to ankle. |
| `left_foot` | Left foot and toes. |
| `right_foot` | Right foot and toes. |
| `internal` | Inside the body; no surface location. |
| `whole_body` | The whole body, or no single region. |
| `other` | A region not listed; say which in the note. |

**`artefact_type`** — Artefact type

| Term | Meaning |
|---|---|
| `mesh` | A polygon mesh of the body or a part of it (for example OBJ, PLY, glTF). |
| `point_cloud` | An unmeshed point cloud from a scan or photogrammetry (for example PLY, E57, LAS). |
| `skin_texture_map` | A texture map of the skin, registered to a mesh. |
| `skeletal_rig` | A skeleton and joint hierarchy that animates a body model. |
| `voice_corpus` | Recorded speech collected to synthesise the person's voice. |
| `text_corpus` | Writing by the person, collected to train or condition a language model. |
| `trace_archive` | An export of the person's accounts, messages or other online activity. |
| `behaviour_model` | A trained model that reacts in the manner of the person. |
| `fingerprint_card` | An image of inked or scanned fingerprints, such as a ten-print card. |
| `fingerprint_template` | A minutiae template or other encoded fingerprint. |
| `retinal_image` | An image or template of the retina. |
| `voiceprint` | An encoded speaker-recognition template. |

**`consent`** — Consent

| Term | Meaning |
|---|---|
| `given` | The person consented. |
| `given_by_estate` | Consent was given after death by the person entitled to give it. |
| `refused` | Consent was refused. |
| `withdrawn` | Consent was given and later withdrawn. |
| `not_asked` | Nobody asked. |
| `unknown` | Whether consent exists is not known. |

**`country`** — Country. *ISO 3166-1 alpha-2, plus the historical codes of AXGF 1.0 §6.5.*

The 249 officially assigned ISO 3166-1 alpha-2 codes, as enumerated in the schema, and the five historical codes of 1.0 §6.5: `SU`, `DD`, `YU`, `CS`, `OT`. User-assigned codes such as `XK` are not in the vocabulary.

---

## 4. Sensitive Classes

### 4.1 The four classes

Some attributes describe what is most harmful to disclose about a person. 1.1 names four classes of them, and every attribute belongs to at most one:

| Class | Covers |
|---|---|
| `health` | Physical and mental health, treatment and results — and the other special categories of personal data that are neither biometric nor genetic: religious or philosophical belief, political opinion, and trade-union or similar membership. |
| `biometrics` | Measurements and templates of the body or voice that can identify a person: fingerprints, retinal prints, voiceprints and their measures, body and face models. |
| `genomics` | Genetic and other molecular data: DNA tests and sequences, haplogroups, variants, epigenetic and microbiome results. |
| `legal` | Criminal proceedings and their outcomes. |

The classes are **independent**. An implementation MUST be able to grant, withhold, export and audit each one without the others: a reader may be shown a person's criminal record and not their diagnoses, and an export may carry health data and leave out genomes.

The class of each attribute is fixed by this specification and stated in its group's table and in the schema (`x-axgf-class`). Classes follow the data, not the groups: `motor_tics` in *Biometrics* is `health`, `dependencies` in *Personality and behaviour* is `health`, and *Belief and affiliation* is `health` throughout (Appendix A.6). An implementation MAY govern any attribute more strictly than its class. It MUST NOT govern one less strictly.

1.0's `death.cause` belongs to `health`.

### 4.2 Attributes by class

| Class | Attributes |
|---|---|
| `health` | `death.cause` (1.0), `biometrics.motor_tics`, `biometrics.hearing`, `biometrics.visual_acuity`, `biometrics.optical_correction`, `health.blood_group`, `health.rhesus`, `health.blood_pressure`, `health.resting_heart_rate`, `health.respiratory_capacity`, `health.conditions`, `health.surgeries`, `health.injuries`, `health.deformities`, `health.amputations`, `health.prostheses`, `health.implants`, `health.devices`, `health.medications`, `health.allergies`, `health.vaccinations`, `health.serology`, `health.lab_results`, `health.deficiencies`, `health.sleep_disorders`, `health.mental_health_assessments`, `death.causes`, `death.contributing_factors`, `death.autopsy`, `belief.religions`, `belief.sacraments`, `belief.beliefs`, `belief.political_leanings`, `belief.memberships`, `personality.dependencies` |
| `biometrics` | `biometrics.fingerprints`, `biometrics.retinal_print`, `biometrics.voice_signature`, `biometrics.voice_frequency`, `biometrics.vocal_timbre`, `biometrics.speech_rate`, `digital_legacy.body_models`, `digital_legacy.skin_textures`, `digital_legacy.rigs`, `digital_legacy.voice_corpora` |
| `genomics` | `genomics.autosomal_mapping`, `genomics.y_haplogroup`, `genomics.mt_haplogroup`, `genomics.whole_genome_sequencing`, `genomics.risk_variants`, `genomics.hereditary_conditions`, `genomics.predispositions`, `genomics.epigenetic_markers`, `genomics.epigenetic_age`, `genomics.gut_microbiome`, `genomics.skin_microbiome`, `genomics.toxicological_sensitivities` |
| `legal` | `legal.criminal_record` |

### 4.3 Default visibility

A class's data on a person is visible at the most restrictive of the person's record visibility (1.0 §9.1) and the class default:

| Subject | `health`, `biometrics`, `legal` | `genomics` |
|---|---|---|
| Living (`identity.is_living: true`) | `private` | `private` |
| Deceased | the record's visibility | the record's visibility, but never `public` — at least `members` |

- **A living person's class data is `private`** — administrators only — whatever the record's own visibility. A person whose record is `public` does not thereby publish their diagnoses.
- **A deceased person's class data follows the record**: a cause of death two centuries old is the substance of genealogy.
- **A deceased person's genome is never public.** It is a partial genome of every living descendant, and publishing a grandmother's pathogenic variant states a risk for her grandchildren (Appendix A.7).
- **Living means the recorded flag.** Implementations often infer that somebody born long ago must be dead; such an inference MAY change how a record is displayed and MUST NOT relax class visibility. A presumption of death that opened class data would publish every such person's health at once.

A reader who may not see a class's data SHOULD be told that data exists and is withheld, rather than being shown a record that silently looks empty. Omission is a statement too, and a false one.

### 4.4 Per-person class visibility

`identity.class_visibility` sets a visibility for one or more classes on one person:

```json
"identity": {
  "is_living": false,
  "visibility": "public",
  "class_visibility": { "health": "members", "legal": "private" }
}
```

It can only **tighten**: the effective visibility is the more restrictive of this value and §4.3. A family that wants a deceased relative's psychiatric history kept to signed-in members, or a conviction kept to administrators, says so here. Nothing can make a living person's class data less than `private`.

### 4.5 What must carry the rule

Class data leaks through the surfaces nobody was thinking about rather than the ones they were. An implementation that withholds a class MUST withhold it from every copy of the value, including:

- **Histories and journals.** A recorded change carries the value that changed; a change to a class attribute is class data. The change SHOULD keep its row and lose its values, so the history stays true about *that* something changed.
- **Raw views.** Any display or editor of an entity's JSON MUST strip the withheld classes before serialising, not after.
- **Conflict and merge screens**, which show the stored entity to somebody who did not write it.
- **Round trips.** A form that was given an entity with a class stripped out MUST NOT delete that class's data when submitted: absence in what comes back is the redaction returning, not an edit.
- **Derived values.** Anything computed from class data — a score, a chart, a summary — carries the most restrictive class among its inputs, and MUST be computed only from data the reader may see (§4.7).
- **Exports.** An export that leaves a class out MUST list it in `manifest.privacy.withheld_classes`, so a recipient can tell "no health data" from "health data withheld". Exports SHOULD leave all four classes out unless their inclusion is chosen for that export.

```json
"privacy": {
  "contains_living_persons": true,
  "living_persons_redacted": false,
  "withheld_classes": ["health", "genomics"]
}
```

### 4.6 Behavioural profiles of living persons

*Personality and behaviour* (§5.12) has no class of its own, and a single hobby is not sensitive. But the group taken together, about a living person, is an inferred psychological profile, and a model trained to react as that person (`digital_legacy.behaviour_models`) is one in executable form. Implementations SHOULD govern the group and those models, for a living person, as they govern a sensitive class.

### 4.7 Derived values are not claims

A score, a percentile, a classification or any other value computed from recorded claims MUST NOT be written into a bundle as an attribute. Written down, today's inference reaches a future reader looking exactly like a recorded fact, with a confidence it never earned. A computed value belongs to the software that computes it, and is recomputed when the claims change. The only exception is a value a *source* states — a BMI on a medical record, a percentile on a test report — which is a claim like any other, with that source.

---

## 5. Attribute Groups

Each group lists its attributes in the order an implementation should present them. The **Attribute** column names what is recorded; **Path** is relative to the Person, or names the entity it lives on; **Kind** is *single* or *series* (§3.2), or *mapped* where an existing field records it and 1.1 adds nothing; **Value** is the claim's `value`; **Class** is its sensitive class (§4).

In value shapes, `text` is a non-empty string, a bold name is a vocabulary from this specification, and `?` marks an optional field. An object value lists its fields; `one of` names fields of which at least one is required.

### 5.1 Identity and civil status

What the record says the person is called and was registered as, and where the registers say so. Names, birth date and birth place are 1.0 fields and stay where they are.

`identity.gender` (1.0) remains the record's gender. `sex_at_birth` is what the birth was registered as, and `gender_identity` how the person identified; a record that knows neither leaves both out rather than copying `gender` into them.

#### 5.1.1 Attributes

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Full name | identity.name.display | mapped | — | — |
| Given names | identity.name.components[type=given_name] | mapped | — | — |
| Nicknames | identity.names[type=nickname], identity.name.components[type=nickname] | mapped | — | — |
| Titles | `identity.titles` | series | `text` text; `kind?` **title_kind** | — |
| Sex at birth | `identity.sex_at_birth` | single | **sex_at_birth** | — |
| Gender identity | `identity.gender_identity` | series | **gender_identity** | — |
| Birth date | birth.date | mapped | — | — |
| Birth time | `birth.time` | single | time_of_day | — |
| Birth place | birth.place_id | mapped | — | — |
| Birth coordinates | `birth.coordinates` | single | coordinates | — |
| Birth certificate number | `civil_status.birth_certificate_number` | single | text | — |
| Civil register entries | `civil_status.register_entries` | series | `register_type` **register_type**; `office?` text; `place_id?` uuid; `volume?` text; `page?` text; `entry_number?` text | — |
| Marginal annotations | `civil_status.marginal_annotations` | series | `text` text; `register_type?` **register_type**; `entry_number?` text | — |

- **`identity.titles`** — The title as written — "Dr.", "Hrabia", "Monsignor" — with what kind of title it is.
- **`identity.sex_at_birth`** — What the birth was registered as. `identity.gender` (1.0) is unchanged and remains the record's gender.
- **`identity.gender_identity`** — How the person identified, dated.
- **`birth.time`** — Local time as recorded, `HH:MM` or `HH:MM:SS`.
- **`birth.coordinates`** — Where the birth took place, when it is known more precisely than the place.
- **`civil_status.birth_certificate_number`** — The number of the birth certificate or act.
- **`civil_status.register_entries`** — One entry per act in a civil or parish register that serves as one.
- **`civil_status.marginal_annotations`** — A later mention written in the margin of an entry — a marriage, a divorce, a death. The claim's date is the date of the annotation.

#### 5.1.2 Vocabularies

**`title_kind`** — Title kind

| Term | Meaning |
|---|---|
| `nobility` | A hereditary or conferred title of nobility. |
| `academic` | An academic title or degree used as a title. |
| `professional` | A title belonging to a profession. |
| `religious` | A religious title or style. |
| `military` | A military title used as a style of address. |
| `civic` | A civic or honorary title. |
| `courtesy` | A courtesy style of address. |
| `other` | Another kind of title. |

**`sex_at_birth`** — Sex at birth

| Term | Meaning |
|---|---|
| `female` | Recorded female at birth. |
| `male` | Recorded male at birth. |
| `intersex` | Recorded with a variation of sex characteristics. |
| `undetermined` | Recorded at birth as undetermined. |
| `unknown` | Not known to the researcher. |

**`gender_identity`** — Gender identity

| Term | Meaning |
|---|---|
| `woman` | Identifies as a woman. |
| `man` | Identifies as a man. |
| `non_binary` | Identifies outside the binary. |
| `other` | Another identity; the note may say which. |
| `undisclosed` | The person chose not to say. |
| `unknown` | Not known to the researcher. |

**`register_type`** — Register entry type

| Term | Meaning |
|---|---|
| `birth` | A civil birth entry. |
| `baptism` | A baptism entry serving as the record of birth. |
| `marriage` | A marriage entry. |
| `death` | A civil death entry. |
| `burial` | A burial entry serving as the record of death. |
| `divorce` | A divorce entry or its transcription. |
| `recognition` | Recognition of a child. |
| `legitimation` | Legitimation of a child. |
| `adoption` | An adoption entry. |
| `name_change` | A change of name. |
| `other` | Another kind of entry. |

#### 5.1.3 Example

```json
{
  "identity": {
    "name": { "display": "Zofia Nowicka", "components": [] },
    "gender": { "value": "F" },
    "is_living": false,
    "titles": [
      { "value": { "text": "dr", "kind": "academic" },
        "date": { "value": "1961", "precision": "year" }, "confidence": 0.95 }
    ],
    "sex_at_birth": { "value": "female", "confidence": 0.99 }
  },
  "birth": {
    "date": { "value": "1932-03-14", "precision": "exact" },
    "time": { "value": "05:40", "confidence": 0.8 }
  },
  "civil_status": {
    "birth_certificate_number": { "value": "212/1932", "confidence": 0.99 },
    "register_entries": [
      { "value": { "register_type": "birth", "office": "Urząd Stanu Cywilnego Lublin-Śródmieście",
                   "volume": "1932/I", "page": "71", "entry_number": "212" },
        "date": { "value": "1932-03-16", "precision": "exact" }, "confidence": 0.99 }
    ],
    "marginal_annotations": [
      { "value": { "text": "Zawarła związek małżeński 12.08.1955 w Lublinie, akt 604/1955.",
                   "register_type": "birth", "entry_number": "212" },
        "date": { "value": "1955-08-20", "precision": "exact" }, "confidence": 0.95 }
    ]
  }
}
```

### 5.2 Morphology

The body as it was measured and described — by a conscription register, a passport, a medical record, a photograph or a relative. Descriptions are recorded in the source's terms mapped to the vocabulary, with the source's own word in `note` when the mapping took judgement.

Nearly all of it is a series: a body changes, and two sources a generation apart are both right. Only `skin_tone` and `skin_undertone`, which are constitutive, are single.

Skin tone uses Fitzpatrick's six phototypes; Appendix A.4 says why that scale and not von Luschan's.

#### 5.2.1 Attributes

Block: `morphology` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Exact height | `morphology.height` | series | number (cm, 20–300) | — |
| Weight over time | `morphology.weight` | series | number (kg, 0.3–700) | — |
| BMI | `morphology.bmi` | series | number (kg/m², 5–150) | — |
| Body composition | `morphology.body_composition` | series | `bone_percent?` number (%, 0–100); `muscle_percent?` number (%, 0–100); `fat_percent?` number (%, 0–100); one of: `bone_percent` or `muscle_percent` or `fat_percent` | — |
| Build | `morphology.build` | series | **build** | — |
| Precise eye colour | `morphology.eye_colour` | series | **eye_colour** | — |
| Eye shape | `morphology.eye_shape` | series | **eye_shape** | — |
| Eye spacing | `morphology.eye_spacing` | series | **eye_spacing** | — |
| Natural hair colour | `morphology.hair_colour` | series | **hair_colour** | — |
| Hair texture | `morphology.hair_texture` | series | **hair_texture** | — |
| Hairline | `morphology.hairline` | series | **hairline** | — |
| Facial hair | `morphology.facial_hair` | series | **facial_hair** | — |
| Body hair | `morphology.body_hair` | series | **body_hair** | — |
| Skin tone | `morphology.skin_tone` | single | **skin_tone** | — |
| Skin undertone | `morphology.skin_undertone` | single | **skin_undertone** | — |
| Freckles | `morphology.freckles` | series | **freckles** | — |
| Pigmentation | `morphology.pigmentation` | series | `kind` **pigmentation_mark**; `body_region?` **body_region**; `description?` text | — |
| Scars | `morphology.scars` | series | `description` text; `body_region?` **body_region** | — |
| Tattoos | `morphology.tattoos` | series | `description` text; `body_region?` **body_region** | — |
| Moles with location and shape | `morphology.moles` | series | `body_region` **body_region**; `location?` text; `shape?` **mole_shape**; `diameter_mm?` number (mm, 0–500) | — |
| Facial asymmetries | `morphology.facial_asymmetries` | series | text | — |
| Facial bone structure | `morphology.face_shape` | series | **face_shape** | — |
| Nose shape | `morphology.nose_shape` | series | **nose_shape** | — |
| Ear shape | `morphology.ear_shape` | series | **ear_shape** | — |
| Lip shape | `morphology.lip_shape` | series | **lip_shape** | — |
| Dentition | `morphology.dentition` | series | **dentition** | — |
| Dental malocclusion | `morphology.malocclusion` | series | **malocclusion** | — |
| Posture | `morphology.posture` | series | **posture** | — |
| Gait | `morphology.gait` | series | **gait** | — |
| Distinguishing features | `morphology.distinguishing_features` | series | text | — |

- **`morphology.height`** — Centimetres.
- **`morphology.weight`** — Kilograms.
- **`morphology.bmi`** — As recorded by the source. A reader MAY compute one from height and weight but MUST NOT write it here unless a source states it.
- **`morphology.body_composition`** — Shares of body mass. At least one.
- **`morphology.build`** — What a conscription register or a passport records where no composition was ever measured.
- **`morphology.eye_colour`** — An infant's blue eyes may be brown at five: a series.
- **`morphology.hair_colour`** — Natural colour, not dyed.
- **`morphology.skin_tone`** — Fitzpatrick phototype, which is constitutive and does not change; see Appendix A.4 for why this scale.
- **`morphology.pigmentation`** — Marks described by their appearance, not diagnosed.
- **`morphology.scars`** — Free text.
- **`morphology.tattoos`** — Free text.
- **`morphology.facial_asymmetries`** — Free text.
- **`morphology.malocclusion`** — Angle class.
- **`morphology.distinguishing_features`** — Anything else a passport or a register notes about appearance. Free text.

#### 5.2.2 Vocabularies

**`build`** — Build

| Term | Meaning |
|---|---|
| `slight` | Slight. |
| `slim` | Slim. |
| `average` | Average. |
| `sturdy` | Sturdy. |
| `stout` | Stout. |
| `heavy` | Heavy. |

**`eye_colour`** — Eye colour

| Term | Meaning |
|---|---|
| `light_blue` | Light blue. |
| `blue` | Blue. |
| `dark_blue` | Dark blue. |
| `grey` | Grey. |
| `blue_grey` | Blue-grey. |
| `green` | Green. |
| `grey_green` | Grey-green. |
| `hazel` | Hazel. |
| `amber` | Amber. |
| `light_brown` | Light brown. |
| `brown` | Brown. |
| `dark_brown` | Dark brown. |
| `black` | Black, or brown too dark to distinguish. |
| `mixed` | More than one colour in one iris or between the two irises. |
| `other` | A colour not listed. |

**`eye_shape`** — Eye shape

| Term | Meaning |
|---|---|
| `almond` | Almond. |
| `round` | Round. |
| `hooded` | Hooded. |
| `monolid` | Monolid. |
| `deep_set` | Deep-set. |
| `protruding` | Protruding. |
| `upturned` | Upturned. |
| `downturned` | Downturned. |
| `other` | Another shape. |

**`eye_spacing`** — Eye spacing

| Term | Meaning |
|---|---|
| `close_set` | Close-set. |
| `average` | Average. |
| `wide_set` | Wide-set. |

**`hair_colour`** — Natural hair colour

| Term | Meaning |
|---|---|
| `black` | Black. |
| `dark_brown` | Dark brown. |
| `brown` | Brown. |
| `light_brown` | Light brown. |
| `auburn` | Auburn. |
| `red` | Red. |
| `strawberry_blond` | Strawberry blond. |
| `dark_blond` | Dark blond. |
| `blond` | Blond, or fair. |
| `light_blond` | Light blond. |
| `grey` | Grey. |
| `white` | White. |
| `none` | No hair. |
| `other` | A colour not listed. |

**`hair_texture`** — Hair texture

| Term | Meaning |
|---|---|
| `straight` | Straight. |
| `wavy` | Wavy. |
| `curly` | Curly. |
| `coily` | Coily or tightly curled. |
| `other` | Another texture. |

**`hairline`** — Hairline

| Term | Meaning |
|---|---|
| `straight` | Straight. |
| `rounded` | Rounded. |
| `widows_peak` | Widow's peak. |
| `m_shaped` | M-shaped. |
| `bell_shaped` | Bell-shaped. |
| `uneven` | Uneven. |
| `receding` | Receding. |
| `bald` | Bald. |

**`facial_hair`** — Facial hair

| Term | Meaning |
|---|---|
| `none` | None. |
| `stubble` | Stubble. |
| `moustache` | Moustache. |
| `goatee` | Goatee. |
| `full_beard` | Full beard. |
| `sideburns` | Sideburns. |
| `other` | Another style. |

**`body_hair`** — Body hair

| Term | Meaning |
|---|---|
| `none` | None. |
| `sparse` | Sparse. |
| `moderate` | Moderate. |
| `dense` | Dense. |

**`skin_tone`** — Skin tone (Fitzpatrick phototype). *Fitzpatrick, T. B. (1988), The validity and practicality of sun-reactive skin types I through VI.*

| Term | Meaning |
|---|---|
| `type_i` | Type I: pale; always burns, never tans. |
| `type_ii` | Type II: fair; usually burns, tans minimally. |
| `type_iii` | Type III: light to medium; sometimes burns, tans uniformly. |
| `type_iv` | Type IV: olive or light brown; burns minimally, always tans well. |
| `type_v` | Type V: brown; very rarely burns, tans very easily. |
| `type_vi` | Type VI: dark brown to black; never burns. |

**`skin_undertone`** — Skin undertone

| Term | Meaning |
|---|---|
| `cool` | Cool. |
| `neutral` | Neutral. |
| `warm` | Warm. |
| `olive` | Olive. |

**`freckles`** — Freckles

| Term | Meaning |
|---|---|
| `none` | None. |
| `few` | Few. |
| `moderate` | Moderate. |
| `many` | Many. |

**`pigmentation_mark`** — Pigmentation mark

| Term | Meaning |
|---|---|
| `birthmark` | A birthmark not otherwise listed. |
| `port_wine_stain` | A port-wine stain. |
| `cafe_au_lait_spot` | A café-au-lait spot. |
| `depigmented_patch` | A patch lighter than the surrounding skin. |
| `hyperpigmented_patch` | A patch darker than the surrounding skin. |
| `other` | Another mark. |

**`mole_shape`** — Mole shape

| Term | Meaning |
|---|---|
| `round` | Round. |
| `oval` | Oval. |
| `irregular` | Irregular. |
| `other` | Another shape. |

**`face_shape`** — Face shape

| Term | Meaning |
|---|---|
| `oval` | Oval. |
| `round` | Round. |
| `square` | Square. |
| `oblong` | Oblong. |
| `heart` | Heart-shaped. |
| `diamond` | Diamond. |
| `triangular` | Triangular. |

**`nose_shape`** — Nose shape

| Term | Meaning |
|---|---|
| `straight` | Straight. |
| `aquiline` | Aquiline, or Roman. |
| `snub` | Snub. |
| `upturned` | Upturned. |
| `flat` | Flat. |
| `broad` | Broad. |
| `bulbous` | Bulbous. |
| `crooked` | Crooked. |
| `other` | Another shape. |

**`ear_shape`** — Ear shape

| Term | Meaning |
|---|---|
| `free_lobe` | Free earlobes. |
| `attached_lobe` | Attached earlobes. |
| `protruding` | Protruding. |
| `close_set` | Close to the head. |
| `pointed` | Pointed. |
| `other` | Another shape. |

**`lip_shape`** — Lip shape

| Term | Meaning |
|---|---|
| `thin` | Thin. |
| `medium` | Medium. |
| `full` | Full. |
| `bow_shaped` | Bow-shaped. |
| `wide` | Wide. |
| `downturned` | Downturned. |
| `other` | Another shape. |

**`dentition`** — Dentition

| Term | Meaning |
|---|---|
| `primary` | Primary teeth only. |
| `mixed` | Primary and permanent teeth. |
| `permanent_complete` | Permanent teeth, complete. |
| `permanent_partial_loss` | Permanent teeth, some lost. |
| `edentulous` | No natural teeth. |
| `partial_denture` | A partial denture. |
| `full_denture` | A full denture. |
| `implants` | Dental implants. |

**`malocclusion`** — Malocclusion (Angle class). *Angle, E. H. (1899), Classification of malocclusion.*

| Term | Meaning |
|---|---|
| `normal` | Normal occlusion. |
| `class_i` | Class I: normal molar relationship with crowding, spacing or rotation. |
| `class_ii_division_1` | Class II, division 1: lower molar distal, upper incisors proclined. |
| `class_ii_division_2` | Class II, division 2: lower molar distal, upper incisors retroclined. |
| `class_iii` | Class III: lower molar mesial. |

**`posture`** — Posture. *Kendall, McCreary et al., Muscles: Testing and Function (postural types).*

| Term | Meaning |
|---|---|
| `ideal` | Ideal alignment. |
| `kyphotic_lordotic` | Kyphosis-lordosis. |
| `flat_back` | Flat back. |
| `sway_back` | Sway back. |
| `stooped` | Stooped. |
| `scoliotic` | Scoliotic. |
| `other` | Another posture. |

**`gait`** — Gait

| Term | Meaning |
|---|---|
| `brisk` | Brisk. |
| `average` | Average. |
| `slow` | Slow. |
| `shuffling` | Shuffling. |
| `limping` | Limping. |
| `waddling` | Waddling. |
| `unsteady` | Unsteady. |
| `stiff` | Stiff. |
| `other` | Another gait. |

#### 5.2.3 Example

```json
{
  "morphology": {
    "height": [
      { "value": 172, "date": { "value": "1914", "precision": "year" },
        "source_id": "9b2f0d1e-3c4a-4b5d-8e6f-7a8b9c0d1e2f", "confidence": 0.9,
        "note": "Register: 5 ft 7¾ in." },
      { "value": 169, "date": { "value": "1950", "precision": "year" }, "confidence": 0.8 }
    ],
    "build": [ { "value": "sturdy", "date": { "value": "1914", "precision": "year" }, "confidence": 0.9 } ],
    "eye_colour": [ { "value": "grey", "confidence": 0.9 } ],
    "hair_colour": [
      { "value": "dark_brown", "date": { "value": "1914", "precision": "year" }, "confidence": 0.9 },
      { "value": "grey", "date": { "value": "1950", "precision": "year" }, "confidence": 0.8 }
    ],
    "skin_tone": { "value": "type_iii", "confidence": 0.5 },
    "scars": [ { "value": { "description": "Sabre cut along the jaw", "body_region": "face" }, "confidence": 0.9 } ],
    "tattoos": [ { "value": { "description": "Anchor", "body_region": "left_arm" }, "confidence": 0.9 } ]
  }
}
```

### 5.3 Biometrics

What identifies a person by body and voice, and how they spoke, saw and heard.

Templates and images — fingerprints, retinal prints, voiceprints — are artefact references (§3.5.1): the Document holds the file. Their measures (`voice_frequency`, `speech_rate`) and `vocal_timbre` share their class. How somebody spoke — accent, tics, vocabulary, register — is ordinary genealogy and has no class. Hearing, sight and motor tics are health data, and are in `health` even though they sit in this group.

#### 5.3.1 Attributes

Block: `biometrics` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Fingerprints | `biometrics.fingerprints` | series | artefact: `fingerprint_card`, `fingerprint_template` | `biometrics` |
| Retinal print | `biometrics.retinal_print` | series | artefact: `retinal_image` | `biometrics` |
| Voice signature | `biometrics.voice_signature` | series | artefact: `voiceprint` | `biometrics` |
| Fundamental voice frequency | `biometrics.voice_frequency` | series | number (Hz, 30–1100) | `biometrics` |
| Vocal timbre | `biometrics.vocal_timbre` | series | **vocal_timbre** | `biometrics` |
| Spoken accent | `biometrics.spoken_accent` | series | `language` language_tag; `description?` text | — |
| Speech rate | `biometrics.speech_rate` | series | number (words/min, 10–600) | `biometrics` |
| Verbal tics | `biometrics.verbal_tics` | series | text | — |
| Frequent vocabulary | `biometrics.frequent_vocabulary` | series | text | — |
| Register of speech | `biometrics.speech_register` | series | **speech_register** | — |
| Motor tics | `biometrics.motor_tics` | series | text | `health` |
| Handedness | `biometrics.handedness` | series | **handedness** | — |
| Hearing capacity | `biometrics.hearing` | series | `ear?` **laterality**; `grade` **hearing_grade**; `threshold_db?` number (dB HL, -10–130) | `health` |
| Visual acuity | `biometrics.visual_acuity` | series | `eye` **laterality**; `decimal` number (0–2.5); `corrected?` boolean | `health` |
| Optical correction | `biometrics.optical_correction` | series | `kind` **optical_correction**; `prescription?` text | `health` |

- **`biometrics.fingerprints`** — A reference to a Document.
- **`biometrics.retinal_print`** — A reference to a Document.
- **`biometrics.voice_signature`** — A reference to a Document.
- **`biometrics.voice_frequency`** — Mean fundamental frequency, hertz.
- **`biometrics.spoken_accent`** — A language tag with a region where it helps (`pl-PL`), and a description.
- **`biometrics.speech_rate`** — Words per minute.
- **`biometrics.verbal_tics`** — Free text.
- **`biometrics.frequent_vocabulary`** — Free text.
- **`biometrics.motor_tics`** — Free text.
- **`biometrics.handedness`** — A series: a left-handed child retrained to the right is two facts.
- **`biometrics.visual_acuity`** — Decimal acuity: 20/20 is 1.0, 6/12 is 0.5.

#### 5.3.2 Vocabularies

**`vocal_timbre`** — Vocal timbre

| Term | Meaning |
|---|---|
| `bright` | Bright. |
| `dark` | Dark. |
| `warm` | Warm. |
| `breathy` | Breathy. |
| `nasal` | Nasal. |
| `hoarse` | Hoarse. |
| `resonant` | Resonant. |
| `thin` | Thin. |
| `other` | Another timbre. |

**`speech_register`** — Register of speech. *Joos, M. (1961), The Five Clocks.*

| Term | Meaning |
|---|---|
| `frozen` | Frozen: fixed, ceremonial language. |
| `formal` | Formal: careful, one-way, complete. |
| `consultative` | Consultative: the ordinary register between people who do not know each other well. |
| `casual` | Casual: among friends; ellipsis and slang. |
| `intimate` | Intimate: private language between people very close. |

**`handedness`** — Handedness

| Term | Meaning |
|---|---|
| `left` | Left-handed. |
| `right` | Right-handed. |
| `ambidextrous` | Ambidextrous. |
| `mixed` | Different hands for different tasks. |
| `unknown` | Not known. |

**`hearing_grade`** — Hearing grade. *World Health Organization (2021), World report on hearing.*

| Term | Meaning |
|---|---|
| `normal` | Normal: under 20 dB in the better ear. |
| `mild` | Mild: 20 to under 35 dB. |
| `moderate` | Moderate: 35 to under 50 dB. |
| `moderately_severe` | Moderately severe: 50 to under 65 dB. |
| `severe` | Severe: 65 to under 80 dB. |
| `profound` | Profound: 80 to under 95 dB. |
| `complete` | Complete or total: 95 dB or more. |

**`optical_correction`** — Optical correction

| Term | Meaning |
|---|---|
| `none` | None. |
| `glasses` | Glasses. |
| `contact_lenses` | Contact lenses. |
| `glasses_and_contact_lenses` | Glasses and contact lenses. |
| `refractive_surgery` | Refractive surgery. |
| `intraocular_lens` | Intraocular lens. |
| `other` | Another correction. |

#### 5.3.3 Example

```json
{
  "biometrics": {
    "fingerprints": [
      { "value": { "document_id": "0f8fad5b-d9cb-469f-a165-70867728950e",
                   "artefact_type": "fingerprint_card", "format": "TIFF" },
        "date": { "value": "1946-02", "precision": "month" },
        "source_id": "7c9e6679-7425-40de-944b-e07fc1f90ae8", "confidence": 0.99 }
    ],
    "spoken_accent": [ { "value": { "language": "pl-PL", "description": "Lwów" }, "confidence": 0.8 } ],
    "speech_register": [ { "value": "consultative", "confidence": 0.6 } ],
    "handedness": [
      { "value": "left", "date": { "value": "1920", "precision": "decade" }, "confidence": 0.7 },
      { "value": "right", "date": { "value": "1935", "precision": "year" }, "confidence": 0.7,
        "note": "Retrained at school." }
    ],
    "hearing": [ { "value": { "ear": "left", "grade": "moderate", "threshold_db": 42 },
                   "date": { "value": "1971", "precision": "year" }, "confidence": 0.9 } ]
  }
}
```

### 5.4 Health

Constitution, conditions, treatment and results. Every attribute in this group is `health`.

**One series of conditions.** Chronic pathologies, diagnosed chronic illnesses, cardiovascular, respiratory, metabolic and endocrine pathologies, autoimmune and oncological disease, and psychiatric and neurodevelopmental conditions are all `conditions`: one entry per condition, with its `icd10_chapter`, whether it is `chronic` or `autoimmune`, and how it was established. The categories overlap — an autoimmune thyroiditis is endocrine and chronic — and a separate list for each would put one diagnosis in three places. A reader asks for the circulatory conditions by filtering on the chapter.

| Attribute as commonly named | Where |
|---|---|
| chronic pathologies | `conditions` with `chronic: true` |
| diagnosed chronic illnesses | `conditions` with `chronic: true` and `diagnosis: diagnosed` |
| cardiovascular pathologies | `conditions` with `icd10_chapter: circulatory` |
| respiratory pathologies | `conditions` with `icd10_chapter: respiratory` |
| metabolic and endocrine pathologies | `conditions` with `icd10_chapter: endocrine_metabolic` |
| autoimmune diseases | `conditions` with `autoimmune: true` |
| oncological pathologies | `conditions` with `icd10_chapter: neoplasms` |
| psychiatric and neurodevelopmental conditions | `conditions` with `icd10_chapter: mental_behavioural` |
| drug, food and environmental allergies | `allergies` with `type` drug, food or environmental |
| basic metabolic, lipid, liver and renal panels, HbA1c, iron metabolism | `lab_results` with `panel` |

**Laboratory results** are one claim per analyte, so each carries its own unit, range and flag, and a panel is the claims that share a date, a panel and a source. The analytes each panel may contain:

| Panel | Analytes |
|---|---|
| `basic_metabolic` | `sodium`, `potassium`, `chloride`, `bicarbonate`, `urea`, `creatinine`, `glucose`, `calcium` |
| `lipid` | `total_cholesterol`, `ldl_cholesterol`, `hdl_cholesterol`, `triglycerides`, `non_hdl_cholesterol` |
| `liver` | `alt`, `ast`, `alp`, `ggt`, `total_bilirubin`, `direct_bilirubin`, `albumin`, `total_protein` |
| `renal` | `creatinine`, `urea`, `egfr`, `uric_acid`, `phosphate`, `urine_albumin_creatinine_ratio` |
| `glycated_haemoglobin` | `hba1c` |
| `iron` | `serum_iron`, `ferritin`, `transferrin`, `transferrin_saturation`, `tibc` |

Units are UCUM codes (§3.4). Where the source gives a conventional unit, record it; do not convert a laboratory result, because the reference range printed beside it is in the source's unit.

#### 5.4.1 Attributes

Block: `health` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Blood group | `health.blood_group` | single | **blood_group** | `health` |
| Rhesus | `health.rhesus` | single | **rhesus** | `health` |
| Mean blood pressure | `health.blood_pressure` | series | `systolic` integer (mmHg, 40–300); `diastolic` integer (mmHg, 20–200) | `health` |
| Resting heart rate | `health.resting_heart_rate` | series | integer (bpm, 20–250) | `health` |
| Respiratory capacity (FEV1/FVC) | `health.respiratory_capacity` | series | `fev1_litres?` number (L, 0–10); `fvc_litres?` number (L, 0–12); `fev1_fvc_ratio?` number (0–1); one of: `fev1_litres` or `fvc_litres` or `fev1_fvc_ratio` | `health` |
| Chronic pathologies; diagnosed chronic illnesses; cardiovascular, respiratory, metabolic and endocrine pathologies; autoimmune diseases; oncological pathologies; psychiatric and neurodevelopmental conditions | `health.conditions` | series | `description` text; `icd10_chapter?` **icd10_chapter**; `chronic?` boolean; `autoimmune?` boolean; `diagnosis?` **diagnosis_status** | `health` |
| Surgical history | `health.surgeries` | series | `description` text; `body_region?` **body_region** | `health` |
| Trauma and fracture sequelae | `health.injuries` | series | `description` text; `body_region?` **body_region**; `fracture?` boolean | `health` |
| Physical deformities | `health.deformities` | series | `description` text; `body_region?` **body_region**; `congenital?` boolean | `health` |
| Amputations | `health.amputations` | series | `body_region` **body_region**; `level?` text; `cause?` text | `health` |
| Prostheses | `health.prostheses` | series | `kind` **prosthesis_kind**; `description?` text | `health` |
| Biomedical implants | `health.implants` | series | `kind` **implant_kind**; `description?` text | `health` |
| Pacemakers and intracorporeal devices | `health.devices` | series | `kind` **device_kind**; `description?` text | `health` |
| Long-term medication | `health.medications` | series | `substance` text; `dose?` text; `indication?` text | `health` |
| Drug allergies; food allergies; environmental allergies | `health.allergies` | series | `type` **allergy_type**; `allergen` text; `severity?` **allergy_severity**; `reaction?` text | `health` |
| Vaccination status | `health.vaccinations` | series | `pathogen` **pathogen**; `status` **vaccination_status**; `dose?` integer (1–20) | `health` |
| Serology status | `health.serology` | series | `pathogen` **pathogen**; `result` **serology_result** | `health` |
| Basic metabolic panel; lipid panel; liver panel; renal panel; HbA1c; iron metabolism | `health.lab_results` | series | `panel` **lab_panel**; `analyte` **lab_analyte**; `result` number; `unit` **lab_unit**; `reference_low?` number; `reference_high?` number; `flag?` **lab_flag** | `health` |
| Vitamin and mineral deficiencies | `health.deficiencies` | series | `nutrient` **nutrient**; `description?` text | `health` |
| Sleep disorders | `health.sleep_disorders` | series | `category` **sleep_disorder**; `description?` text | `health` |
| Mental health assessment | `health.mental_health_assessments` | series | `instrument` **assessment_instrument**; `score?` number (0–1000); `severity?` **assessment_severity**; `summary?` text | `health` |

- **`health.blood_pressure`** — Millimetres of mercury; the mean of a session's readings where there were several.
- **`health.resting_heart_rate`** — Beats per minute.
- **`health.respiratory_capacity`** — At least one.
- **`health.conditions`** — One series for every condition, categorised by ICD-10 chapter; see Appendix A.5.
- **`health.surgeries`** — Free text.
- **`health.devices`** — Worth recording for its own sake: a pacemaker has to be removed before cremation.
- **`health.medications`** — The period goes in `valid_from` / `valid_until`.
- **`health.lab_results`** — One claim per analyte; a panel drawn on one day is several claims sharing a date and a source.

#### 5.4.2 Vocabularies

**`blood_group`** — Blood group (ABO). *ISBT ABO blood group system.*

| Term | Meaning |
|---|---|
| `A` | Group A. |
| `B` | Group B. |
| `AB` | Group AB. |
| `O` | Group O. |

**`rhesus`** — Rhesus (RhD). *ISBT Rh blood group system.*

| Term | Meaning |
|---|---|
| `positive` | RhD positive. |
| `negative` | RhD negative. |
| `weak_d` | Weak D. |
| `unknown` | Tested but not determined, or not known. |

**`icd10_chapter`** — ICD-10 chapter. *WHO International Statistical Classification of Diseases and Related Health Problems, 10th revision.*

| Term | Meaning |
|---|---|
| `infectious_parasitic` | I (A00–B99): certain infectious and parasitic diseases. |
| `neoplasms` | II (C00–D48): neoplasms. |
| `blood_immune` | III (D50–D89): diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism. |
| `endocrine_metabolic` | IV (E00–E90): endocrine, nutritional and metabolic diseases. |
| `mental_behavioural` | V (F00–F99): mental and behavioural disorders, including neurodevelopmental disorders. |
| `nervous_system` | VI (G00–G99): diseases of the nervous system. |
| `eye_adnexa` | VII (H00–H59): diseases of the eye and adnexa. |
| `ear_mastoid` | VIII (H60–H95): diseases of the ear and mastoid process. |
| `circulatory` | IX (I00–I99): diseases of the circulatory system. |
| `respiratory` | X (J00–J99): diseases of the respiratory system. |
| `digestive` | XI (K00–K93): diseases of the digestive system. |
| `skin` | XII (L00–L99): diseases of the skin and subcutaneous tissue. |
| `musculoskeletal` | XIII (M00–M99): diseases of the musculoskeletal system and connective tissue. |
| `genitourinary` | XIV (N00–N99): diseases of the genitourinary system. |
| `pregnancy_childbirth` | XV (O00–O99): pregnancy, childbirth and the puerperium. |
| `perinatal` | XVI (P00–P96): certain conditions originating in the perinatal period. |
| `congenital` | XVII (Q00–Q99): congenital malformations, deformations and chromosomal abnormalities. |
| `ill_defined` | XVIII (R00–R99): symptoms, signs and abnormal findings not elsewhere classified — including old age and unknown causes. |
| `injury_poisoning` | XIX (S00–T98): injury, poisoning and certain other consequences of external causes. |
| `external_causes` | XX (V01–Y98): external causes of morbidity and mortality. |
| `health_factors` | XXI (Z00–Z99): factors influencing health status and contact with health services. |
| `special_purposes` | XXII (U00–U85): codes for special purposes. |

**`diagnosis_status`** — Diagnosis status

| Term | Meaning |
|---|---|
| `diagnosed` | Diagnosed by a clinician. |
| `suspected` | Suspected but not confirmed. |
| `self_reported` | Reported by the person or their family. |
| `unknown` | How it was established is not known. |

**`prosthesis_kind`** — Prosthesis

| Term | Meaning |
|---|---|
| `limb` | A limb or part of a limb. |
| `joint` | A joint replacement. |
| `ocular` | An ocular prosthesis. |
| `dental` | A dental prosthesis. |
| `auditory` | An auditory prosthesis. |
| `breast` | A breast prosthesis. |
| `other` | Another prosthesis. |

**`implant_kind`** — Biomedical implant

| Term | Meaning |
|---|---|
| `orthopaedic` | Orthopaedic hardware: plates, screws, rods. |
| `dental` | A dental implant. |
| `cochlear` | A cochlear implant. |
| `breast` | A breast implant. |
| `intraocular_lens` | An intraocular lens. |
| `contraceptive` | A contraceptive implant. |
| `cosmetic` | A cosmetic implant. |
| `other` | Another implant. |

**`device_kind`** — Intracorporeal device

| Term | Meaning |
|---|---|
| `pacemaker` | A cardiac pacemaker. |
| `implantable_defibrillator` | An implantable cardioverter-defibrillator. |
| `cardiac_resynchronisation` | A cardiac resynchronisation device. |
| `ventricular_assist` | A ventricular assist device. |
| `neurostimulator` | A neurostimulator. |
| `insulin_pump` | An implanted insulin pump. |
| `drug_port` | An implanted drug delivery port. |
| `shunt` | A shunt. |
| `stent` | A stent. |
| `other` | Another device. |

**`allergy_type`** — Allergy type

| Term | Meaning |
|---|---|
| `drug` | A drug. |
| `food` | A food. |
| `environmental` | Something in the environment: pollen, dust, animals, mould. |
| `insect_venom` | Insect venom. |
| `latex` | Latex. |
| `other` | Another allergen. |

**`allergy_severity`** — Allergy severity

| Term | Meaning |
|---|---|
| `mild` | Mild. |
| `moderate` | Moderate. |
| `severe` | Severe. |
| `anaphylactic` | Anaphylactic. |
| `unknown` | Not known. |

**`pathogen`** — Pathogen or vaccine target

| Term | Meaning |
|---|---|
| `diphtheria` | Diphtheria. |
| `tetanus` | Tetanus. |
| `pertussis` | Pertussis. |
| `poliomyelitis` | Poliomyelitis. |
| `measles` | Measles. |
| `mumps` | Mumps. |
| `rubella` | Rubella. |
| `varicella` | Varicella. |
| `smallpox` | Smallpox. |
| `tuberculosis` | Tuberculosis. |
| `hepatitis_a` | Hepatitis A. |
| `hepatitis_b` | Hepatitis B. |
| `hepatitis_c` | Hepatitis C. |
| `haemophilus_influenzae_b` | Haemophilus influenzae type b. |
| `pneumococcal` | Pneumococcal disease. |
| `meningococcal` | Meningococcal disease. |
| `human_papillomavirus` | Human papillomavirus. |
| `influenza` | Influenza. |
| `covid_19` | COVID-19. |
| `rotavirus` | Rotavirus. |
| `yellow_fever` | Yellow fever. |
| `typhoid` | Typhoid. |
| `cholera` | Cholera. |
| `rabies` | Rabies. |
| `japanese_encephalitis` | Japanese encephalitis. |
| `tick_borne_encephalitis` | Tick-borne encephalitis. |
| `hiv` | HIV. |
| `syphilis` | Syphilis. |
| `toxoplasmosis` | Toxoplasmosis. |
| `cytomegalovirus` | Cytomegalovirus. |
| `epstein_barr` | Epstein–Barr virus. |
| `other` | Another pathogen. |

**`vaccination_status`** — Vaccination status

| Term | Meaning |
|---|---|
| `vaccinated` | Vaccinated, with the full course for that target. |
| `partially_vaccinated` | Vaccinated, course incomplete. |
| `unvaccinated` | Not vaccinated. |
| `contraindicated` | Not vaccinated because of a contraindication. |
| `unknown` | Not known. |

**`serology_result`** — Serology result

| Term | Meaning |
|---|---|
| `positive` | Antibodies detected. |
| `negative` | Antibodies not detected. |
| `equivocal` | Equivocal. |
| `unknown` | Not known. |

**`lab_panel`** — Laboratory panel

| Term | Meaning |
|---|---|
| `basic_metabolic` | Basic metabolic panel. |
| `lipid` | Lipid panel. |
| `liver` | Liver panel. |
| `renal` | Renal panel. |
| `glycated_haemoglobin` | Glycated haemoglobin (HbA1c). |
| `iron` | Iron metabolism. |

**`lab_analyte`** — Laboratory analyte

| Term | Meaning |
|---|---|
| `sodium` | Sodium. |
| `potassium` | Potassium. |
| `chloride` | Chloride. |
| `bicarbonate` | Bicarbonate. |
| `urea` | Urea (blood urea nitrogen). |
| `creatinine` | Creatinine. |
| `glucose` | Glucose. |
| `calcium` | Calcium. |
| `total_cholesterol` | Total cholesterol. |
| `ldl_cholesterol` | LDL cholesterol. |
| `hdl_cholesterol` | HDL cholesterol. |
| `triglycerides` | Triglycerides. |
| `non_hdl_cholesterol` | Non-HDL cholesterol. |
| `alt` | Alanine aminotransferase. |
| `ast` | Aspartate aminotransferase. |
| `alp` | Alkaline phosphatase. |
| `ggt` | Gamma-glutamyl transferase. |
| `total_bilirubin` | Total bilirubin. |
| `direct_bilirubin` | Direct bilirubin. |
| `albumin` | Albumin. |
| `total_protein` | Total protein. |
| `egfr` | Estimated glomerular filtration rate. |
| `uric_acid` | Uric acid. |
| `phosphate` | Phosphate. |
| `urine_albumin_creatinine_ratio` | Urine albumin-to-creatinine ratio. |
| `hba1c` | Glycated haemoglobin. |
| `serum_iron` | Serum iron. |
| `ferritin` | Ferritin. |
| `transferrin` | Transferrin. |
| `transferrin_saturation` | Transferrin saturation. |
| `tibc` | Total iron-binding capacity. |

**`lab_unit`** — Laboratory unit (UCUM). *Unified Code for Units of Measure.*

| Term | Meaning |
|---|---|
| `mmol/L` | Millimoles per litre. |
| `umol/L` | Micromoles per litre. |
| `mg/dL` | Milligrams per decilitre. |
| `g/L` | Grams per litre. |
| `g/dL` | Grams per decilitre. |
| `U/L` | Units per litre. |
| `%` | Per cent. |
| `mmol/mol` | Millimoles per mole. |
| `ug/L` | Micrograms per litre. |
| `ug/dL` | Micrograms per decilitre. |
| `ng/mL` | Nanograms per millilitre. |
| `mL/min/{1.73_m2}` | Millilitres per minute per 1.73 m² of body surface. |
| `mg/mmol` | Milligrams per millimole. |
| `mg/g` | Milligrams per gram. |

**`lab_flag`** — Laboratory flag

| Term | Meaning |
|---|---|
| `low` | Below the reference range. |
| `normal` | Within the reference range. |
| `high` | Above the reference range. |
| `critical_low` | Critically low. |
| `critical_high` | Critically high. |

**`nutrient`** — Nutrient

| Term | Meaning |
|---|---|
| `vitamin_a` | Vitamin A. |
| `thiamine` | Thiamine (vitamin B1). |
| `riboflavin` | Riboflavin (vitamin B2). |
| `niacin` | Niacin (vitamin B3). |
| `vitamin_b6` | Vitamin B6. |
| `folate` | Folate (vitamin B9). |
| `vitamin_b12` | Vitamin B12. |
| `vitamin_c` | Vitamin C. |
| `vitamin_d` | Vitamin D. |
| `vitamin_e` | Vitamin E. |
| `vitamin_k` | Vitamin K. |
| `iron` | Iron. |
| `zinc` | Zinc. |
| `magnesium` | Magnesium. |
| `calcium` | Calcium. |
| `iodine` | Iodine. |
| `selenium` | Selenium. |
| `copper` | Copper. |
| `potassium` | Potassium. |
| `phosphorus` | Phosphorus. |
| `other` | Another nutrient. |

**`sleep_disorder`** — Sleep disorder category. *American Academy of Sleep Medicine, International Classification of Sleep Disorders, 3rd edition.*

| Term | Meaning |
|---|---|
| `insomnia` | Insomnia. |
| `sleep_related_breathing` | Sleep-related breathing disorders. |
| `central_hypersomnolence` | Central disorders of hypersomnolence. |
| `circadian_rhythm` | Circadian rhythm sleep-wake disorders. |
| `parasomnia` | Parasomnias. |
| `sleep_related_movement` | Sleep-related movement disorders. |
| `other` | Other sleep disorders. |

**`assessment_instrument`** — Assessment instrument

| Term | Meaning |
|---|---|
| `phq_9` | Patient Health Questionnaire-9 (depression). |
| `gad_7` | Generalized Anxiety Disorder-7. |
| `bdi_ii` | Beck Depression Inventory-II. |
| `hads` | Hospital Anxiety and Depression Scale. |
| `k10` | Kessler Psychological Distress Scale. |
| `gds_15` | Geriatric Depression Scale, short form. |
| `mmse` | Mini-Mental State Examination. |
| `moca` | Montreal Cognitive Assessment. |
| `audit` | Alcohol Use Disorders Identification Test. |
| `clinical_interview` | A clinical interview, no scored instrument. |
| `other` | Another instrument. |

**`assessment_severity`** — Assessment severity

| Term | Meaning |
|---|---|
| `none_minimal` | None or minimal. |
| `mild` | Mild. |
| `moderate` | Moderate. |
| `moderately_severe` | Moderately severe. |
| `severe` | Severe. |

#### 5.4.3 Example

```json
{
  "health": {
    "blood_group": { "value": "O", "source_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f", "confidence": 0.95 },
    "rhesus": { "value": "positive", "source_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f", "confidence": 0.95 },
    "conditions": [
      { "value": { "description": "Tuberculosis", "icd10_chapter": "infectious_parasitic",
                   "diagnosis": "diagnosed" },
        "valid_from": { "date": { "value": "1947", "precision": "year" } },
        "valid_until": { "date": { "value": "1949", "precision": "year" } }, "confidence": 0.8 }
    ],
    "devices": [ { "value": { "kind": "pacemaker" },
                   "date": { "value": "1994-10", "precision": "month" }, "confidence": 0.95 } ],
    "lab_results": [
      { "value": { "panel": "lipid", "analyte": "ldl_cholesterol", "result": 3.9, "unit": "mmol/L",
                   "reference_high": 3.0, "flag": "high" },
        "date": { "value": "1993-05-04", "precision": "exact" }, "confidence": 0.99 },
      { "value": { "panel": "lipid", "analyte": "hdl_cholesterol", "result": 1.1, "unit": "mmol/L",
                   "reference_low": 1.0, "flag": "normal" },
        "date": { "value": "1993-05-04", "precision": "exact" }, "confidence": 0.99 }
    ]
  }
}
```

### 5.5 Genomics

What tests of DNA and of its environment found. Every attribute in this group is `genomics`, and a deceased person's genomic data is never public (§4.3).

Raw data, sequences and reports are Documents, referenced by `document_id`. Haplogroups are half closed (Appendix A.11): the major clade is a vocabulary, the subclade a pattern that must begin with it — ISOGG shorthand (`R-M269`) or longhand (`R1b1a1b`) for Y-DNA, PhyloTree notation (`H1a1`) for mtDNA.

#### 5.5.1 Attributes

Block: `genomics` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Autosomal DNA mapping | `genomics.autosomal_mapping` | series | `provider?` text; `test?` text; `reference_build?` **reference_build**; `snp_count?` integer (1–100000000); `document_id?` uuid | `genomics` |
| Y haplogroup | `genomics.y_haplogroup` | single | `major` **y_haplogroup**; `subclade?` pattern `y_subclade`; `tree_version?` text | `genomics` |
| Mitochondrial haplogroup | `genomics.mt_haplogroup` | single | `major` **mt_haplogroup**; `subclade?` pattern `mt_subclade`; `tree_version?` text | `genomics` |
| Whole genome sequencing | `genomics.whole_genome_sequencing` | series | `provider?` text; `coverage?` number (x, 0–10000); `reference_build?` **reference_build**; `file_format?` **genomic_file_format**; `document_id?` uuid | `genomics` |
| Risk variants | `genomics.risk_variants` | series | `variant` text; `gene?` text; `zygosity?` **zygosity**; `significance?` **clinical_significance**; `condition?` text | `genomics` |
| Hereditary pathologies | `genomics.hereditary_conditions` | series | `description` text; `inheritance?` **inheritance_pattern**; `carrier_status?` **carrier_status** | `genomics` |
| Genetic predispositions | `genomics.predispositions` | series | `description` text; `polygenic_score?` number; `percentile?` number (0–100) | `genomics` |
| Epigenetic markers | `genomics.epigenetic_markers` | series | `description` text; `marker?` text | `genomics` |
| Epigenetic biological age | `genomics.epigenetic_age` | series | `clock` **epigenetic_clock**; `age_years?` number (years, 0–200); `pace?` number (0–5); one of: `age_years` or `pace` | `genomics` |
| Gut microbiome | `genomics.gut_microbiome` | series | `provider?` text; `shannon_diversity?` number (0–20); `summary?` text; `document_id?` uuid | `genomics` |
| Skin microbiome | `genomics.skin_microbiome` | series | `provider?` text; `shannon_diversity?` number (0–20); `summary?` text; `document_id?` uuid | `genomics` |
| Toxicological sensitivities | `genomics.toxicological_sensitivities` | series | `substance` text; `gene?` text; `metaboliser_status?` **metaboliser_status**; `description?` text | `genomics` |

- **`genomics.autosomal_mapping`** — The raw data or chromosome map is a Document.
- **`genomics.y_haplogroup`** — ISOGG nomenclature; see Appendix A.11.
- **`genomics.mt_haplogroup`** — PhyloTree nomenclature, as ISOGG uses; see Appendix A.11.
- **`genomics.risk_variants`** — The variant in HGVS notation or as an rsID; the gene as its HGNC symbol.
- **`genomics.epigenetic_age`** — `pace` for DunedinPACE, `age_years` for every other clock.

#### 5.5.2 Vocabularies

**`reference_build`** — Reference genome build. *Genome Reference Consortium; Telomere-to-Telomere Consortium.*

| Term | Meaning |
|---|---|
| `grch36` | GRCh36 (hg18). |
| `grch37` | GRCh37 (hg19). |
| `grch38` | GRCh38 (hg38). |
| `t2t_chm13` | T2T-CHM13. |

**`y_haplogroup`** — Y-DNA major haplogroup. *ISOGG Y-DNA Haplogroup Tree.*

| Term | Meaning |
|---|---|
| `A` | Haplogroup A. |
| `B` | Haplogroup B. |
| `C` | Haplogroup C. |
| `D` | Haplogroup D. |
| `E` | Haplogroup E. |
| `F` | Haplogroup F. |
| `G` | Haplogroup G. |
| `H` | Haplogroup H. |
| `I` | Haplogroup I. |
| `J` | Haplogroup J. |
| `K` | Haplogroup K. |
| `L` | Haplogroup L. |
| `M` | Haplogroup M. |
| `N` | Haplogroup N. |
| `O` | Haplogroup O. |
| `P` | Haplogroup P. |
| `Q` | Haplogroup Q. |
| `R` | Haplogroup R. |
| `S` | Haplogroup S. |
| `T` | Haplogroup T. |

**`mt_haplogroup`** — mtDNA major haplogroup. *PhyloTree (the mtDNA nomenclature ISOGG adopts).*

| Term | Meaning |
|---|---|
| `L0` | Haplogroup L0. |
| `L1` | Haplogroup L1. |
| `L2` | Haplogroup L2. |
| `L3` | Haplogroup L3. |
| `L4` | Haplogroup L4. |
| `L5` | Haplogroup L5. |
| `L6` | Haplogroup L6. |
| `M` | Haplogroup M. |
| `N` | Haplogroup N. |
| `R` | Haplogroup R. |
| `A` | Haplogroup A. |
| `B` | Haplogroup B. |
| `C` | Haplogroup C. |
| `D` | Haplogroup D. |
| `E` | Haplogroup E. |
| `F` | Haplogroup F. |
| `G` | Haplogroup G. |
| `H` | Haplogroup H. |
| `HV` | Haplogroup HV. |
| `I` | Haplogroup I. |
| `J` | Haplogroup J. |
| `K` | Haplogroup K. |
| `O` | Haplogroup O. |
| `P` | Haplogroup P. |
| `Q` | Haplogroup Q. |
| `S` | Haplogroup S. |
| `T` | Haplogroup T. |
| `U` | Haplogroup U. |
| `V` | Haplogroup V. |
| `W` | Haplogroup W. |
| `X` | Haplogroup X. |
| `Y` | Haplogroup Y. |
| `Z` | Haplogroup Z. |

**`genomic_file_format`** — Genomic file format

| Term | Meaning |
|---|---|
| `raw_microarray` | A genotyping chip's raw data export. |
| `fastq` | FASTQ reads. |
| `bam` | BAM alignments. |
| `cram` | CRAM alignments. |
| `vcf` | VCF variants. |
| `gvcf` | gVCF variants. |
| `other` | Another format. |

**`zygosity`** — Zygosity

| Term | Meaning |
|---|---|
| `heterozygous` | Heterozygous. |
| `homozygous` | Homozygous. |
| `hemizygous` | Hemizygous. |
| `compound_heterozygous` | Compound heterozygous. |

**`clinical_significance`** — Clinical significance. *Richards et al. (2015), ACMG/AMP standards for the interpretation of sequence variants.*

| Term | Meaning |
|---|---|
| `pathogenic` | Pathogenic. |
| `likely_pathogenic` | Likely pathogenic. |
| `uncertain_significance` | Of uncertain significance. |
| `likely_benign` | Likely benign. |
| `benign` | Benign. |

**`inheritance_pattern`** — Inheritance pattern

| Term | Meaning |
|---|---|
| `autosomal_dominant` | Autosomal dominant. |
| `autosomal_recessive` | Autosomal recessive. |
| `x_linked_dominant` | X-linked dominant. |
| `x_linked_recessive` | X-linked recessive. |
| `y_linked` | Y-linked. |
| `mitochondrial` | Mitochondrial. |
| `multifactorial` | Multifactorial. |
| `unknown` | Not known. |

**`carrier_status`** — Carrier status

| Term | Meaning |
|---|---|
| `affected` | Affected. |
| `carrier` | A carrier, unaffected. |
| `not_carrier` | Not a carrier. |
| `unknown` | Not known. |

**`epigenetic_clock`** — Epigenetic clock

| Term | Meaning |
|---|---|
| `horvath` | Horvath (2013), in years. |
| `hannum` | Hannum (2013), in years. |
| `phenoage` | PhenoAge (2018), in years. |
| `grimage` | GrimAge (2019), in years. |
| `dunedinpace` | DunedinPACE (2022), a pace: years of ageing per calendar year. |
| `other` | Another clock. |

**`metaboliser_status`** — Metaboliser status. *Clinical Pharmacogenetics Implementation Consortium (CPIC) standardised terms.*

| Term | Meaning |
|---|---|
| `poor` | Poor metaboliser. |
| `intermediate` | Intermediate metaboliser. |
| `normal` | Normal metaboliser. |
| `rapid` | Rapid metaboliser. |
| `ultrarapid` | Ultrarapid metaboliser. |

#### 5.5.3 Example

```json
{
  "genomics": {
    "y_haplogroup": { "value": { "major": "I", "subclade": "I-M253", "tree_version": "ISOGG 2020" },
                      "source_id": "d4e5f6a7-b8c9-4d0e-9f1a-2b3c4d5e6f7a", "confidence": 0.95 },
    "risk_variants": [
      { "value": { "variant": "NM_007294.4:c.5266dupC", "gene": "BRCA1", "zygosity": "heterozygous",
                   "significance": "pathogenic", "condition": "Hereditary breast and ovarian cancer" },
        "date": { "value": "2018-03", "precision": "month" }, "confidence": 0.99 }
    ],
    "epigenetic_age": [
      { "value": { "clock": "grimage", "age_years": 61.4 },
        "date": { "value": "2021-09", "precision": "month" }, "confidence": 0.9 },
      { "value": { "clock": "dunedinpace", "pace": 0.94 },
        "date": { "value": "2021-09", "precision": "month" }, "confidence": 0.9 }
    ],
    "toxicological_sensitivities": [
      { "value": { "substance": "codeine", "gene": "CYP2D6", "metaboliser_status": "ultrarapid" }, "confidence": 0.95 }
    ]
  }
}
```

### 5.6 Death

When, where and why a life ended, and what became of the body. It extends the 1.0 `death` block in place: `date`, `place_id`, `cause`, `confidence`, `source_id` and `event_id` keep their meaning, and 1.0's free-text `cause` stays valid beside `causes`.

`causes` follows the structure of a death certificate: `sequence` 1 is the immediate cause, 2 the condition that led to it, and so on; conditions that contributed without being in the chain are `contributing_factors`. Causes, factors and the autopsy are `health`. Time, place, disposition and grave are not: a grave is where a family goes, and publishing it is what genealogy is for.

#### 5.6.1 Attributes

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Death date | death.date | mapped | — | — |
| Death place | death.place_id | mapped | — | — |
| Death time | `death.time` | single | time_of_day | — |
| Death coordinates | `death.coordinates` | single | coordinates | — |
| Direct causes | `death.causes` | series | `description` text; `icd10_chapter?` **icd10_chapter**; `sequence?` integer (1–10) | `health` |
| Contributing factors | `death.contributing_factors` | series | `description` text; `icd10_chapter?` **icd10_chapter** | `health` |
| Autopsy and forensic report | `death.autopsy` | single | `kind` **autopsy**; `findings?` text; `document_id?` uuid | `health` |
| Burial or cremation place | `death.disposition` | series | `method` **disposition**; `place_id?` uuid | — |
| Grave coordinates | `death.grave` | series | `coordinates?` coordinates; `plot?` text; `inscription?` text; one of: `coordinates` or `plot` | — |

- **`death.time`** — Local time as recorded.
- **`death.causes`** — The chain on the certificate: sequence 1 is the immediate cause, higher numbers the conditions leading to it. 1.0's free-text `death.cause` stays valid and carries the same class.
- **`death.disposition`** — A series, because a body may be exhumed and reburied. The claim's date is the date of the disposition.
- **`death.grave`** — Where the grave is: a position, a plot reference, or both.

#### 5.6.2 Vocabularies

Also used here: `icd10_chapter` (§5.4).

**`autopsy`** — Autopsy

| Term | Meaning |
|---|---|
| `not_performed` | No autopsy was performed. |
| `clinical` | A clinical (hospital) autopsy. |
| `forensic` | A forensic (medico-legal) autopsy. |
| `external_examination` | An external examination only. |
| `unknown` | Not known. |

**`disposition`** — Disposition of the body

| Term | Meaning |
|---|---|
| `burial` | Burial. |
| `cremation` | Cremation. |
| `entombment` | Entombment. |
| `burial_at_sea` | Burial at sea. |
| `natural_burial` | Natural burial. |
| `body_donation` | Donation to science. |
| `other` | Another disposition. |
| `unknown` | Not known. |

#### 5.6.3 Example

```json
{
  "death": {
    "date": { "value": "1964-01-17", "precision": "exact" },
    "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "time": { "value": "04:10", "confidence": 0.9 },
    "causes": [
      { "value": { "description": "Pulmonary embolism", "icd10_chapter": "circulatory", "sequence": 1 }, "confidence": 0.9 },
      { "value": { "description": "Fracture of the neck of the femur", "icd10_chapter": "injury_poisoning", "sequence": 2 }, "confidence": 0.9 }
    ],
    "contributing_factors": [
      { "value": { "description": "Senile debility", "icd10_chapter": "ill_defined" }, "confidence": 0.6 }
    ],
    "autopsy": { "value": { "kind": "not_performed" }, "confidence": 0.8 },
    "disposition": [
      { "value": { "method": "burial", "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301" },
        "date": { "value": "1964-01-21", "precision": "exact" }, "confidence": 0.99 },
      { "value": { "method": "burial" }, "date": { "value": "1987", "precision": "year" },
        "confidence": 0.7, "note": "Moved to the family grave when the old cemetery was cleared." }
    ],
    "grave": [ { "value": { "plot": "Kwatera 3, rząd 11", "coordinates": { "lat": 50.0679, "lon": 19.9480 } },
                 "confidence": 0.9 } ]
  }
}
```

### 5.7 Residence and nationality

Where the person lived, which states counted them as nationals, and the languages they spoke.

**Addresses are one series.** The principal address and the chronological history are the same claims looked at two ways: every address carries its period, and the principal address at any date is the `use: principal` entry whose period covers it. A separate "principal address" field would repeat one of the history's entries and drift from it.

Countries are ISO codes, with 1.0's historical codes (§3.5); a place that belonged to a state with no code, such as Austria-Hungary, is recorded through its Place's `country_history` (1.0 §5.3), not here. `nationality_of_origin` is single; the nationalities a life acquired, and lost, are a series with their periods.

#### 5.7.1 Attributes

Block: `residence` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Principal address; chronological address history | `residence.addresses` | series | `use?` **address_use**; `lines?` text; `place_id?` uuid; `postal_code?` text; `country?` **country**; `coordinates?` coordinates; one of: `lines` or `place_id` | — |
| Nationality of origin | `residence.nationality_of_origin` | single | **country** | — |
| Acquired nationalities | `residence.acquired_nationalities` | series | `country` **country**; `mode?` **nationality_mode** | — |
| Mother tongue | `residence.mother_tongue` | series | language_tag | — |
| Spoken languages | `residence.spoken_languages` | series | `language` language_tag; `proficiency?` **language_proficiency** | — |

- **`residence.addresses`** — Every address, with its period. The principal address at any moment is the entry with `use: principal` whose period covers it.
- **`residence.acquired_nationalities`** — `valid_from` is when it was acquired, `valid_until` when it was lost or renounced.
- **`residence.mother_tongue`** — A series only because a child can have two first languages.

#### 5.7.2 Vocabularies

**`address_use`** — Address use

| Term | Meaning |
|---|---|
| `principal` | The principal residence, or domicile. |
| `secondary` | A secondary residence. |
| `temporary` | A temporary residence. |
| `postal` | An address for correspondence only. |
| `other` | Another use. |

**`nationality_mode`** — How a nationality was acquired

| Term | Meaning |
|---|---|
| `descent` | By descent from a national. |
| `birth_in_territory` | By birth in the territory. |
| `naturalisation` | By naturalisation. |
| `marriage` | By marriage. |
| `registration` | By registration or declaration. |
| `restoration` | By restoration of a nationality previously held. |
| `state_succession` | By a change of sovereignty over the place of residence. |
| `other` | Another way. |

**`language_proficiency`** — Language proficiency. *Council of Europe, Common European Framework of Reference for Languages.*

| Term | Meaning |
|---|---|
| `a1` | A1: breakthrough. |
| `a2` | A2: waystage. |
| `b1` | B1: threshold. |
| `b2` | B2: vantage. |
| `c1` | C1: effective operational proficiency. |
| `c2` | C2: mastery. |
| `native` | A first language. |

#### 5.7.3 Example

```json
{
  "residence": {
    "addresses": [
      { "value": { "use": "principal", "lines": "ul. Grodzka 12", "country": "PL",
                   "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301" },
        "valid_from": { "date": { "value": "1929", "precision": "year" } },
        "valid_until": { "date": { "value": "1946", "precision": "year" } }, "confidence": 0.8 },
      { "value": { "use": "principal", "lines": "14 rue des Lilas, Lille", "country": "FR" },
        "valid_from": { "date": { "value": "1946", "precision": "year" } }, "confidence": 0.9 }
    ],
    "nationality_of_origin": { "value": "PL", "confidence": 0.95 },
    "acquired_nationalities": [
      { "value": { "country": "FR", "mode": "naturalisation" },
        "valid_from": { "date": { "value": "1958-07-02", "precision": "exact" } }, "confidence": 0.99 }
    ],
    "mother_tongue": [ { "value": "pl", "confidence": 0.95 } ],
    "spoken_languages": [ { "value": { "language": "fr", "proficiency": "c1" }, "confidence": 0.8 } ]
  }
}
```

### 5.8 Education and work

What the person learned and how they made a living.

**Occupations stay entities.** 1.0 made an occupation a state with a start and an end, on an entity of its own (1.0 §4.5), and that is still where occupations held, and successive employers, are recorded. 1.1 adds `position` to Occupation for the post held, where `title` is the occupation itself: `title` "teacher", `position` "headmaster".

Education levels are ISCED 2011, which classifies a completed programme by its level regardless of country or era; the diploma's own name stays in `title`. Income is a quintile of the society at that time, which compares across a century, an amount with its currency and period, which does not, or both.

#### 5.8.1 Attributes

Block: `education` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Education level | `education.level` | series | **isced_level** | — |
| Diplomas | `education.diplomas` | series | `title` text; `isced_level?` **isced_level**; `institution?` text; `place_id?` uuid | — |
| Institutions attended | `education.institutions` | series | `name` text; `isced_level?` **isced_level**; `place_id?` uuid | — |
| Occupations held | Occupation entities with `person_id` (1.0 §4.5) | mapped | — | — |
| Positions | Occupation.position (new in 1.1) | mapped | — | — |
| Successive employers | Occupation.employer, ordered by `valid_from` (1.0 §4.5) | mapped | — | — |
| Average income level | `education.income` | series | `quintile?` **income_quintile**; `amount?` number (≥ 0); `currency?` currency_code; `period?` **pay_period**; one of: `quintile` or `amount` | — |
| Real estate holdings | `education.real_estate` | series | `description` text; `tenure?` **tenure**; `place_id?` uuid; `document_id?` uuid | — |

- **`education.level`** — The highest level completed as of the claim's date.
- **`education.institutions`** — The period goes in `valid_from` / `valid_until`.
- **Occupations held** — Unchanged: an occupation is a period, and an entity of its own.
- **Positions** — The post held, where `title` is the occupation: title "teacher", position "headmaster".
- **`education.income`** — A quintile of that society at that time, an amount, or both. An amount needs its currency and period to mean anything.

#### 5.8.2 Vocabularies

**`isced_level`** — Education level (ISCED 2011). *UNESCO Institute for Statistics, International Standard Classification of Education 2011.*

| Term | Meaning |
|---|---|
| `isced_0` | Level 0: early childhood education, or less than primary. |
| `isced_1` | Level 1: primary education. |
| `isced_2` | Level 2: lower secondary education. |
| `isced_3` | Level 3: upper secondary education. |
| `isced_4` | Level 4: post-secondary non-tertiary education. |
| `isced_5` | Level 5: short-cycle tertiary education. |
| `isced_6` | Level 6: bachelor's or equivalent. |
| `isced_7` | Level 7: master's or equivalent. |
| `isced_8` | Level 8: doctoral or equivalent. |

**`income_quintile`** — Income quintile

| Term | Meaning |
|---|---|
| `q1` | The lowest fifth of incomes in that society at that time. |
| `q2` | The second fifth. |
| `q3` | The middle fifth. |
| `q4` | The fourth fifth. |
| `q5` | The highest fifth. |

**`pay_period`** — Pay period

| Term | Meaning |
|---|---|
| `hourly` | Per hour. |
| `daily` | Per day. |
| `weekly` | Per week. |
| `monthly` | Per month. |
| `annual` | Per year. |

**`tenure`** — Tenure

| Term | Meaning |
|---|---|
| `owned` | Owned outright. |
| `co_owned` | Owned jointly. |
| `leasehold` | Held on a long lease. |
| `rented` | Rented. |
| `usufruct` | Held in usufruct. |
| `other` | Another form of tenure. |

#### 5.8.3 Example

```json
{
  "education": {
    "level": [ { "value": "isced_3", "date": { "value": "1938", "precision": "year" }, "confidence": 0.9 } ],
    "diplomas": [ { "value": { "title": "Świadectwo dojrzałości", "isced_level": "isced_3",
                               "institution": "Gimnazjum im. Stanisława Staszica" },
                    "date": { "value": "1938-06", "precision": "month" }, "confidence": 0.95 } ],
    "income": [ { "value": { "quintile": "q2", "amount": 180, "currency": "PLZ", "period": "monthly" },
                  "date": { "value": "1938", "precision": "year" }, "confidence": 0.5 } ],
    "real_estate": [ { "value": { "description": "Two hectares of arable land", "tenure": "owned" },
                       "valid_from": { "date": { "value": "1925", "precision": "year" } }, "confidence": 0.8 } ]
  }
}

{
  "id": "6fa459ea-ee8a-4ca4-894e-db77e160355e",
  "type": "occupation",
  "axgf_version": "1.1",
  "person_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "title": "Nauczyciel",
  "position": "Kierownik szkoły",
  "valid_from": { "date": { "value": "1951", "precision": "year" } },
  "confidence": 0.9
}
```

### 5.9 Military and honours

Service, rank and recognition, civil honours included.

**Ranks are national** (Appendix A.9). `military.ranks[].value.country` selects the vocabulary `rank` is drawn from; each registered rank has its title in its own language and a `category` that compares across armies. A rank in a country 1.1 does not register — or in an army that no longer exists — is `rank_text`, with its `category` if the recorder can give one. Registering a further country's vocabulary is an additive change for a later minor version.

#### 5.9.1 Attributes

Block: `military` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Honorific distinctions | `military.distinctions` | series | `name` text; `kind?` **distinction_kind**; `conferred_by?` text; `country?` **country** | — |
| Military citations | `military.citations` | series | `text` text; `unit?` text | — |
| Rank | `military.ranks` | series | `country?` **country**; `service?` **military_service**; `rank?` **military_rank_⟨country⟩**; `rank_text?` text; `category?` **rank_category**; one of: `rank` or `rank_text` | — |
| Regiment | `military.units` | series | text | — |
| Service number | `military.service_numbers` | series | `number` text; `service?` **military_service**; `country?` **country** | — |

- **`military.distinctions`** — Civil and military alike.
- **`military.ranks`** — `rank` from the vocabulary of `country`, which it then requires, when 1.1 registers one; otherwise `rank_text`, with `country` where the army has a code. See Appendix A.9.
- **`military.units`** — The unit's name as the source gives it.

#### 5.9.2 Vocabularies

**`distinction_kind`** — Distinction

| Term | Meaning |
|---|---|
| `order` | Membership of an order. |
| `decoration` | A decoration. |
| `medal` | A medal. |
| `title` | An honorific title. |
| `other` | Another distinction. |

**`military_service`** — Service

| Term | Meaning |
|---|---|
| `army` | Army. |
| `navy` | Navy. |
| `air_force` | Air force. |
| `marines` | Marines. |
| `gendarmerie` | Gendarmerie or military police. |
| `border_guard` | Border guard. |
| `national_guard` | National or territorial guard. |
| `other` | Another service. |

**`rank_category`** — Rank category

| Term | Meaning |
|---|---|
| `enlisted` | Enlisted rank. |
| `non_commissioned` | Non-commissioned officer. |
| `warrant` | Warrant officer, or its national equivalent. |
| `officer_cadet` | Officer cadet. |
| `junior_officer` | Junior officer. |
| `senior_officer` | Senior officer. |
| `general_officer` | General officer, one star and above. |

**`military_rank_fr`** — Armée de terre (France), selected by `country: "FR"`

| Term | Title | Category |
|---|---|---|
| `soldat_de_2e_classe` | Soldat de 2e classe | `enlisted` |
| `soldat_de_1re_classe` | Soldat de 1re classe | `enlisted` |
| `caporal` | Caporal | `enlisted` |
| `caporal_chef` | Caporal-chef | `enlisted` |
| `caporal_chef_de_1re_classe` | Caporal-chef de 1re classe | `enlisted` |
| `sergent` | Sergent | `non_commissioned` |
| `sergent_chef` | Sergent-chef | `non_commissioned` |
| `adjudant` | Adjudant | `non_commissioned` |
| `adjudant_chef` | Adjudant-chef | `non_commissioned` |
| `major` | Major | `non_commissioned` |
| `aspirant` | Aspirant | `officer_cadet` |
| `sous_lieutenant` | Sous-lieutenant | `junior_officer` |
| `lieutenant` | Lieutenant | `junior_officer` |
| `capitaine` | Capitaine | `junior_officer` |
| `commandant` | Commandant | `senior_officer` |
| `lieutenant_colonel` | Lieutenant-colonel | `senior_officer` |
| `colonel` | Colonel | `senior_officer` |
| `general_de_brigade` | Général de brigade | `general_officer` |
| `general_de_division` | Général de division | `general_officer` |
| `general_de_corps_d_armee` | Général de corps d'armée | `general_officer` |
| `general_d_armee` | Général d'armée | `general_officer` |
| `marechal_de_france` | Maréchal de France | `general_officer` |

**`military_rank_pl`** — Wojska Lądowe (Polska), selected by `country: "PL"`

| Term | Title | Category |
|---|---|---|
| `szeregowy` | szeregowy | `enlisted` |
| `starszy_szeregowy` | starszy szeregowy | `enlisted` |
| `kapral` | kapral | `non_commissioned` |
| `starszy_kapral` | starszy kapral | `non_commissioned` |
| `plutonowy` | plutonowy | `non_commissioned` |
| `sierzant` | sierżant | `non_commissioned` |
| `starszy_sierzant` | starszy sierżant | `non_commissioned` |
| `mlodszy_chorazy` | młodszy chorąży | `warrant` |
| `chorazy` | chorąży | `warrant` |
| `starszy_chorazy` | starszy chorąży | `warrant` |
| `starszy_chorazy_sztabowy` | starszy chorąży sztabowy | `warrant` |
| `podporucznik` | podporucznik | `junior_officer` |
| `porucznik` | porucznik | `junior_officer` |
| `kapitan` | kapitan | `junior_officer` |
| `major` | major | `senior_officer` |
| `podpulkownik` | podpułkownik | `senior_officer` |
| `pulkownik` | pułkownik | `senior_officer` |
| `general_brygady` | generał brygady | `general_officer` |
| `general_dywizji` | generał dywizji | `general_officer` |
| `general_broni` | generał broni | `general_officer` |
| `general` | generał | `general_officer` |
| `marszalek_polski` | marszałek Polski | `general_officer` |

**`military_rank_de`** — Heer (Deutschland), selected by `country: "DE"`

| Term | Title | Category |
|---|---|---|
| `soldat` | Soldat | `enlisted` |
| `gefreiter` | Gefreiter | `enlisted` |
| `obergefreiter` | Obergefreiter | `enlisted` |
| `hauptgefreiter` | Hauptgefreiter | `enlisted` |
| `stabsgefreiter` | Stabsgefreiter | `enlisted` |
| `oberstabsgefreiter` | Oberstabsgefreiter | `enlisted` |
| `unteroffizier` | Unteroffizier | `non_commissioned` |
| `stabsunteroffizier` | Stabsunteroffizier | `non_commissioned` |
| `feldwebel` | Feldwebel | `non_commissioned` |
| `oberfeldwebel` | Oberfeldwebel | `non_commissioned` |
| `hauptfeldwebel` | Hauptfeldwebel | `non_commissioned` |
| `stabsfeldwebel` | Stabsfeldwebel | `non_commissioned` |
| `oberstabsfeldwebel` | Oberstabsfeldwebel | `non_commissioned` |
| `fahnenjunker` | Fahnenjunker | `officer_cadet` |
| `faehnrich` | Fähnrich | `officer_cadet` |
| `oberfaehnrich` | Oberfähnrich | `officer_cadet` |
| `leutnant` | Leutnant | `junior_officer` |
| `oberleutnant` | Oberleutnant | `junior_officer` |
| `hauptmann` | Hauptmann | `junior_officer` |
| `stabshauptmann` | Stabshauptmann | `junior_officer` |
| `major` | Major | `senior_officer` |
| `oberstleutnant` | Oberstleutnant | `senior_officer` |
| `oberst` | Oberst | `senior_officer` |
| `brigadegeneral` | Brigadegeneral | `general_officer` |
| `generalmajor` | Generalmajor | `general_officer` |
| `generalleutnant` | Generalleutnant | `general_officer` |
| `general` | General | `general_officer` |

**`military_rank_gb`** — British Army (United Kingdom), selected by `country: "GB"`

| Term | Title | Category |
|---|---|---|
| `private` | Private | `enlisted` |
| `lance_corporal` | Lance Corporal | `non_commissioned` |
| `corporal` | Corporal | `non_commissioned` |
| `sergeant` | Sergeant | `non_commissioned` |
| `staff_sergeant` | Staff Sergeant | `non_commissioned` |
| `warrant_officer_class_2` | Warrant Officer Class 2 | `warrant` |
| `warrant_officer_class_1` | Warrant Officer Class 1 | `warrant` |
| `officer_cadet` | Officer Cadet | `officer_cadet` |
| `second_lieutenant` | Second Lieutenant | `junior_officer` |
| `lieutenant` | Lieutenant | `junior_officer` |
| `captain` | Captain | `junior_officer` |
| `major` | Major | `senior_officer` |
| `lieutenant_colonel` | Lieutenant Colonel | `senior_officer` |
| `colonel` | Colonel | `senior_officer` |
| `brigadier` | Brigadier | `general_officer` |
| `major_general` | Major General | `general_officer` |
| `lieutenant_general` | Lieutenant General | `general_officer` |
| `general` | General | `general_officer` |
| `field_marshal` | Field Marshal | `general_officer` |

**`military_rank_us`** — United States Army, selected by `country: "US"`

| Term | Title | Category |
|---|---|---|
| `private` | Private | `enlisted` |
| `private_first_class` | Private First Class | `enlisted` |
| `specialist` | Specialist | `enlisted` |
| `corporal` | Corporal | `non_commissioned` |
| `sergeant` | Sergeant | `non_commissioned` |
| `staff_sergeant` | Staff Sergeant | `non_commissioned` |
| `sergeant_first_class` | Sergeant First Class | `non_commissioned` |
| `master_sergeant` | Master Sergeant | `non_commissioned` |
| `first_sergeant` | First Sergeant | `non_commissioned` |
| `sergeant_major` | Sergeant Major | `non_commissioned` |
| `command_sergeant_major` | Command Sergeant Major | `non_commissioned` |
| `sergeant_major_of_the_army` | Sergeant Major of the Army | `non_commissioned` |
| `warrant_officer_1` | Warrant Officer 1 | `warrant` |
| `chief_warrant_officer_2` | Chief Warrant Officer 2 | `warrant` |
| `chief_warrant_officer_3` | Chief Warrant Officer 3 | `warrant` |
| `chief_warrant_officer_4` | Chief Warrant Officer 4 | `warrant` |
| `chief_warrant_officer_5` | Chief Warrant Officer 5 | `warrant` |
| `second_lieutenant` | Second Lieutenant | `junior_officer` |
| `first_lieutenant` | First Lieutenant | `junior_officer` |
| `captain` | Captain | `junior_officer` |
| `major` | Major | `senior_officer` |
| `lieutenant_colonel` | Lieutenant Colonel | `senior_officer` |
| `colonel` | Colonel | `senior_officer` |
| `brigadier_general` | Brigadier General | `general_officer` |
| `major_general` | Major General | `general_officer` |
| `lieutenant_general` | Lieutenant General | `general_officer` |
| `general` | General | `general_officer` |
| `general_of_the_army` | General of the Army | `general_officer` |

**`military_rank_ru`** — Сухопутные войска (Россия), selected by `country: "RU"`

| Term | Title | Category |
|---|---|---|
| `ryadovoy` | рядовой | `enlisted` |
| `efreytor` | ефрейтор | `enlisted` |
| `mladshiy_serzhant` | младший сержант | `non_commissioned` |
| `serzhant` | сержант | `non_commissioned` |
| `starshiy_serzhant` | старший сержант | `non_commissioned` |
| `starshina` | старшина | `non_commissioned` |
| `praporshchik` | прапорщик | `warrant` |
| `starshiy_praporshchik` | старший прапорщик | `warrant` |
| `mladshiy_leytenant` | младший лейтенант | `junior_officer` |
| `leytenant` | лейтенант | `junior_officer` |
| `starshiy_leytenant` | старший лейтенант | `junior_officer` |
| `kapitan` | капитан | `junior_officer` |
| `mayor` | майор | `senior_officer` |
| `podpolkovnik` | подполковник | `senior_officer` |
| `polkovnik` | полковник | `senior_officer` |
| `general_mayor` | генерал-майор | `general_officer` |
| `general_leytenant` | генерал-лейтенант | `general_officer` |
| `general_polkovnik` | генерал-полковник | `general_officer` |
| `general_armii` | генерал армии | `general_officer` |
| `marshal_rossiyskoy_federatsii` | маршал Российской Федерации | `general_officer` |

#### 5.9.3 Example

```json
{
  "military": {
    "ranks": [
      { "value": { "country": "PL", "service": "army", "rank": "kapral" },
        "date": { "value": "1939-08", "precision": "month" }, "confidence": 0.9 },
      { "value": { "rank_text": "Zugsführer", "category": "non_commissioned" },
        "date": { "value": "1916", "precision": "year" }, "confidence": 0.8,
        "note": "k.u.k. Infanterieregiment Nr. 20" }
    ],
    "units": [ { "value": "20 Pułk Piechoty Ziemi Krakowskiej",
                 "valid_from": { "date": { "value": "1938", "precision": "year" } }, "confidence": 0.9 } ],
    "service_numbers": [ { "value": { "number": "1043/38", "service": "army", "country": "PL" }, "confidence": 0.9 } ],
    "distinctions": [ { "value": { "name": "Krzyż Walecznych", "kind": "decoration", "country": "PL" },
                        "date": { "value": "1945", "precision": "year" }, "confidence": 0.9 } ]
  }
}
```

### 5.10 Legal

Criminal proceedings and their outcomes. `legal` throughout.

One claim per case: the offence as the source words it, its section of the UNODC International Classification of Crime for Statistical Purposes — which, like ICD chapters for illness, categorises without pretending to a precision the source does not have — where it was tried, and how it ended. A conviction later quashed, pardoned or expunged is recorded as it stands now, with the history in further claims if it matters.

#### 5.10.1 Attributes

Block: `legal` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Criminal record | `legal.criminal_record` | series | `offence` text; `iccs_section?` **iccs_section**; `jurisdiction?` **country**; `court?` text; `outcome?` **case_outcome**; `sentence?` text | `legal` |

- **`legal.criminal_record`** — One claim per case. The offence as the source words it, and its ICCS section.

#### 5.10.2 Vocabularies

**`iccs_section`** — Offence section (ICCS). *UNODC, International Classification of Crime for Statistical Purposes, version 1.0 (2015), level 1.*

| Term | Meaning |
|---|---|
| `acts_leading_to_death` | 01: acts leading to death or intending to cause death. |
| `acts_causing_harm` | 02: acts causing harm or intending to cause harm to the person. |
| `sexual_acts` | 03: injurious acts of a sexual nature. |
| `property_with_violence` | 04: acts against property involving violence or threat against a person. |
| `property_only` | 05: acts against property only. |
| `controlled_substances` | 06: acts involving controlled psychoactive substances or other drugs. |
| `fraud_deception_corruption` | 07: acts involving fraud, deception or corruption. |
| `public_order_and_state` | 08: acts against public order, authority and provisions of the State. |
| `public_safety_and_security` | 09: acts against public safety and state security. |
| `natural_environment` | 10: acts against the natural environment. |
| `other_criminal_acts` | 11: other criminal acts not elsewhere classified. |

**`case_outcome`** — Case outcome

| Term | Meaning |
|---|---|
| `convicted` | Convicted. |
| `acquitted` | Acquitted. |
| `dismissed` | Charges dismissed or dropped. |
| `conviction_quashed` | Conviction quashed on appeal. |
| `pardoned` | Pardoned. |
| `amnestied` | Amnestied. |
| `expunged` | Record expunged. |
| `pending` | Pending. |
| `unknown` | Not known. |

#### 5.10.3 Example

```json
{
  "legal": {
    "criminal_record": [
      { "value": { "offence": "Kradzież drewna z lasu rządowego", "iccs_section": "property_only",
                   "jurisdiction": "PL", "court": "Sąd Pokoju w Miechowie", "outcome": "convicted",
                   "sentence": "Grzywna 15 rubli" },
        "date": { "value": "1897-11-02", "precision": "exact" }, "confidence": 0.9 }
    ]
  }
}
```

### 5.11 Belief and affiliation

Faith, conviction, and the organisations a person belonged to. The whole group is `health` (Appendix A.6).

A religion is a tradition from the vocabulary and a denomination as the source names it: `christianity_orthodox` and "Old Believers", `christianity_catholic` and "Greek Catholic". Sacraments are claims about the person; the rite itself, with its godparents and officiant, is an Event (1.0 §4.3), and the claim's `event_id` points at it.

#### 5.11.1 Attributes

Block: `belief` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Religion | `belief.religions` | series | `tradition` **religion**; `denomination?` text | `health` |
| Sacraments received | `belief.sacraments` | series | `sacrament` **sacrament**; `place_id?` uuid | `health` |
| Individual beliefs | `belief.beliefs` | series | text | `health` |
| Political leanings | `belief.political_leanings` | series | `position?` **political_position**; `party?` text; one of: `position` or `party` | `health` |
| Union and association memberships | `belief.memberships` | series | `organisation` text; `kind?` **membership_kind**; `role?` text | `health` |

- **`belief.religions`** — The tradition from the vocabulary; the church, rite or community as the source names it.
- **`belief.sacraments`** — Point the claim's `event_id` at the Event when one exists.
- **`belief.beliefs`** — Free text.
- **`belief.memberships`** — The period goes in `valid_from` / `valid_until`.

#### 5.11.2 Vocabularies

**`religion`** — Religious tradition

| Term | Meaning |
|---|---|
| `buddhism` | Buddhism. |
| `christianity_catholic` | Christianity: Catholic, Latin or Eastern. |
| `christianity_orthodox` | Christianity: Eastern Orthodox, Oriental Orthodox, Old Believers. |
| `christianity_protestant` | Christianity: Protestant, including Anglican. |
| `christianity_other` | Christianity: another tradition. |
| `hinduism` | Hinduism. |
| `islam_sunni` | Islam: Sunni. |
| `islam_shia` | Islam: Shia. |
| `islam_other` | Islam: another tradition. |
| `jainism` | Jainism. |
| `judaism` | Judaism. |
| `sikhism` | Sikhism. |
| `bahai` | Bahá'í Faith. |
| `shinto` | Shinto. |
| `taoism` | Taoism. |
| `zoroastrianism` | Zoroastrianism. |
| `traditional` | A traditional, folk or indigenous religion. |
| `other` | Another religion. |
| `none` | No religion. |
| `unknown` | Not known. |

**`sacrament`** — Sacrament or rite

| Term | Meaning |
|---|---|
| `baptism` | Baptism. |
| `confirmation` | Confirmation, or chrismation. |
| `first_communion` | First communion. |
| `reconciliation` | Reconciliation, or penance. |
| `anointing_of_the_sick` | Anointing of the sick. |
| `holy_orders` | Holy orders. |
| `matrimony` | Matrimony. |
| `other_rite` | Another rite of passage; the note says which. |

**`political_position`** — Political position

| Term | Meaning |
|---|---|
| `far_left` | Far left. |
| `left` | Left. |
| `centre_left` | Centre-left. |
| `centre` | Centre. |
| `centre_right` | Centre-right. |
| `right` | Right. |
| `far_right` | Far right. |
| `apolitical` | Apolitical. |
| `other` | Not on this axis. |
| `unknown` | Not known. |

**`membership_kind`** — Membership

| Term | Meaning |
|---|---|
| `trade_union` | A trade union. |
| `political_party` | A political party. |
| `professional_body` | A professional body. |
| `religious_order` | A religious order. |
| `religious_association` | A religious association or confraternity. |
| `fraternal_order` | A fraternal order. |
| `veterans_association` | A veterans' association. |
| `sports_club` | A sports club. |
| `cultural_association` | A cultural association. |
| `charitable_association` | A charitable association. |
| `other` | Another organisation. |

#### 5.11.3 Example

```json
{
  "belief": {
    "religions": [
      { "value": { "tradition": "christianity_catholic", "denomination": "Greek Catholic" },
        "valid_until": { "date": { "value": "1946", "precision": "year" } }, "confidence": 0.9 },
      { "value": { "tradition": "christianity_orthodox", "denomination": "Polish Autocephalous Orthodox Church" },
        "valid_from": { "date": { "value": "1946", "precision": "year" } }, "confidence": 0.7 }
    ],
    "sacraments": [
      { "value": { "sacrament": "baptism" }, "date": { "value": "1911-05-07", "precision": "exact" },
        "event_id": "2c1d4f5e-6a7b-4c8d-9e0f-1a2b3c4d5e6f", "confidence": 0.95 }
    ],
    "memberships": [
      { "value": { "organisation": "Związek Zawodowy Kolejarzy", "kind": "trade_union" },
        "valid_from": { "date": { "value": "1925", "precision": "year" } }, "confidence": 0.8 }
    ]
  }
}
```

### 5.12 Personality and behaviour

Temperament, habits and pastimes.

**Big Five are scores, never labels.** Each of the five axes is 0–100 — a percentile, so that instruments with different raw scales compare — with the instrument that produced them. A profile inferred from letters or described by a relative is `inferred` or `observer_rating` and says so, which is what lets a reader weigh it. A source that says only that somebody was "reserved" is `introversion_extraversion`, not an invented Big Five.

`dependencies` is `health`. The rest of the group has no class, but see §4.6 for how the group should be governed on a living person.

#### 5.12.1 Attributes

Block: `personality` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Personality traits (Big Five) | `personality.big_five` | series | `openness` integer (0–100); `conscientiousness` integer (0–100); `extraversion` integer (0–100); `agreeableness` integer (0–100); `neuroticism` integer (0–100); `instrument?` **personality_instrument** | — |
| Personality traits (MBTI) | `personality.mbti` | series | **mbti** | — |
| Introversion/extraversion | `personality.introversion_extraversion` | series | **introversion_extraversion** | — |
| Stress tolerance | `personality.stress_tolerance` | series | **stress_tolerance** | — |
| Decision-making style | `personality.decision_style` | series | **decision_style** | — |
| Interests | `personality.interests` | series | text | — |
| Hobbies | `personality.hobbies` | series | text | — |
| Sport | `personality.sports` | series | `sport` text; `level?` **sport_level** | — |
| Dietary habits | `personality.dietary_habits` | series | `diet` **diet**; `details?` text | — |
| Dependencies and addictions (tobacco, alcohol, substances) | `personality.dependencies` | series | `substance` **substance**; `pattern?` **use_pattern** | `health` |

- **`personality.big_five`** — Five scores from 0 to 100, never labels: a T-score or a percentile is converted to a percentile and the instrument named.
- **`personality.introversion_extraversion`** — A descriptor for sources that say "reserved" or "gregarious" and measured nothing.
- **`personality.interests`** — Free text.
- **`personality.hobbies`** — Free text.
- **`personality.dietary_habits`** — A restriction observed for faith or for health belongs in the class that governs it, not here.

#### 5.12.2 Vocabularies

**`personality_instrument`** — Personality instrument

| Term | Meaning |
|---|---|
| `neo_pi_3` | NEO Personality Inventory-3. |
| `neo_ffi_3` | NEO Five-Factor Inventory-3. |
| `bfi_2` | Big Five Inventory-2. |
| `ipip_neo_120` | IPIP-NEO-120. |
| `tipi` | Ten-Item Personality Inventory. |
| `hexaco_pi_r` | HEXACO-PI-R, Big Five axes only. |
| `observer_rating` | Rated by somebody who knew the person. |
| `inferred` | Inferred from records rather than measured. |
| `other` | Another instrument. |

**`mbti`** — MBTI type. *Myers–Briggs Type Indicator.*

| Term | Meaning |
|---|---|
| `ISTJ` | ISTJ. |
| `ISFJ` | ISFJ. |
| `INFJ` | INFJ. |
| `INTJ` | INTJ. |
| `ISTP` | ISTP. |
| `ISFP` | ISFP. |
| `INFP` | INFP. |
| `INTP` | INTP. |
| `ESTP` | ESTP. |
| `ESFP` | ESFP. |
| `ENFP` | ENFP. |
| `ENTP` | ENTP. |
| `ESTJ` | ESTJ. |
| `ESFJ` | ESFJ. |
| `ENFJ` | ENFJ. |
| `ENTJ` | ENTJ. |

**`introversion_extraversion`** — Introversion and extraversion

| Term | Meaning |
|---|---|
| `strongly_introverted` | Strongly introverted. |
| `introverted` | Introverted. |
| `ambiverted` | Ambiverted. |
| `extraverted` | Extraverted. |
| `strongly_extraverted` | Strongly extraverted. |

**`stress_tolerance`** — Stress tolerance

| Term | Meaning |
|---|---|
| `very_low` | Very low. |
| `low` | Low. |
| `moderate` | Moderate. |
| `high` | High. |
| `very_high` | Very high. |

**`decision_style`** — Decision-making style. *Scott & Bruce (1995), General Decision-Making Style inventory.*

| Term | Meaning |
|---|---|
| `rational` | Rational: a thorough search for and logical evaluation of alternatives. |
| `intuitive` | Intuitive: reliance on hunches and feelings. |
| `dependent` | Dependent: a search for advice and direction from others. |
| `avoidant` | Avoidant: postponing and avoiding decisions. |
| `spontaneous` | Spontaneous: a sense of immediacy and a wish to be through the decision quickly. |

**`sport_level`** — Sport level

| Term | Meaning |
|---|---|
| `recreational` | Recreational. |
| `amateur_competitive` | Competitive, amateur. |
| `semi_professional` | Semi-professional. |
| `professional` | Professional. |

**`diet`** — Dietary pattern

| Term | Meaning |
|---|---|
| `omnivore` | Omnivore. |
| `flexitarian` | Flexitarian. |
| `pescatarian` | Pescatarian. |
| `vegetarian` | Vegetarian. |
| `vegan` | Vegan. |
| `other` | Another pattern. |

**`substance`** — Substance or behaviour

| Term | Meaning |
|---|---|
| `tobacco` | Tobacco and nicotine. |
| `alcohol` | Alcohol. |
| `cannabis` | Cannabis. |
| `opioids` | Opioids. |
| `stimulants` | Stimulants, including cocaine. |
| `sedatives_hypnotics` | Sedatives and hypnotics. |
| `hallucinogens` | Hallucinogens. |
| `inhalants` | Volatile inhalants. |
| `gambling` | Gambling. |
| `gaming` | Gaming. |
| `other` | Another substance or behaviour. |

**`use_pattern`** — Pattern of use

| Term | Meaning |
|---|---|
| `occasional_use` | Occasional use. |
| `regular_use` | Regular use. |
| `harmful_use` | Harmful use. |
| `dependence` | Dependence. |
| `in_remission` | In remission. |

#### 5.12.3 Example

```json
{
  "personality": {
    "big_five": [
      { "value": { "openness": 70, "conscientiousness": 85, "extraversion": 25, "agreeableness": 60,
                   "neuroticism": 55, "instrument": "inferred" },
        "confidence": 0.3, "note": "Inferred from forty years of letters." }
    ],
    "mbti": [ { "value": "ISTJ", "date": { "value": "1979", "precision": "year" }, "confidence": 0.6 } ],
    "decision_style": [ { "value": "rational", "confidence": 0.5 } ],
    "stress_tolerance": [ { "value": "high", "confidence": 0.5 } ],
    "hobbies": [ { "value": "Stamp collecting", "confidence": 0.9 } ],
    "sports": [ { "value": { "sport": "Rowing", "level": "amateur_competitive" },
                  "valid_until": { "date": { "value": "1939", "precision": "year" } }, "confidence": 0.8 } ],
    "dependencies": [
      { "value": { "substance": "tobacco", "pattern": "dependence" },
        "valid_until": { "date": { "value": "1971", "precision": "year" } }, "confidence": 0.8 }
    ]
  }
}
```

### 5.13 Relationships

Who the person was related to. In AXGF this lives on Family and Link and never on the person (1.0 P1; Appendix A.3): a spouse recorded on both people and on their Family would be three records of one fact. 1.1 adds the two things 1.0 could not say.

**`lineage`** on each entry of `Family.children[]` says how the child belongs to that family's union: `biological`, `adoptive`, `foster`, `step`, `guardianship` or `unknown`. Absent means the record does not say — the 1.0 reading — which is not the same as `biological`. A child raised by a mother and a stepfather is a child of two families: the biological one, and the mother's second union with `lineage: step`.

**`relation`** on Link says what the relationship is, from the `from` entity's side, where `label` and `label_reverse` say it in words. `relation: godparent` with `label: "matka chrzestna"` states the kind for software and the words for people.

#### 5.13.1 Attributes

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Biological father; biological mother | Family where the person is a child with `lineage: biological`; the partners of its union | mapped | — | — |
| Adoptive parents | Family where the person is a child with `lineage: adoptive` | mapped | — | — |
| Siblings | the other children of the families the person is a child of | mapped | — | — |
| Sibling rank | Family.children[].birth_order (1.0) | mapped | — | — |
| Spouses | Family.union.persons of the families the person is a partner in | mapped | — | — |
| Marriage and civil-union dates | Family.union.start.date, with union.type marriage or civil_union (1.0) | mapped | — | — |
| Divorce and separation dates | Family.union.end.date, with union.status ended_by_divorce or ended_by_separation (1.0) | mapped | — | — |
| Children | Family.children of the families the person is a partner in (1.0) | mapped | — | — |
| Godparents | Link with `relation: godparent`, category spiritual | mapped | — | — |
| Official witnesses | Link with `relation: witness`; Event participants with role witness (1.0) | mapped | — | — |
| Business relationships | Link with category professional and `relation` business_partner, employer or employee | mapped | — | — |
| Close friends | Link with `relation: close_friend`, category social | mapped | — | — |

#### 5.13.2 Vocabularies

**`lineage`** — Lineage. *GEDCOM PEDI, extended.*

| Term | Meaning |
|---|---|
| `biological` | The child's biological parents. |
| `adoptive` | Parents by adoption. |
| `foster` | Foster parents. |
| `step` | A parent's partner who is not a parent of the child. |
| `guardianship` | Legal guardians. |
| `unknown` | Not known. |

**`link_relation`** — Relation

| Term | Meaning |
|---|---|
| `godparent` | The from-end is godparent of the to-end. |
| `godchild` | The from-end is godchild of the to-end. |
| `witness` | The from-end witnessed something for the to-end. |
| `officiant` | The from-end officiated for the to-end. |
| `business_partner` | Business partners. |
| `employer` | The from-end employed the to-end. |
| `employee` | The from-end was employed by the to-end. |
| `mentor` | The from-end was mentor to the to-end. |
| `apprentice` | The from-end was apprenticed to the to-end. |
| `close_friend` | Close friends. |
| `neighbour` | Neighbours. |
| `guardian` | The from-end was guardian of the to-end. |
| `ward` | The from-end was ward of the to-end. |
| `other` | Another relation; the label says which. |

#### 5.13.3 Example

```json
{
  "id": "aaaa1234-e29b-41d4-a716-446655440001",
  "type": "family",
  "axgf_version": "1.1",
  "union": {
    "type": "marriage",
    "persons": [
      { "person_id": "11111111-1111-4111-8111-111111111111", "role": "spouse" },
      { "person_id": "22222222-2222-4222-8222-222222222222", "role": "spouse" }
    ],
    "start": { "date": { "value": "1950-06-03", "precision": "exact" } }
  },
  "children": [
    { "person_id": "33333333-3333-4333-8333-333333333333", "birth_order": 1, "lineage": "step" },
    { "person_id": "44444444-4444-4444-8444-444444444444", "birth_order": 2, "lineage": "biological" }
  ]
}

{
  "id": "bbbb1234-e29b-41d4-a716-446655440002",
  "type": "link",
  "axgf_version": "1.1",
  "from": { "entity_type": "person", "entity_id": "55555555-5555-4555-8555-555555555555" },
  "to":   { "entity_type": "person", "entity_id": "44444444-4444-4444-8444-444444444444" },
  "label": "matka chrzestna",
  "label_reverse": "chrześniak",
  "category": "spiritual",
  "relation": "godparent",
  "confidence": 0.9
}
```

### 5.14 Digital legacy

Artefacts made from or about the person: models of the body, recordings of the voice, collected writing, archives of accounts, and models trained to behave like them. They are things, not facts, and every attribute but one holds artefact references (§3.5.1) whose files are Documents. The exception is `carbon_footprint`, an estimate with the method that produced it.

Body models, skin textures, rigs and voice corpora are `biometrics`: each can identify, or imitate, the person it was made from. Because every artefact in this group is made to stand in for a person, recording `consent` is strongly recommended, and a behaviour model of a living person falls under §4.6.

#### 5.14.1 Attributes

Block: `digital_legacy` on Person.

| Attribute | Path | Kind | Value | Class |
|---|---|---|---|---|
| Source morphological 3D model (mesh or point cloud) | `digital_legacy.body_models` | series | artefact: `mesh`, `point_cloud` | `biometrics` |
| HD skin texture map | `digital_legacy.skin_textures` | series | artefact: `skin_texture_map` | `biometrics` |
| Skeletal and articular rigging | `digital_legacy.rigs` | series | artefact: `skeletal_rig` | `biometrics` |
| Source audio for voice synthesis | `digital_legacy.voice_corpora` | series | artefact: `voice_corpus` | `biometrics` |
| Written corpus for LLM training | `digital_legacy.text_corpora` | series | artefact: `text_corpus` | — |
| Digital trace history | `digital_legacy.digital_traces` | series | artefact: `trace_archive` | — |
| Estimated carbon footprint | `digital_legacy.carbon_footprint` | series | `tonnes_co2e_per_year` number (t CO2e/yr, 0–100000); `method?` text | — |
| AI-driven reactive behaviour model | `digital_legacy.behaviour_models` | series | artefact: `behaviour_model` | — |

- **`digital_legacy.body_models`** — A body or face model identifies its subject.
- **`digital_legacy.rigs`** — A rig carries the body's proportions.
- **`digital_legacy.carbon_footprint`** — The one fact in a group of artefacts: an estimate, with the method that produced it.
- **`digital_legacy.behaviour_models`** — See §4.6.

#### 5.14.2 Example

```json
{
  "digital_legacy": {
    "body_models": [
      { "value": { "document_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d", "artefact_type": "mesh",
                   "format": "glTF", "generator": "Photogrammetry from 214 photographs", "consent": "given" },
        "date": { "value": "2024-05", "precision": "month" }, "confidence": 0.9 }
    ],
    "rigs": [
      { "value": { "document_id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e", "artefact_type": "skeletal_rig",
                   "derived_from_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d" }, "confidence": 0.9 }
    ],
    "text_corpora": [
      { "value": { "document_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e70", "artefact_type": "text_corpus",
                   "format": "JSONL", "consent": "given_by_estate" }, "confidence": 0.95,
        "note": "Letters 1946–1998, transcribed." }
    ],
    "carbon_footprint": [
      { "value": { "tonnes_co2e_per_year": 6.2, "method": "Household consumption survey, national factors" },
        "date": { "value": "2015", "precision": "year" }, "confidence": 0.4 }
    ]
  }
}
```

---

## 6. Vocabulary Index

Every closed vocabulary 1.1 defines, where it is defined, and the standard it follows. In the schema each is `$defs/vocab_<name>`.

| Vocabulary | Title | Terms | Defined in | Standard |
|---|---|---|---|---|
| `sensitive_class` | Sensitive class | 4 | §4.1 | AXGF 1.1 §4 |
| `laterality` | Laterality | 3 | §3.5 | — |
| `body_region` | Body region | 21 | §3.5 | — |
| `artefact_type` | Artefact type | 12 | §3.5 | — |
| `consent` | Consent | 6 | §3.5 | — |
| `sex_at_birth` | Sex at birth | 5 | §5.1 | — |
| `gender_identity` | Gender identity | 6 | §5.1 | — |
| `title_kind` | Title kind | 8 | §5.1 | — |
| `register_type` | Register entry type | 11 | §5.1 | — |
| `build` | Build | 6 | §5.2 | — |
| `eye_colour` | Eye colour | 15 | §5.2 | — |
| `eye_shape` | Eye shape | 9 | §5.2 | — |
| `eye_spacing` | Eye spacing | 3 | §5.2 | — |
| `hair_colour` | Natural hair colour | 14 | §5.2 | — |
| `hair_texture` | Hair texture | 5 | §5.2 | — |
| `hairline` | Hairline | 8 | §5.2 | — |
| `facial_hair` | Facial hair | 7 | §5.2 | — |
| `body_hair` | Body hair | 4 | §5.2 | — |
| `skin_tone` | Skin tone (Fitzpatrick phototype) | 6 | §5.2 | Fitzpatrick, T. B. (1988), The validity and practicality of sun-reactive skin types I through VI |
| `skin_undertone` | Skin undertone | 4 | §5.2 | — |
| `freckles` | Freckles | 4 | §5.2 | — |
| `pigmentation_mark` | Pigmentation mark | 6 | §5.2 | — |
| `mole_shape` | Mole shape | 4 | §5.2 | — |
| `face_shape` | Face shape | 7 | §5.2 | — |
| `nose_shape` | Nose shape | 9 | §5.2 | — |
| `ear_shape` | Ear shape | 6 | §5.2 | — |
| `lip_shape` | Lip shape | 7 | §5.2 | — |
| `dentition` | Dentition | 8 | §5.2 | — |
| `malocclusion` | Malocclusion (Angle class) | 5 | §5.2 | Angle, E. H. (1899), Classification of malocclusion |
| `posture` | Posture | 7 | §5.2 | Kendall, McCreary et al., Muscles: Testing and Function (postural types) |
| `gait` | Gait | 9 | §5.2 | — |
| `vocal_timbre` | Vocal timbre | 9 | §5.3 | — |
| `speech_register` | Register of speech | 5 | §5.3 | Joos, M. (1961), The Five Clocks |
| `handedness` | Handedness | 5 | §5.3 | — |
| `hearing_grade` | Hearing grade | 7 | §5.3 | World Health Organization (2021), World report on hearing |
| `optical_correction` | Optical correction | 7 | §5.3 | — |
| `blood_group` | Blood group (ABO) | 4 | §5.4 | ISBT ABO blood group system |
| `rhesus` | Rhesus (RhD) | 4 | §5.4 | ISBT Rh blood group system |
| `icd10_chapter` | ICD-10 chapter | 22 | §5.4 | WHO International Statistical Classification of Diseases and Related Health Problems, 10th revision |
| `diagnosis_status` | Diagnosis status | 4 | §5.4 | — |
| `prosthesis_kind` | Prosthesis | 7 | §5.4 | — |
| `implant_kind` | Biomedical implant | 8 | §5.4 | — |
| `device_kind` | Intracorporeal device | 10 | §5.4 | — |
| `allergy_type` | Allergy type | 6 | §5.4 | — |
| `allergy_severity` | Allergy severity | 5 | §5.4 | — |
| `pathogen` | Pathogen or vaccine target | 32 | §5.4 | — |
| `vaccination_status` | Vaccination status | 5 | §5.4 | — |
| `serology_result` | Serology result | 4 | §5.4 | — |
| `lab_panel` | Laboratory panel | 6 | §5.4 | — |
| `lab_analyte` | Laboratory analyte | 31 | §5.4 | — |
| `lab_unit` | Laboratory unit (UCUM) | 14 | §5.4 | Unified Code for Units of Measure |
| `lab_flag` | Laboratory flag | 5 | §5.4 | — |
| `nutrient` | Nutrient | 21 | §5.4 | — |
| `sleep_disorder` | Sleep disorder category | 7 | §5.4 | American Academy of Sleep Medicine, International Classification of Sleep Disorders, 3rd edition |
| `assessment_instrument` | Assessment instrument | 11 | §5.4 | — |
| `assessment_severity` | Assessment severity | 5 | §5.4 | — |
| `reference_build` | Reference genome build | 4 | §5.5 | Genome Reference Consortium; Telomere-to-Telomere Consortium |
| `genomic_file_format` | Genomic file format | 7 | §5.5 | — |
| `y_haplogroup` | Y-DNA major haplogroup | 20 | §5.5 | ISOGG Y-DNA Haplogroup Tree |
| `mt_haplogroup` | mtDNA major haplogroup | 33 | §5.5 | PhyloTree (the mtDNA nomenclature ISOGG adopts) |
| `zygosity` | Zygosity | 4 | §5.5 | — |
| `clinical_significance` | Clinical significance | 5 | §5.5 | Richards et al. (2015), ACMG/AMP standards for the interpretation of sequence variants |
| `inheritance_pattern` | Inheritance pattern | 8 | §5.5 | — |
| `carrier_status` | Carrier status | 4 | §5.5 | — |
| `epigenetic_clock` | Epigenetic clock | 6 | §5.5 | — |
| `metaboliser_status` | Metaboliser status | 5 | §5.5 | Clinical Pharmacogenetics Implementation Consortium (CPIC) standardised terms |
| `autopsy` | Autopsy | 5 | §5.6 | — |
| `disposition` | Disposition of the body | 8 | §5.6 | — |
| `address_use` | Address use | 5 | §5.7 | — |
| `country` | Country | 254 | §3.5 | ISO 3166-1 alpha-2, plus the historical codes of AXGF 1.0 §6.5 |
| `nationality_mode` | How a nationality was acquired | 8 | §5.7 | — |
| `language_proficiency` | Language proficiency | 7 | §5.7 | Council of Europe, Common European Framework of Reference for Languages |
| `isced_level` | Education level (ISCED 2011) | 9 | §5.8 | UNESCO Institute for Statistics, International Standard Classification of Education 2011 |
| `income_quintile` | Income quintile | 5 | §5.8 | — |
| `pay_period` | Pay period | 5 | §5.8 | — |
| `tenure` | Tenure | 6 | §5.8 | — |
| `distinction_kind` | Distinction | 5 | §5.9 | — |
| `military_service` | Service | 8 | §5.9 | — |
| `rank_category` | Rank category | 7 | §5.9 | — |
| `military_rank_fr` | Military rank — Armée de terre (France) | 22 | §5.9 | — |
| `military_rank_pl` | Military rank — Wojska Lądowe (Polska) | 22 | §5.9 | — |
| `military_rank_de` | Military rank — Heer (Deutschland) | 27 | §5.9 | — |
| `military_rank_gb` | Military rank — British Army (United Kingdom) | 19 | §5.9 | — |
| `military_rank_us` | Military rank — United States Army | 28 | §5.9 | — |
| `military_rank_ru` | Military rank — Сухопутные войска (Россия) | 20 | §5.9 | — |
| `iccs_section` | Offence section (ICCS) | 11 | §5.10 | UNODC, International Classification of Crime for Statistical Purposes, version 1.0 (2015), level 1 |
| `case_outcome` | Case outcome | 9 | §5.10 | — |
| `religion` | Religious tradition | 20 | §5.11 | — |
| `sacrament` | Sacrament or rite | 8 | §5.11 | — |
| `political_position` | Political position | 10 | §5.11 | — |
| `membership_kind` | Membership | 11 | §5.11 | — |
| `mbti` | MBTI type | 16 | §5.12 | Myers–Briggs Type Indicator |
| `personality_instrument` | Personality instrument | 9 | §5.12 | — |
| `introversion_extraversion` | Introversion and extraversion | 5 | §5.12 | — |
| `stress_tolerance` | Stress tolerance | 5 | §5.12 | — |
| `decision_style` | Decision-making style | 5 | §5.12 | Scott & Bruce (1995), General Decision-Making Style inventory |
| `sport_level` | Sport level | 4 | §5.12 | — |
| `diet` | Dietary pattern | 6 | §5.12 | — |
| `substance` | Substance or behaviour | 11 | §5.12 | — |
| `use_pattern` | Pattern of use | 5 | §5.12 | — |
| `lineage` | Lineage | 6 | §5.13 | GEDCOM PEDI, extended |
| `link_relation` | Relation | 14 | §5.13 | — |

Terms are lowercase ASCII with underscores, except where the standard's own notation is the term: ABO groups (`A`, `AB`), MBTI types (`INTJ`), haplogroups (`R`, `L3`), UCUM units (`mmol/L`) and ISO country codes (`PL`). A term is an identifier, not a label: implementations translate terms for display and store the term.

---

## 7. Validation

### 7.1 Structural

Every entity MUST validate against `schema/axgf-1.1.schema.json` (1.0 §12.1 applies unchanged). The schema enumerates every vocabulary, so a value outside one fails structurally.

### 7.2 Out-of-vocabulary values

A value outside its vocabulary MUST be reported, never silently accepted and never silently coerced to a neighbouring term. A validator SHOULD report it distinctly from other structural failures — naming the attribute, the value and the vocabulary — because it is the one failure a contributor can nearly always fix by choosing again. The reference library reports it as `OUT_OF_VOCABULARY`.

Unknown *attributes* inside a 1.1 block are not errors: 1.0 P9 applies, and a later minor version may add attributes. Validators MAY report them for information, since a misspelt attribute name is otherwise invisible.

### 7.3 Semantic rules

These cannot be expressed in the schema, and validators SHOULD check them:

| Rule | Applies to |
|---|---|
| A haplogroup `subclade` begins with its `major`: `R-M269` and `R1b1a` under `R`, `H1a1` under `H`. | `genomics.y_haplogroup`, `genomics.mt_haplogroup` |
| A laboratory `analyte` belongs to its `panel` (§5.4). | `health.lab_results` |
| A registered `rank`'s `category`, when both are given, is the category the vocabulary assigns it. | `military.ranks` |
| `dunedinpace` gives `pace`; every other clock gives `age_years`. | `genomics.epigenetic_age` |
| `valid_until` is not before `valid_from`. | every claim |
| An entity with 1.1 attributes declares `"1.1"`; no entity declares a version newer than its manifest (§2.1). | every entity |
| `death.causes[].sequence` values are distinct. | `death.causes` |

Semantic findings are warnings, not refusals: 1.0's validation is non-blocking and so is this.

---

## 8. Complete Example

A deceased person with claims in most groups. Every value in it is a term from this specification, and the file validates against the 1.1 schema; it is also [`examples/person-profile-1.1.json`](./examples/person-profile-1.1.json).

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "type": "person",
  "axgf_version": "1.1",
  "created_at": "2026-09-15T09:00:00Z",
  "updated_at": "2026-09-15T09:00:00Z",
  "version_num": 1,
  "identity": {
    "name": {
      "display": "Zofia Nowicka",
      "components": [
        { "type": "given_name",  "value": "Zofia",   "order": 1 },
        { "type": "family_name", "value": "Nowicka", "order": 2 }
      ]
    },
    "names": [
      { "type": "nickname", "display": "Zosia", "components": [], "confidence": 0.9 }
    ],
    "gender": { "value": "F" },
    "is_living": false,
    "visibility": "members",
    "titles": [
      { "value": { "text": "dr", "kind": "academic" },
        "date": { "value": "1961", "precision": "year" },
        "source_id": "9b2f0d1e-3c4a-4b5d-8e6f-7a8b9c0d1e2f", "confidence": 0.95 }
    ],
    "sex_at_birth": { "value": "female",
                      "source_id": "5a1e2b3c-4d5e-4f60-8a7b-9c0d1e2f3a4b", "confidence": 0.99 },
    "class_visibility": { "health": "contributors" }
  },
  "birth": {
    "date": { "value": "1932-03-14", "precision": "exact" },
    "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "confidence": 0.99,
    "source_id": "5a1e2b3c-4d5e-4f60-8a7b-9c0d1e2f3a4b",
    "time": { "value": "05:40", "source_id": "5a1e2b3c-4d5e-4f60-8a7b-9c0d1e2f3a4b", "confidence": 0.8 }
  },
  "civil_status": {
    "birth_certificate_number": { "value": "212/1932", "confidence": 0.99,
                                  "source_id": "5a1e2b3c-4d5e-4f60-8a7b-9c0d1e2f3a4b" },
    "register_entries": [
      { "value": { "register_type": "birth", "office": "Urząd Stanu Cywilnego Lublin-Śródmieście",
                   "volume": "1932/I", "page": "71", "entry_number": "212" },
        "date": { "value": "1932-03-16", "precision": "exact" },
        "source_id": "5a1e2b3c-4d5e-4f60-8a7b-9c0d1e2f3a4b", "confidence": 0.99 }
    ],
    "marginal_annotations": [
      { "value": { "text": "Zawarła związek małżeński 12.08.1955 w Lublinie, akt 604/1955.",
                   "register_type": "birth", "entry_number": "212" },
        "date": { "value": "1955-08-20", "precision": "exact" },
        "source_id": "5a1e2b3c-4d5e-4f60-8a7b-9c0d1e2f3a4b", "confidence": 0.95 }
    ]
  },
  "morphology": {
    "height": [
      { "value": 158, "date": { "value": "1950", "precision": "year" }, "confidence": 0.9,
        "source_id": "9b2f0d1e-3c4a-4b5d-8e6f-7a8b9c0d1e2f" },
      { "value": 154, "date": { "value": "2005", "precision": "year" }, "confidence": 0.7 }
    ],
    "eye_colour": [ { "value": "grey_green", "confidence": 0.8 } ],
    "hair_colour": [
      { "value": "dark_blond", "date": { "value": "1950", "precision": "year" }, "confidence": 0.8 },
      { "value": "white", "date": { "value": "2005", "precision": "year" }, "confidence": 0.9 }
    ],
    "skin_tone": { "value": "type_ii", "confidence": 0.6, "note": "From photographs and a family description." },
    "scars": [ { "value": { "description": "Appendectomy scar", "body_region": "abdomen" }, "confidence": 0.9 } ],
    "moles": [ { "value": { "body_region": "face", "location": "left cheek, below the eye",
                            "shape": "round", "diameter_mm": 3 }, "confidence": 0.9 } ],
    "gait": [ { "value": "brisk", "date": { "value": "1980", "precision": "decade" }, "confidence": 0.6 } ]
  },
  "biometrics": {
    "handedness": [ { "value": "right", "confidence": 0.9 } ],
    "speech_register": [ { "value": "formal", "confidence": 0.7 } ],
    "visual_acuity": [
      { "value": { "eye": "both", "decimal": 0.8, "corrected": true },
        "date": { "value": "2001-05", "precision": "month" }, "confidence": 0.9 }
    ],
    "optical_correction": [
      { "value": { "kind": "glasses", "prescription": "+2.25 both eyes" },
        "valid_from": { "date": { "value": "1975", "precision": "year" } }, "confidence": 0.9 }
    ]
  },
  "health": {
    "blood_group": { "value": "A", "confidence": 0.95, "source_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f" },
    "rhesus": { "value": "negative", "confidence": 0.95, "source_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f" },
    "blood_pressure": [
      { "value": { "systolic": 145, "diastolic": 88 },
        "date": { "value": "2010-02-03", "precision": "exact" }, "confidence": 0.9 }
    ],
    "conditions": [
      { "value": { "description": "Essential hypertension", "icd10_chapter": "circulatory",
                   "chronic": true, "diagnosis": "diagnosed" },
        "valid_from": { "date": { "value": "1998", "precision": "year" } }, "confidence": 0.9 },
      { "value": { "description": "Hashimoto's thyroiditis", "icd10_chapter": "endocrine_metabolic",
                   "chronic": true, "autoimmune": true, "diagnosis": "diagnosed" },
        "confidence": 0.85 }
    ],
    "allergies": [
      { "value": { "type": "drug", "allergen": "penicillin", "severity": "severe", "reaction": "urticaria" },
        "confidence": 0.9 }
    ],
    "vaccinations": [
      { "value": { "pathogen": "smallpox", "status": "vaccinated" },
        "date": { "value": "1933", "precision": "year" }, "confidence": 0.7 }
    ],
    "lab_results": [
      { "value": { "panel": "glycated_haemoglobin", "analyte": "hba1c", "result": 41,
                   "unit": "mmol/mol", "reference_high": 42, "flag": "normal" },
        "date": { "value": "2012-06-11", "precision": "exact" },
        "source_id": "c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e6f", "confidence": 0.99 }
    ]
  },
  "genomics": {
    "mt_haplogroup": { "value": { "major": "H", "subclade": "H1a1", "tree_version": "PhyloTree Build 17" },
                       "confidence": 0.9 }
  },
  "death": {
    "date": { "value": "2019-11-02", "precision": "exact" },
    "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
    "confidence": 0.99,
    "time": { "value": "23:15", "confidence": 0.9 },
    "causes": [
      { "value": { "description": "Cardiac arrest", "icd10_chapter": "circulatory", "sequence": 1 },
        "confidence": 0.9 },
      { "value": { "description": "Hypertensive heart disease", "icd10_chapter": "circulatory", "sequence": 2 },
        "confidence": 0.8 }
    ],
    "autopsy": { "value": { "kind": "not_performed" }, "confidence": 0.9 },
    "disposition": [
      { "value": { "method": "burial", "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301" },
        "date": { "value": "2019-11-06", "precision": "exact" }, "confidence": 0.99 }
    ],
    "grave": [
      { "value": { "coordinates": { "lat": 51.2505, "lon": 22.5584, "precision": "grave" },
                   "plot": "kwatera 12, rząd 4, grób 7" }, "confidence": 0.95 }
    ]
  },
  "residence": {
    "addresses": [
      { "value": { "use": "principal", "lines": "ul. Narutowicza 14 m. 3", "postal_code": "20-016",
                   "place_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301", "country": "PL" },
        "valid_from": { "date": { "value": "1958", "precision": "year" } },
        "valid_until": { "date": { "value": "2019-11-02", "precision": "exact" } }, "confidence": 0.9 }
    ],
    "nationality_of_origin": { "value": "PL", "confidence": 0.99 },
    "mother_tongue": [ { "value": "pl", "confidence": 0.99 } ],
    "spoken_languages": [
      { "value": { "language": "ru", "proficiency": "b2" }, "confidence": 0.7 },
      { "value": { "language": "fr", "proficiency": "a2" }, "confidence": 0.5 }
    ]
  },
  "education": {
    "level": [ { "value": "isced_8", "date": { "value": "1961", "precision": "year" }, "confidence": 0.95 } ],
    "diplomas": [
      { "value": { "title": "Doktor nauk medycznych", "isced_level": "isced_8",
                   "institution": "Akademia Medyczna w Lublinie" },
        "date": { "value": "1961", "precision": "year" }, "confidence": 0.95 }
    ],
    "income": [
      { "value": { "quintile": "q4" }, "date": { "value": "1975", "precision": "decade" }, "confidence": 0.4 }
    ]
  },
  "military": {
    "distinctions": [
      { "value": { "name": "Złoty Krzyż Zasługi", "kind": "decoration", "country": "PL" },
        "date": { "value": "1978", "precision": "year" }, "confidence": 0.9 }
    ]
  },
  "belief": {
    "religions": [ { "value": { "tradition": "christianity_catholic", "denomination": "Kościół rzymskokatolicki" },
                     "confidence": 0.9 } ],
    "sacraments": [
      { "value": { "sacrament": "baptism" }, "date": { "value": "1932-04-03", "precision": "exact" },
        "confidence": 0.95 }
    ]
  },
  "personality": {
    "big_five": [
      { "value": { "openness": 72, "conscientiousness": 81, "extraversion": 38, "agreeableness": 64,
                   "neuroticism": 30, "instrument": "observer_rating" },
        "confidence": 0.4, "note": "Rated by her son in 2022 from memory." }
    ],
    "hobbies": [ { "value": "Beekeeping", "confidence": 0.9 } ]
  },
  "digital_legacy": {
    "voice_corpora": [
      { "value": { "document_id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b", "artefact_type": "voice_corpus",
                   "format": "FLAC", "consent": "given_by_estate" },
        "date": { "value": "2021", "precision": "year" }, "confidence": 0.95 }
    ]
  }
}
```

---

## 9. Changelog

| Version | Date | Changes |
|---|---|---|
| 1.1 (draft) | 2026-09 | Extended person profile: fourteen attribute groups, the claim, series, 102 closed vocabularies, four sensitive classes, `identity.class_visibility`, `manifest.privacy.withheld_classes`, Family `children[].lineage`, Link `relation`, Occupation `position`. Additive to 1.0. |
| 1.0 | 2026-06-15 | Initial public draft |

---

## Appendix A — Design Decisions

**A.1 Why every attribute is a claim**  
A blood group with no source is a rumour, and the shape of the data is what makes that visible rather than a matter of discipline. 1.0 already dates, sources and rates every fact it has; an extension that stored a height as a bare number would be a second format inside the first, with a weaker idea of what a fact is. Reusing 1.0's date, source and confidence means a reader that can show the evidence for a birth can show it for a blood pressure without learning anything.

**A.2 Why series and single claims, and why conflicts stay on Source**  
Nearly everything about a body and a life changes, and a format that keeps one value per field forces the recorder to throw the others away. The few attributes that cannot change are single so that "which is it?" has one place to be answered — and when sources disagree about one of those, 1.0 already has the place the disagreement is argued out: the Source's `conflicts[]`. Making every attribute a series would have been simpler to implement and worse to read, because a list of three blood groups is not a record of a disagreement; it is a record that nobody resolved one.

**A.3 Why relationships are not person attributes**  
1.0 is built on four independent entities, and a relationship recorded on the person as well as on the Family would be two records of one fact that will eventually disagree. So *Relationships* adds only what 1.0 could not say: whether a child's parents in a family are biological, adoptive, foster, step or guardians (`lineage`, following GEDCOM's PEDI and extending it), and what a Link is (`relation`). Lineage is per child and family rather than per child and parent because that is how records state it — a stepfather is the partner in a second union, not a second father in the first — and it round-trips with GEDCOM.

**A.4 Why Fitzpatrick rather than von Luschan**  
The von Luschan scale is a set of 36 physical glass tiles matched against the skin. Observers matched the same skin to different tiles, the tiles cannot be reproduced reliably from a document, and the scale was built for and abandoned with racial typology. Fitzpatrick's six phototypes are defined by how skin responds to the sun, can be established from a description rather than an instrument, are in current dermatological use, and have about the resolution a genealogical source can support: no register ever recorded one of 36 tiles, and many recorded "fair" or "dark". The scale is coarse at the dark end and describes response to sunlight rather than colour, which is why a precise colour belongs in a skin texture map (§5.14), not in a finer vocabulary.

**A.5 Why ICD-10 chapters, and not codes or ICD-11**  
A cause of death on an 1890 register is "consumption"; mapping it to a chapter (infectious) is a researcher's judgement a reader can check, and mapping it to A15.0 is a diagnosis nobody made. Chapters are therefore the finest category a genealogical source reliably supports, and conditions use the same vocabulary as causes of death so that one question — "what kind of illness?" — has one set of answers. ICD-10 rather than ICD-11 because mortality statistics and most of the world's existing coded death records use ICD-10's chapters, which have been stable for three decades; the free-text `description` stays beside the chapter either way.

**A.6 Why four sensitive classes, and why belief is in `health`**  
The classes are what an implementation has to be able to withhold separately. Religion, philosophical belief, political opinion and trade-union membership are listed by data-protection law beside health, and genealogists record them constantly without thinking of them that way — a baptism is a statement of religion. They share `health`'s rule, and so share its class, rather than becoming a fifth class that every implementation, export and audit would have to handle and that would protect them by exactly the same rule. The class is named for its largest member.

**A.7 Why genomics of the dead is never public**  
Data protection usually ends at death, and 1.1 follows that for health: a deceased person's class data follows their record. A genome is different because it is not only theirs. A grandmother's pathogenic BRCA1 variant is a probability about each of her descendants, and publishing her genome publishes part of theirs without asking them. So a deceased person's genomic data stays at `members` or tighter.

**A.8 Why artefacts are Documents**  
A mesh, a voice corpus and a trained model are files, sometimes gigabytes of them, and 1.0 already has an entity for a file: it embeds the bytes, records a checksum, says whether the bundle holds it, and links it to any entity. Inlining artefacts would make a person's JSON the size of a film; a bare URL would rot. The reference records what the file *is* to this person, and — because these artefacts are made to imitate a person — whether they consented.

**A.9 Why ranks are per country, and why a category rather than a NATO code**  
A rank is a national institution: a French *caporal* is not an NCO, a Polish *kapral* is, and translating either into the other's word states something false about both. So each registered country has its own vocabulary, with each rank's title in its own language, and 1.1 registers six (FR, PL, DE, GB, US, RU). A rank from anywhere else — or from an army that no longer exists — is `rank_text` until a later version registers that vocabulary. The cross-national comparison is a seven-step `category`, because it is the comparison a genealogical source actually supports; NATO's grade codes are defined for current forces and are misapplied to an imperial army of 1860.

**A.10 Why derived scores are never stored**  
See §4.7. A score computed today from three facts, stored in the bundle, is read in ten years as a fourth fact.

**A.11 Why haplogroups are half closed**  
The major haplogroups are known and stable; their subclades are revised every year as testing finds new branches, so no list of them could stay valid for the life of a bundle. The major clade is therefore a closed vocabulary, and the subclade is a pattern that must begin with it, in ISOGG's notation for Y-DNA and PhyloTree's — which ISOGG adopts — for mtDNA, with `tree_version` recording which revision named it.

---

*AXGF Specification 1.1 (Draft) — September 2026*  
*Released under Creative Commons CC0 1.0 Universal*  
*https://github.com/plkarin/axgf-spec*
