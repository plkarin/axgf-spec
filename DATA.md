# AXGF Data Catalogue

**Everything AXGF can hold about a person, on one page.**

This page is for someone who wants to know whether AXGF can carry what their project needs, without reading the specification to find out. It lists every attribute in [AXGF 1.0](./SPEC_1.0.md) and the [1.1 draft](./SPEC_1.1.md), grouped as the specification groups them, with a short account of what each group is for and what having that data lets a project do.

It is a catalogue, not a second specification. It names attributes and links to where they are defined; it does not define them. The normative text is [SPEC_1.0.md](./SPEC_1.0.md), [SPEC_1.1.md](./SPEC_1.1.md) and the schemas in [`schema/`](./schema/). **If this page and the specification ever disagree, the specification is right and this page is out of date.**

In numbers: **236 attributes** across Person and seven other entities — 100 from 1.0, and 136 added by 1.1: the 132 profile attributes of its fourteen groups and four fields that support them — and **102 closed vocabularies**. The list is checked against the schema by [`tools/check_data_catalogue.py`](./tools/check_data_catalogue.py), in both directions: nothing in the schema is missing from this page, and nothing on this page is missing from the schema.

---

## Every attribute is a claim

**Nothing in AXGF is a bare value.** Every fact about a person is a *claim*: a value together with the date it describes, the source it rests on, and a confidence from 0.0 to 1.0 in how well that source supports it.

```json
{ "value": 158, "date": { "value": "1950", "precision": "year" },
  "source_id": "9b2f0d1e-3c4a-4b5d-8e6f-7a8b9c0d1e2f", "confidence": 0.9,
  "note": "Conscription register, height column." }
```

This is what distinguishes the format, and it applies to every attribute below. A height is not "158"; it is "158, measured in 1950, according to this conscription register, which we trust at 0.9". A blood group recorded without a source is visibly unsourced, and its confidence says how far to trust it. A confidence that is not known is left out, and absent means *unknown* — never certain, never zero ([1.0 §8](./SPEC_1.0.md#8-confidence-model), [1.1 §3.1](./SPEC_1.1.md#31-the-claim)).

Two consequences run through every table on this page:

- **A value that can change in a life is a series, not a single value.** Two heights, two nationalities, three addresses: each is its own dated, sourced claim, and none overwrites another ([1.1 §3.2](./SPEC_1.1.md#32-single-claims-and-series)).
- **Sources that disagree are both kept.** In a series they are two entries; for a single value the disagreement is recorded on the Source, in `conflicts[]` ([1.1 §3.3](./SPEC_1.1.md#33-disagreeing-sources)).

1.0 facts carry the same three fields in the same shapes — a birth has its date, `source_id` and `confidence`, and so do alternate names, unions, Events, Links and Occupations. The handful of fields that describe the *record* rather than the person — who may see it (`visibility`), the living flag, free notes, the AI vault — are not claims about anyone, and the tables show them for completeness.

---

## Sensitive classes

Four classes of attribute describe what is most harmful to disclose about a person. Each such attribute is marked in the **Class** column below and, in the schema, with `x-axgf-class`:

| Class | What it covers |
|---|---|
| `health` | Health, treatment and results — and, with them, religion and belief, political opinion, and union or association membership, which data-protection law treats alike |
| `biometrics` | Measurements and templates of the body or voice that can identify a person |
| `genomics` | DNA tests and sequences, haplogroups, variants, epigenetic and microbiome results |
| `legal` | Criminal proceedings and their outcomes |

The classes are flagged in the schema precisely so that an implementation can govern access to them — grant, withhold, export and audit each class independently of the others — and a conforming implementation is expected to. By default a living person's class data is visible to administrators only, and a dead person's genome is never public, because it is part of every living descendant's. The rules are in [1.1 §4](./SPEC_1.1.md#4-sensitive-classes).

A class follows the data, not the group: *Motor tics* sit in Biometrics and are `health`; *Belief and affiliation* is `health` throughout.

---

## Reading the tables

| Column | Meaning |
|---|---|
| **Attribute** | What is recorded. |
| **Path** | Where it lives in the JSON. Relative to the Person unless it names another entity (`Family.…`, `Link.…`). |
| **Type** | The shape of the value: *term* (one word from a closed vocabulary), *text*, a number with its fixed unit, *record* (several fields), *artefact reference* (a Document holding a file), a *date*, a *reference* to another entity. |
| **Vocabulary** | The closed vocabularies the value draws on, each linked to where the schema enumerates it; *free text* where part of the value is the source's own words. |
| **Kind** | *single* — one value, fixed at birth or by one event; *series* — dated claims over a lifetime; *list* — several values at once, such as a person's documents. |
| **Class** | Sensitive class, or — for none. |
| **Since** | The version that introduced the attribute: 1.0, or the 1.1 draft. |
| **Spec** | The section that defines it. |

---

## Contents

**Person**

1. [Identity and civil status](#1-identity-and-civil-status)
2. [Morphology](#2-morphology)
3. [Biometrics](#3-biometrics)
4. [Health](#4-health)
5. [Genomics](#5-genomics)
6. [Death](#6-death)
7. [Residence and nationality](#7-residence-and-nationality)
8. [Education and work](#8-education-and-work)
9. [Military and honours](#9-military-and-honours)
10. [Legal](#10-legal)
11. [Belief and affiliation](#11-belief-and-affiliation)
12. [Personality and behaviour](#12-personality-and-behaviour)
13. [Relationships](#13-relationships)
14. [Digital legacy](#14-digital-legacy)
15. [Narrative, documents and AI](#15-narrative-documents-and-ai)

**The other entities**

[Family](#family) · [Event](#event) · [Link](#link) · [Occupation](#occupation) · [Source](#source) · [Place](#place) · [Document](#document)

[Closed vocabularies](#closed-vocabularies) · [Keeping this page true](#keeping-this-page-true)

---

## Person

A Person is the atomic entity of AXGF. It exists on its own — a person with nothing known but a place in a tree is valid — and it does not contain their relationships: parents, spouses, children and friends live on Family and Link, which are entities in their own right ([1.0 §4.1](./SPEC_1.0.md#41-person), [P1](./SPEC_1.0.md#11-core-philosophy)).

1.1 organises the person into fourteen groups ([1.1 §5](./SPEC_1.1.md#5-attribute-groups)). They are an organisation, not a JSON structure: most are one block on Person, but *Identity and civil status* spans three, *Death* extends 1.0's `death`, and *Relationships* lives entirely on Family and Link.

### 1. Identity and civil status

What the record says the person is called, how they were registered, and where the registers say so. Names, gender, birth date and birth place are 1.0; 1.1 adds titles, sex at birth and gender identity as separate facts from the record's gender, the precise time and point of birth, and the register entries themselves.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Name | `identity.name` | multilingual name | closed component types | single | — | 1.0 | [1.0 §5.1](./SPEC_1.0.md#51-name) |
| Other names — birth, married, alias, nickname, religious, pen name | `identity.names` | multilingual name | closed name types | list | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Gender of the record | `identity.gender` | term + note | closed + free text | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Living | `identity.is_living` | boolean | — | single | — | 1.0 | [1.0 §9.2](./SPEC_1.0.md#92-living-persons) |
| Record visibility | `identity.visibility` | term | closed | single | — | 1.0 | [1.0 §9.1](./SPEC_1.0.md#91-visibility-levels) |
| Titles | `identity.titles` | record | [`title_kind`][v-title_kind] + free text | series | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Sex at birth | `identity.sex_at_birth` | term | [`sex_at_birth`][v-sex_at_birth] | single | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Gender identity | `identity.gender_identity` | term | [`gender_identity`][v-gender_identity] | series | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Per-class visibility for this person | `identity.class_visibility` | map of class → visibility | [`sensitive_class`][v-sensitive_class] | single | — | 1.1 | [§4.4](./SPEC_1.1.md#44-per-person-class-visibility) |
| Birth date | `birth.date` | date | — | single | — | 1.0 | [1.0 §5.2](./SPEC_1.0.md#52-date) |
| Birth place | `birth.place_id` | reference → Place | — | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Birth: confidence | `birth.confidence` | confidence 0–1 | — | single | — | 1.0 | [1.0 §8](./SPEC_1.0.md#8-confidence-model) |
| Birth: source | `birth.source_id` | reference → Source | — | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Birth: event | `birth.event_id` | reference → Event | — | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Birth time | `birth.time` | time of day | — | single | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Birth coordinates | `birth.coordinates` | coordinates | — | single | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Birth certificate number | `civil_status.birth_certificate_number` | text | free text | single | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Civil register entries | `civil_status.register_entries` | record | [`register_type`][v-register_type] + free text | series | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |
| Marginal annotations | `civil_status.marginal_annotations` | record | [`register_type`][v-register_type] + free text | series | — | 1.1 | [§5.1](./SPEC_1.1.md#511-attributes) |

**What it enables.** A name is held as its components in its own script, with a Latin transliteration and a reading for each, so a Japanese, Hebrew or Arabic name is stored as written and still found by someone who cannot read it. Keeping the record's gender, the sex registered at birth and a person's own dated gender identity as three separate facts lets a record say what each source said without one overwriting another. Register entries and their marginal annotations — the later marriage, divorce or death written beside a birth act — are how civil-registration research actually proceeds: holding the volume, page and entry number lets another researcher go back to the same line of the same register, and a project indexing parish or civil registers has somewhere to put what it transcribes.

### 2. Morphology

What the person's body looked like: stature and weight, eyes, hair, skin, face, teeth, posture and gait, and the marks by which someone could be recognised. Almost all of it is a series, because a child's body and an adult's are different facts.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Height | `morphology.height` | number (cm) | — | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Weight | `morphology.weight` | number (kg) | — | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| BMI, as a source states it | `morphology.bmi` | number (kg/m²) | — | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Body composition | `morphology.body_composition` | record (%) | — | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Build | `morphology.build` | term | [`build`][v-build] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Eye colour | `morphology.eye_colour` | term | [`eye_colour`][v-eye_colour] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Eye shape | `morphology.eye_shape` | term | [`eye_shape`][v-eye_shape] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Eye spacing | `morphology.eye_spacing` | term | [`eye_spacing`][v-eye_spacing] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Natural hair colour | `morphology.hair_colour` | term | [`hair_colour`][v-hair_colour] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Hair texture | `morphology.hair_texture` | term | [`hair_texture`][v-hair_texture] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Hairline | `morphology.hairline` | term | [`hairline`][v-hairline] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Facial hair | `morphology.facial_hair` | term | [`facial_hair`][v-facial_hair] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Body hair | `morphology.body_hair` | term | [`body_hair`][v-body_hair] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Skin tone (Fitzpatrick) | `morphology.skin_tone` | term | [`skin_tone`][v-skin_tone] | single | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Skin undertone | `morphology.skin_undertone` | term | [`skin_undertone`][v-skin_undertone] | single | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Freckles | `morphology.freckles` | term | [`freckles`][v-freckles] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Pigmentation marks | `morphology.pigmentation` | record | [`body_region`][v-body_region], [`pigmentation_mark`][v-pigmentation_mark] + free text | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Scars | `morphology.scars` | record | [`body_region`][v-body_region] + free text | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Tattoos | `morphology.tattoos` | record | [`body_region`][v-body_region] + free text | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Moles, with location and shape | `morphology.moles` | record (mm) | [`body_region`][v-body_region], [`mole_shape`][v-mole_shape] + free text | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Facial asymmetries | `morphology.facial_asymmetries` | text | free text | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Face shape | `morphology.face_shape` | term | [`face_shape`][v-face_shape] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Nose shape | `morphology.nose_shape` | term | [`nose_shape`][v-nose_shape] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Ear shape | `morphology.ear_shape` | term | [`ear_shape`][v-ear_shape] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Lip shape | `morphology.lip_shape` | term | [`lip_shape`][v-lip_shape] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Dentition | `morphology.dentition` | term | [`dentition`][v-dentition] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Dental malocclusion (Angle class) | `morphology.malocclusion` | term | [`malocclusion`][v-malocclusion] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Posture | `morphology.posture` | term | [`posture`][v-posture] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Gait | `morphology.gait` | term | [`gait`][v-gait] | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |
| Distinguishing features | `morphology.distinguishing_features` | text | free text | series | — | 1.1 | [§5.2](./SPEC_1.1.md#521-attributes) |

**What it enables.** This is what a researcher reading a conscription register, a passport, a prison ledger or a seaman's book already has in front of them — height, eyes, hair, complexion, scars and "distinguishing marks" — and until now had nowhere to put except a note. Held as dated, sourced claims in fixed units and shared vocabularies, descriptions of one man from two registers thirty years apart can be compared rather than reread, and the same comparison can be run across a lineage: who in a family was tall, whose eyes were recorded as blue. It is also the descriptive half of what a physical reconstruction — a portrait, a model — would need, alongside the scans and textures in [Digital legacy](#14-digital-legacy).

### 3. Biometrics

The identifying measures of the body and voice — fingerprints, retina, voiceprint, the pitch, timbre and rate of speech — and how the person spoke, moved and perceived: accent, tics, register of speech, handedness, hearing and sight.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Fingerprints | `biometrics.fingerprints` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Retinal print | `biometrics.retinal_print` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Voice signature | `biometrics.voice_signature` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Fundamental voice frequency | `biometrics.voice_frequency` | number (Hz) | — | series | `biometrics` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Vocal timbre | `biometrics.vocal_timbre` | term | [`vocal_timbre`][v-vocal_timbre] | series | `biometrics` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Spoken accent | `biometrics.spoken_accent` | record | free text | series | — | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Speech rate | `biometrics.speech_rate` | number (words/min) | — | series | `biometrics` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Verbal tics | `biometrics.verbal_tics` | text | free text | series | — | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Frequent vocabulary | `biometrics.frequent_vocabulary` | text | free text | series | — | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Register of speech | `biometrics.speech_register` | term | [`speech_register`][v-speech_register] | series | — | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Motor tics | `biometrics.motor_tics` | text | free text | series | `health` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Handedness | `biometrics.handedness` | term | [`handedness`][v-handedness] | series | — | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Hearing | `biometrics.hearing` | record (dB HL) | [`hearing_grade`][v-hearing_grade], [`laterality`][v-laterality] | series | `health` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Visual acuity | `biometrics.visual_acuity` | record | [`laterality`][v-laterality] | series | `health` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |
| Optical correction | `biometrics.optical_correction` | record | [`optical_correction`][v-optical_correction] + free text | series | `health` | 1.1 | [§5.3](./SPEC_1.1.md#531-attributes) |

**What it enables.** Biometric attributes carry what identifies a body rather than a life. A fingerprint card from a police or immigration file, a retinal image or a voiceprint is held as a reference to the Document that contains it, with a record of whether the person — or after their death, whoever could — consented to it being kept. The voice measures are what a reconstruction project would need: pitch in hertz, timbre, rate and register, with the accent and the phrases a family remembers as "the way she spoke". Handedness, hearing and eyesight turn up in school, military and medical records and are the kind of trait families wonder whether they share.

### 4. Health

Blood group, vital measurements, diagnoses, operations and injuries, what was implanted or prescribed, allergies, vaccinations, serology, laboratory results, deficiencies, sleep disorders and mental-health assessments. The whole group is in the `health` class.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Blood group (ABO) | `health.blood_group` | term | [`blood_group`][v-blood_group] | single | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Rhesus | `health.rhesus` | term | [`rhesus`][v-rhesus] | single | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Blood pressure | `health.blood_pressure` | record (mmHg) | — | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Resting heart rate | `health.resting_heart_rate` | integer (bpm) | — | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Respiratory capacity (FEV1/FVC) | `health.respiratory_capacity` | record (L) | — | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Conditions — chronic, autoimmune, oncological, psychiatric and others | `health.conditions` | record | [`diagnosis_status`][v-diagnosis_status], [`icd10_chapter`][v-icd10_chapter] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Surgical history | `health.surgeries` | record | [`body_region`][v-body_region] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Injuries and fracture sequelae | `health.injuries` | record | [`body_region`][v-body_region] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Physical deformities | `health.deformities` | record | [`body_region`][v-body_region] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Amputations | `health.amputations` | record | [`body_region`][v-body_region] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Prostheses | `health.prostheses` | record | [`prosthesis_kind`][v-prosthesis_kind] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Biomedical implants | `health.implants` | record | [`implant_kind`][v-implant_kind] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Pacemakers and other intracorporeal devices | `health.devices` | record | [`device_kind`][v-device_kind] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Long-term medication | `health.medications` | record | free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Allergies — drug, food, environmental | `health.allergies` | record | [`allergy_severity`][v-allergy_severity], [`allergy_type`][v-allergy_type] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Vaccinations | `health.vaccinations` | record | [`pathogen`][v-pathogen], [`vaccination_status`][v-vaccination_status] | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Serology | `health.serology` | record | [`pathogen`][v-pathogen], [`serology_result`][v-serology_result] | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Laboratory results — metabolic, lipid, liver, renal, HbA1c, iron | `health.lab_results` | record (UCUM unit per result) | [`lab_analyte`][v-lab_analyte], [`lab_flag`][v-lab_flag], [`lab_panel`][v-lab_panel], [`lab_unit`][v-lab_unit] | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Vitamin and mineral deficiencies | `health.deficiencies` | record | [`nutrient`][v-nutrient] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Sleep disorders | `health.sleep_disorders` | record | [`sleep_disorder`][v-sleep_disorder] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |
| Mental-health assessments | `health.mental_health_assessments` | record | [`assessment_instrument`][v-assessment_instrument], [`assessment_severity`][v-assessment_severity] + free text | series | `health` | 1.1 | [§5.4](./SPEC_1.1.md#541-attributes) |

**What it enables.** A family medical history is the most practical thing genealogy produces, and the one most often kept as scattered anecdote. Diagnoses coded to ICD-10 chapters beside the source's own words — "consumption" beside *infectious* — let conditions be compared across generations and centuries without claiming a precision the source never had. Blood pressure, laboratory values and vaccinations held as dated series are the shape a clinician-facing family history or a cohort study would need. Because every entry carries its source and confidence, "grandmother had diabetes, according to a cousin" and "HbA1c of 8.1% on a 1998 hospital report" stay distinguishable — and because the group is a sensitive class, holding it does not mean showing it.

### 5. Genomics

DNA tests and sequences, haplogroups, variants and hereditary conditions, predispositions, epigenetic markers and biological age, microbiomes, and inherited sensitivities to substances. The whole group is in the `genomics` class.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Autosomal DNA test | `genomics.autosomal_mapping` | record | [`reference_build`][v-reference_build] + free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Y-DNA haplogroup | `genomics.y_haplogroup` | record | [`y_haplogroup`][v-y_haplogroup] + free text | single | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Mitochondrial haplogroup | `genomics.mt_haplogroup` | record | [`mt_haplogroup`][v-mt_haplogroup] + free text | single | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Whole-genome sequencing | `genomics.whole_genome_sequencing` | record (x coverage) | [`genomic_file_format`][v-genomic_file_format], [`reference_build`][v-reference_build] + free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Risk variants | `genomics.risk_variants` | record | [`clinical_significance`][v-clinical_significance], [`zygosity`][v-zygosity] + free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Hereditary conditions | `genomics.hereditary_conditions` | record | [`carrier_status`][v-carrier_status], [`inheritance_pattern`][v-inheritance_pattern] + free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Genetic predispositions | `genomics.predispositions` | record | free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Epigenetic markers | `genomics.epigenetic_markers` | record | free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Epigenetic age | `genomics.epigenetic_age` | record (years) | [`epigenetic_clock`][v-epigenetic_clock] | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Gut microbiome | `genomics.gut_microbiome` | record | free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Skin microbiome | `genomics.skin_microbiome` | record | free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |
| Toxicological sensitivities | `genomics.toxicological_sensitivities` | record | [`metaboliser_status`][v-metaboliser_status] + free text | series | `genomics` | 1.1 | [§5.5](./SPEC_1.1.md#551-attributes) |

**What it enables.** Haplogroups place a lineage on the human migration tree and are the bridge between documentary genealogy and genetic genealogy: a Y-DNA haplogroup confirms or breaks a paternal line that the registers claim, and the major clade is a closed vocabulary (ISOGG, PhyloTree) so that two families' results can be compared at all. Test records point at the raw data as a Document and name the reference build it was aligned to, so the file can be reinterpreted later. Match-level evidence — shared centimorgans between two testers — is on the [Source](#source), where it supports a relationship. Variants, carrier status and inheritance pattern are what a family would need to follow a hereditary condition down a tree; because a dead person's genome is part of every living descendant's, it is never public.

### 6. Death

When, where and how the person died, and what became of the body. Date, place and the free-text cause are 1.0; 1.1 adds the time and exact point of death, coded causes in sequence, contributing factors, the autopsy, the disposition of the body and the grave.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Death date | `death.date` | date | — | single | — | 1.0 | [1.0 §5.2](./SPEC_1.0.md#52-date) |
| Death place | `death.place_id` | reference → Place | — | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Cause of death, as written | `death.cause` | text | free text | single | `health` | 1.0 | [§4.1](./SPEC_1.1.md#41-the-four-classes) |
| Death: confidence | `death.confidence` | confidence 0–1 | — | single | — | 1.0 | [1.0 §8](./SPEC_1.0.md#8-confidence-model) |
| Death: source | `death.source_id` | reference → Source | — | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Death: event | `death.event_id` | reference → Event | — | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Death time | `death.time` | time of day | — | single | — | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |
| Death coordinates | `death.coordinates` | coordinates | — | single | — | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |
| Direct causes, in sequence | `death.causes` | record | [`icd10_chapter`][v-icd10_chapter] + free text | series | `health` | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |
| Contributing factors | `death.contributing_factors` | record | [`icd10_chapter`][v-icd10_chapter] + free text | series | `health` | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |
| Autopsy or forensic report | `death.autopsy` | record | [`autopsy`][v-autopsy] + free text | single | `health` | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |
| Burial, cremation or other disposition | `death.disposition` | record | [`disposition`][v-disposition] | series | — | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |
| Grave — coordinates, plot, inscription | `death.grave` | record | free text | series | — | 1.1 | [§5.6](./SPEC_1.1.md#561-attributes) |

**What it enables.** Causes of death coded to the same ICD-10 chapters as conditions in life mean one question — "what did people in this family die of?" — has one set of answers across two centuries of certificates, and a chain of causes keeps "pneumonia following a fracture" from being flattened to either. The grave's coordinates, plot and inscription are what a cemetery survey records and what a descendant needs to find a stone; disposition and grave are series because remains are sometimes moved and graves relocated. A cause of death from 1850 is the substance of genealogy, so a dead person's health data follows their record's own visibility.

### 7. Residence and nationality

Where the person lived, which nationalities they held and how they acquired them, and the languages they spoke.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Addresses, principal and over time | `residence.addresses` | record | [`address_use`][v-address_use], [`country`][v-country] + free text | series | — | 1.1 | [§5.7](./SPEC_1.1.md#571-attributes) |
| Nationality of origin | `residence.nationality_of_origin` | term | [`country`][v-country] | single | — | 1.1 | [§5.7](./SPEC_1.1.md#571-attributes) |
| Acquired nationalities | `residence.acquired_nationalities` | record | [`country`][v-country], [`nationality_mode`][v-nationality_mode] | series | — | 1.1 | [§5.7](./SPEC_1.1.md#571-attributes) |
| Mother tongue | `residence.mother_tongue` | language tag | — | series | — | 1.1 | [§5.7](./SPEC_1.1.md#571-attributes) |
| Spoken languages, with proficiency | `residence.spoken_languages` | record | [`language_proficiency`][v-language_proficiency] | series | — | 1.1 | [§5.7](./SPEC_1.1.md#571-attributes) |

**What it enables.** An address history is how records are found: censuses, directories and electoral rolls are searched by where someone lived and when. Nationality held as a series, with how each was acquired — by descent, naturalisation, marriage or a border moving across the person's home — is the evidence citizenship-by-descent applications turn on, and it records honestly the people who changed nationality without moving. Countries are ISO codes plus the historical ones (`SU`, `YU`, `CS`, `DD`, `OT`), so a subject of the Ottoman Empire is not recorded as a citizen of a state founded after they died. Languages with CEFR proficiency say what a family spoke at home and when it stopped.

### 8. Education and work

Schooling and qualifications, occupations and the posts held in them, income and property.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Education level (ISCED 2011) | `education.level` | term | [`isced_level`][v-isced_level] | series | — | 1.1 | [§5.8](./SPEC_1.1.md#581-attributes) |
| Diplomas | `education.diplomas` | record | [`isced_level`][v-isced_level] + free text | series | — | 1.1 | [§5.8](./SPEC_1.1.md#581-attributes) |
| Institutions attended | `education.institutions` | record | [`isced_level`][v-isced_level] + free text | series | — | 1.1 | [§5.8](./SPEC_1.1.md#581-attributes) |
| Income | `education.income` | record | [`income_quintile`][v-income_quintile], [`pay_period`][v-pay_period] | series | — | 1.1 | [§5.8](./SPEC_1.1.md#581-attributes) |
| Real estate held | `education.real_estate` | record | [`tenure`][v-tenure] + free text | series | — | 1.1 | [§5.8](./SPEC_1.1.md#581-attributes) |
| Position held in an occupation | `Occupation.position` | text | free text | single | — | 1.1 | [§5.8](./SPEC_1.1.md#581-attributes) |

Occupations themselves and successive employers are 1.0 [Occupation](#occupation) entities, each dated with its own source; `position` is the one field 1.1 adds to them.

**What it enables.** Occupations as dated states with employers, rather than a single word on a death certificate, give a working life its shape — apprentice, journeyman, master; clerk, then manager — and let a study follow social mobility across generations. Education mapped to ISCED levels makes a Polish *gimnazjum* and a French *lycée* comparable without pretending they were the same school. Income is held either as an amount in its historical currency or as a quintile, because a source that says "well-off" supports a quintile and nothing more. Property with its tenure is the material behind land and inheritance research.

### 9. Military and honours

Service, ranks, units and service numbers, citations, and distinctions — military or civil.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Distinctions — orders, decorations, medals, titles | `military.distinctions` | record | [`country`][v-country], [`distinction_kind`][v-distinction_kind] + free text | series | — | 1.1 | [§5.9](./SPEC_1.1.md#591-attributes) |
| Citations | `military.citations` | record | free text | series | — | 1.1 | [§5.9](./SPEC_1.1.md#591-attributes) |
| Ranks | `military.ranks` | record | [`country`][v-country], [`military_rank_de`][v-military_rank_de], [`military_rank_fr`][v-military_rank_fr], [`military_rank_gb`][v-military_rank_gb], [`military_rank_pl`][v-military_rank_pl], [`military_rank_ru`][v-military_rank_ru], [`military_rank_us`][v-military_rank_us], [`military_service`][v-military_service], [`rank_category`][v-rank_category] + free text | series | — | 1.1 | [§5.9](./SPEC_1.1.md#591-attributes) |
| Units and regiments | `military.units` | text | free text | series | — | 1.1 | [§5.9](./SPEC_1.1.md#591-attributes) |
| Service numbers | `military.service_numbers` | record | [`country`][v-country], [`military_service`][v-military_service] + free text | series | — | 1.1 | [§5.9](./SPEC_1.1.md#591-attributes) |

**What it enables.** Service numbers and units are the keys to military archives — the number is how a service file is requested, and the regiment is how a war diary is found. Ranks are recorded in each army's own vocabulary and language (six countries registered so far, free text for any other or for armies that no longer exist), with a seven-step category beside them, so a researcher can compare a French *caporal* and a Polish *kapral* without stating that they were the same thing. Series of ranks and units trace a career through promotions and transfers, and let two men of the same name be told apart.

### 10. Legal

Criminal proceedings and their outcomes. In the `legal` class.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Criminal record | `legal.criminal_record` | record | [`case_outcome`][v-case_outcome], [`country`][v-country], [`iccs_section`][v-iccs_section] + free text | series | `legal` | 1.1 | [§5.10](./SPEC_1.1.md#5101-attributes) |

**What it enables.** Court and prison records are among the richest sources on ordinary lives, and among the most sensitive. Holding the offence as the source wrote it, beside its UN ICCS section, the jurisdiction, court, outcome and sentence, lets a family record a transportation, a political imprisonment or a later pardon accurately — including that a conviction was quashed or expunged — and lets it be withheld from readers who may see the rest of the record. Its own class means a conviction can be shown to a family historian without showing them anyone's diagnoses.

### 11. Belief and affiliation

Religion and the rites received, individual beliefs, political leanings, and membership of unions and associations. In the `health` class throughout, because data-protection law protects these alongside health.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Religion | `belief.religions` | record | [`religion`][v-religion] + free text | series | `health` | 1.1 | [§5.11](./SPEC_1.1.md#5111-attributes) |
| Sacraments and rites received | `belief.sacraments` | record | [`sacrament`][v-sacrament] | series | `health` | 1.1 | [§5.11](./SPEC_1.1.md#5111-attributes) |
| Individual beliefs | `belief.beliefs` | text | free text | series | `health` | 1.1 | [§5.11](./SPEC_1.1.md#5111-attributes) |
| Political leanings | `belief.political_leanings` | record | [`political_position`][v-political_position] + free text | series | `health` | 1.1 | [§5.11](./SPEC_1.1.md#5111-attributes) |
| Union and association memberships | `belief.memberships` | record | [`membership_kind`][v-membership_kind] + free text | series | `health` | 1.1 | [§5.11](./SPEC_1.1.md#5111-attributes) |

**What it enables.** Religion decides which records exist — a parish register, a synagogue's book, a mosque's — and a conversion, held as a series, explains why a family disappears from one set of records and appears in another. Sacraments and rites held as dated facts are often the only dates a parish register gives: a baptism stands in for a birth, a burial for a death. Memberships of guilds, unions, lodges and parties connect a person to the organisations whose archives may name them. Genealogists record these constantly without thinking of them as sensitive; the class makes sure an implementation does.

### 12. Personality and behaviour

Temperament, personality measures, interests and hobbies, sport, diet, and dependencies.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Big Five traits | `personality.big_five` | record | [`personality_instrument`][v-personality_instrument] | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| MBTI type | `personality.mbti` | term | [`mbti`][v-mbti] | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Introversion and extraversion | `personality.introversion_extraversion` | term | [`introversion_extraversion`][v-introversion_extraversion] | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Stress tolerance | `personality.stress_tolerance` | term | [`stress_tolerance`][v-stress_tolerance] | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Decision-making style | `personality.decision_style` | term | [`decision_style`][v-decision_style] | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Interests | `personality.interests` | text | free text | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Hobbies | `personality.hobbies` | text | free text | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Sports | `personality.sports` | record | [`sport_level`][v-sport_level] + free text | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Dietary habits | `personality.dietary_habits` | record | [`diet`][v-diet] + free text | series | — | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |
| Dependencies — tobacco, alcohol, substances, behaviours | `personality.dependencies` | record | [`substance`][v-substance], [`use_pattern`][v-use_pattern] | series | `health` | 1.1 | [§5.12](./SPEC_1.1.md#5121-attributes) |

**What it enables.** Behavioural and personality attributes exist because a record of what someone was like is as much a part of who they were as their dates. Held as dated, sourced claims with explicit confidence, they can support research into how traits recur across a lineage, and they are the foundation a digital-legacy project would need — one where a living person records their own traits for descendants, or where an interactive persona is built from what a family actually recorded rather than from invention. The format's insistence that every claim carries its confidence matters here more than anywhere: a personality inferred from one anecdote and one attested from a lifetime of letters must not look alike, and the Big Five record names the instrument — a published inventory, an observer's rating, or `inferred` — so the difference is in the data, not in a footnote. The group has no class of its own, but about a living person it amounts to a psychological profile, and the specification asks implementations to treat it as sensitive ([§4.6](./SPEC_1.1.md#46-behavioural-profiles-of-living-persons)).

### 13. Relationships

Parents, siblings, spouses, children, godparents, witnesses, business partners and friends. **None of these is a field on Person.** Relationships are entities — [Family](#family) and [Link](#link) — with their own dates, sources and confidence, so that a relationship can be questioned or ended without editing either person. 1.1 adds two fields to those entities:

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Lineage of a child in a family | `Family.children[].lineage` | term | [`lineage`][v-lineage] | single | — | 1.1 | [§5.13](./SPEC_1.1.md#513-relationships) |
| Typed relation of a Link | `Link.relation` | term | [`link_relation`][v-link_relation] | single | — | 1.1 | [§5.13](./SPEC_1.1.md#513-relationships) |

Where each relationship is recorded ([§5.13.1](./SPEC_1.1.md#5131-attributes)):

- **Parents** — the partners of a Family in which the person is a child; the child's `lineage` says biological, adoptive, foster, step or guardians.
- **Siblings and birth order** — the other children of the same Family, with `birth_order`.
- **Spouses, marriages, divorces** — the Family's `union`: its partners, type, start and end.
- **Children** — the children of the Families in which the person is a partner.
- **Godparents, witnesses, officiants, employers, business partners, friends** — Links, typed by `relation` beside the source's own word in `label`.

**What it enables.** Because a parent–child relationship belongs to a family and carries its own lineage, a tree can show a stepfather, an adoptive mother and a biological father without contradiction, and a pedigree can be drawn by blood or by upbringing. Links with typed relations and dates record the networks — godparents, witnesses at weddings, employers, neighbours — that researchers use to break through brick walls, since the same names recur around a family long before a document states how they were related.

### 14. Digital legacy

Files made from or about the person: body scans and models, skin textures, rigs, voice and text corpora, archives of their online life, trained behaviour models — and an estimate of their carbon footprint.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| 3D body model — mesh or point cloud | `digital_legacy.body_models` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Skin texture map | `digital_legacy.skin_textures` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Skeletal and joint rig | `digital_legacy.rigs` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Voice corpus for synthesis | `digital_legacy.voice_corpora` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | `biometrics` | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Written corpus for a language model | `digital_legacy.text_corpora` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | — | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Digital trace archive | `digital_legacy.digital_traces` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | — | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Estimated carbon footprint | `digital_legacy.carbon_footprint` | record (t CO2e/yr) | free text | series | — | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |
| Behaviour model | `digital_legacy.behaviour_models` | artefact reference | [`artefact_type`][v-artefact_type], [`consent`][v-consent] | series | — | 1.1 | [§5.14](./SPEC_1.1.md#5141-attributes) |

**What it enables.** Scans, voice recordings, letters and account exports are now part of what a person leaves, and they are large, fragile and easily separated from whom they depict. Held as Documents in the bundle, each is checksummed, linked to the person, says whether the file is actually present, records what it was derived from — a rig from a mesh, a model from a corpus — and whether the person or their estate consented. That is what a digital-legacy or reconstruction project would need in order to keep its inputs with the family record rather than on a vendor's server, and to be able to show where a synthetic voice or persona came from. A behaviour model of a living person is, in the specification's words, a psychological profile in executable form, and is expected to be governed as one.

### 15. Narrative, documents and AI

The rest of the 1.0 Person record: free narrative, the documents linked to the person, and the optional AI section — a Markdown vault page and hypotheses awaiting review.

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Biography | `bio` | text | free text | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Notes | `notes` | text | free text | single | — | 1.0 | [1.0 §4.1](./SPEC_1.0.md#41-person) |
| Linked documents, with their role | `documents` | reference → Document | — | list | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Vault page | `ai.vault_page` | path | — | single | — | 1.0 | [1.0 §7.1](./SPEC_1.0.md#71-vault-section) |
| Embedding model | `ai.embedding_model` | text | — | single | — | 1.0 | [1.0 §7.3](./SPEC_1.0.md#73-embedding-metadata) |
| Embedding updated | `ai.embedding_updated_at` | timestamp | — | single | — | 1.0 | [1.0 §7.3](./SPEC_1.0.md#73-embedding-metadata) |
| AI hypotheses | `ai.hypotheses` | record | closed status + free text | list | — | 1.0 | [1.0 §7.2](./SPEC_1.0.md#72-hypothesis-status) |

**What it enables.** A hypothesis — "probably the Jan Kowalski baptised in 1871" — is kept apart from established fact, with its confidence, its evidence and a status that moves from *pending* to *confirmed* or *rejected* when someone reviews it. Research in progress can therefore live in the same file as the finished tree without contaminating it, whether the hypothesis came from a person or a program. The vault page is a readable narrative of the person that a language model or a human can use directly.

---

## The other entities

A bundle holds eight kinds of entity. Person is one; the other seven are listed here in summary, because what AXGF can hold about a person includes what it holds *around* them. Each is its own file with its own identity: a relationship, an event or a job is never a field buried inside a person.

### Family

A structural group: a union of any number of partners (or none known), and the children of it, each with their birth order and lineage. A Family has its own documents and history, and exists even when its members are unknown ([1.0 §4.2](./SPEC_1.0.md#42-family)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Family name | `Family.name` | text | free text | single | — | 1.0 | [1.0 §4.2](./SPEC_1.0.md#42-family) |
| Description | `Family.description` | text | free text | single | — | 1.0 | [1.0 §4.2](./SPEC_1.0.md#42-family) |
| Union — partners, type, status, start, end, source, confidence | `Family.union` | record | closed union type and status | single | — | 1.0 | [1.0 §4.2.1](./SPEC_1.0.md#421-union-types) |
| Children, with birth order and confidence | `Family.children` | record | — | list | — | 1.0 | [1.0 §4.2](./SPEC_1.0.md#42-family) |
| Documents | `Family.documents` | reference → Document | — | list | — | 1.0 | [1.0 §4.2](./SPEC_1.0.md#42-family) |
| Notes | `Family.notes` | text | free text | single | — | 1.0 | [1.0 §4.2](./SPEC_1.0.md#42-family) |
| AI vault page | `Family.ai` | record | — | single | — | 1.0 | [1.0 §7.1](./SPEC_1.0.md#71-vault-section) |

A child's `lineage` is listed under [Relationships](#13-relationships).

**What it enables.** Polygamous unions, sibling groups whose parents are unknown, unions that ended by death, divorce or annulment, and families in which some children are adopted — all expressible without inventing a person or a marriage that the records do not show.

### Event

A dated fact with any number of participants, each in a typed role — a baptism with its godparents and priest, a census with its household, an emigration with everyone who left together ([1.0 §4.3](./SPEC_1.0.md#43-event)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Category | `Event.category` | term | closed event categories | single | — | 1.0 | [1.0 §4.3.1](./SPEC_1.0.md#431-event-categories) |
| Subcategory | `Event.subcategory` | text | free text | single | — | 1.0 | [1.0 §4.3](./SPEC_1.0.md#43-event) |
| Date | `Event.date` | date | — | single | — | 1.0 | [1.0 §5.2](./SPEC_1.0.md#52-date) |
| Place | `Event.place_id` | reference → Place | — | single | — | 1.0 | [1.0 §4.3](./SPEC_1.0.md#43-event) |
| Participants, with roles | `Event.participants` | record | free-text role | list | — | 1.0 | [1.0 §4.3](./SPEC_1.0.md#43-event) |
| Description | `Event.description` | text | free text | single | — | 1.0 | [1.0 §4.3](./SPEC_1.0.md#43-event) |
| Documents | `Event.documents` | reference → Document | — | list | — | 1.0 | [1.0 §4.3](./SPEC_1.0.md#43-event) |
| Confidence | `Event.confidence` | confidence 0–1 | — | single | — | 1.0 | [1.0 §8](./SPEC_1.0.md#8-confidence-model) |
| Source | `Event.source_id` | reference → Source | — | single | — | 1.0 | [1.0 §4.3](./SPEC_1.0.md#43-event) |
| AI vault page | `Event.ai` | record | — | single | — | 1.0 | [1.0 §7.1](./SPEC_1.0.md#71-vault-section) |

**What it enables.** One event recorded once, with everyone who was there: the witnesses at a wedding are participants of the marriage, not a note on the bride. A migration, a naturalisation or an imprisonment is a fact that happened to several people at once, and can be found from any of them.

### Link

A typed, directed relationship between any two persons, families or events, with its own period of validity, source, confidence and visibility ([1.0 §4.4](./SPEC_1.0.md#44-link)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| From | `Link.from` | reference → Person, Family or Event | — | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| To | `Link.to` | reference → Person, Family or Event | — | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Label, in the source's words | `Link.label` | text | free text | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Reverse label | `Link.label_reverse` | text | free text | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Category | `Link.category` | term | closed link categories | single | — | 1.0 | [1.0 §4.4.1](./SPEC_1.0.md#441-link-categories) |
| Bidirectional | `Link.bidirectional` | boolean | — | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Valid from | `Link.valid_from` | date or Event | — | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Valid until | `Link.valid_until` | date or Event | — | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Confidence | `Link.confidence` | confidence 0–1 | — | single | — | 1.0 | [1.0 §8](./SPEC_1.0.md#8-confidence-model) |
| Source | `Link.source_id` | reference → Source | — | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Note | `Link.note` | text | free text | single | — | 1.0 | [1.0 §4.4](./SPEC_1.0.md#44-link) |
| Visibility | `Link.visibility` | term | closed | single | — | 1.0 | [1.0 §9.3](./SPEC_1.0.md#93-sensitive-links) |

A Link's typed `relation` is listed under [Relationships](#13-relationships).

**What it enables.** Relationships that are not kinship — godparent, guardian, employer, teacher, rival — held with the same evidence as a birth, with a start and end, and with their own visibility so that a sensitive relationship can be kept private while both people remain visible.

### Occupation

A state, not an event: an occupation held by one person over a period, with the employer and place ([1.0 §4.5](./SPEC_1.0.md#45-occupation)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Person | `Occupation.person_id` | reference → Person | — | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Title, as written | `Occupation.title` | text | free text | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Title, transliterated | `Occupation.title_latin` | text | free text | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Title, normalised | `Occupation.title_normalized` | text | free text | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Employer | `Occupation.employer` | record | free text | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Place | `Occupation.place_id` | reference → Place | — | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Valid from | `Occupation.valid_from` | date | — | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Valid until | `Occupation.valid_until` | date | — | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Confidence | `Occupation.confidence` | confidence 0–1 | — | single | — | 1.0 | [1.0 §8](./SPEC_1.0.md#8-confidence-model) |
| Source | `Occupation.source_id` | reference → Source | — | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |
| Note | `Occupation.note` | text | free text | single | — | 1.0 | [1.0 §4.5](./SPEC_1.0.md#45-occupation) |

`Occupation.position`, added in 1.1, is listed under [Education and work](#8-education-and-work).

**What it enables.** See [Education and work](#8-education-and-work): a career as a sequence of dated, sourced states, with the title kept as the source wrote it and a normalised form beside it for comparison.

### Source

The evidence: what it is, how reliable, where it is held, what it says and where it disagrees with other sources — including DNA matches ([1.0 §5.4](./SPEC_1.0.md#54-source)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Title | `Source.title` | text | free text | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Source type | `Source.source_type` | term | closed source types | single | — | 1.0 | [1.0 §5.4.1](./SPEC_1.0.md#541-source-types) |
| Reliability | `Source.reliability` | term | closed reliability levels | single | — | 1.0 | [1.0 §5.4.2](./SPEC_1.0.md#542-reliability-levels) |
| Confidence | `Source.confidence` | confidence 0–1 | — | single | — | 1.0 | [1.0 §8](./SPEC_1.0.md#8-confidence-model) |
| Status | `Source.status` | term | closed | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Repository | `Source.repository` | record | free text | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Date | `Source.date` | date | — | single | — | 1.0 | [1.0 §5.2](./SPEC_1.0.md#52-date) |
| Place | `Source.place_id` | reference → Place | — | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Document | `Source.document_id` | reference → Document | — | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Conflicts with other sources, and their resolution | `Source.conflicts` | record | closed resolution + free text | list | — | 1.0 | [1.0 §8.3](./SPEC_1.0.md#83-conflicting-sources) |
| Transcription | `Source.transcription` | text | free text | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Language | `Source.language` | language tag | — | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| Script | `Source.script` | text | — | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |
| DNA test and match — provider, test type, shared cM | `Source.dna` | record | closed test type | single | — | 1.0 | [1.0 §5.4.3](./SPEC_1.0.md#543-dna-source) |
| Note | `Source.note` | text | free text | single | — | 1.0 | [1.0 §5.4](./SPEC_1.0.md#54-source) |

**What it enables.** Every claim above can point here, and this is where the claim's confidence is justified. A source can be recorded as *known missing* — a register that was burned, a certificate that exists but has not been obtained — which is itself genealogical information. Conflicts between sources are recorded with the field they disagree on and how the disagreement was resolved, so a later researcher can see that the question was asked. A DNA match is a source like any other, supporting a relationship with the centimorgans shared.

### Place

A reusable place with names in several languages, coordinates, identifiers in external gazetteers, and the history of which country it belonged to ([1.0 §5.3](./SPEC_1.0.md#53-place)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Names, per language | `Place.names` | record | free text | list | — | 1.0 | [1.0 §5.3](./SPEC_1.0.md#53-place) |
| Place type | `Place.place_type` | term | closed place types | single | — | 1.0 | [1.0 §5.3.1](./SPEC_1.0.md#531-place-types) |
| Region | `Place.region` | text | free text | single | — | 1.0 | [1.0 §5.3](./SPEC_1.0.md#53-place) |
| Current country | `Place.country_current` | country code | — | single | — | 1.0 | [1.0 §6.5](./SPEC_1.0.md#65-country-codes) |
| Coordinates | `Place.coordinates` | coordinates | — | single | — | 1.0 | [1.0 §5.3](./SPEC_1.0.md#53-place) |
| Country history | `Place.country_history` | record | — | list | — | 1.0 | [1.0 §5.3](./SPEC_1.0.md#53-place) |
| Identifiers — Wikidata, GeoNames, INSEE | `Place.identifiers` | record | — | single | — | 1.0 | [1.0 §5.3](./SPEC_1.0.md#53-place) |
| Note | `Place.note` | text | free text | single | — | 1.0 | [1.0 §5.3](./SPEC_1.0.md#53-place) |

**What it enables.** Lwów, Lemberg, Lviv and Львів are one place with four names, which was in Austria-Hungary, Poland, the Soviet Union and Ukraine within one lifetime. Holding that history on the place lets a birth be shown in the country it was in at the time, and lets records be searched in the archive that held them then.

### Document

A file — photograph, certificate, letter, recording, scan or model — embedded in the bundle or known to exist, with its checksum, OCR, and the entities it concerns ([1.0 §5.5](./SPEC_1.0.md#55-document)).

| Attribute | Path | Type | Vocabulary | Kind | Class | Since | Spec |
|---|---|---|---|---|---|---|---|
| Filename | `Document.filename` | text | — | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| MIME type | `Document.mime_type` | text | — | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Document type | `Document.document_type` | term | closed document types | single | — | 1.0 | [1.0 §5.5.2](./SPEC_1.0.md#552-document-types) |
| Status — whether the bundle holds the file | `Document.status` | term | closed document status | single | — | 1.0 | [1.0 §5.5.1](./SPEC_1.0.md#551-document-status) |
| File — path, size, SHA-256 | `Document.file` | record | — | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| URL | `Document.url` | text | — | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Date | `Document.date` | date | — | single | — | 1.0 | [1.0 §5.2](./SPEC_1.0.md#52-date) |
| Place | `Document.place_id` | reference → Place | — | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Language | `Document.language` | language tag | — | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Linked entities, with roles | `Document.linked_to` | reference → any entity | — | list | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| OCR text | `Document.ocr` | record | free text | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| AI summary and suggested links | `Document.ai` | record | free text | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Caption | `Document.caption` | text | free text | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |
| Note | `Document.note` | text | free text | single | — | 1.0 | [1.0 §5.5](./SPEC_1.0.md#55-document) |

**What it enables.** The evidence travels with the tree: a bundle can carry the certificate, not just a citation of it, with a checksum that shows it has not changed. A document that is known to exist but has not been obtained is recorded as such, so the gap is visible. Every artefact in [Biometrics](#3-biometrics) and [Digital legacy](#14-digital-legacy) is a Document, which is how a gigabyte scan stays out of a person's JSON and still belongs to them.

---

## Closed vocabularies

Wherever the possible answers can be known in advance, 1.1 makes them a closed vocabulary, so that two implementations store the same word for the same thing: 102 of them, several following an external standard — ISCED 2011, ICD-10 chapters, ICCS, Fitzpatrick, CEFR, ISOGG and PhyloTree, UCUM, ISO 3166-1. Where the answers cannot be known in advance, the value is free text.

This page names the vocabularies and does not list their values. Each vocabulary name in the tables links to its `$defs/vocab_<name>` entry in [`schema/axgf-1.1.schema.json`](./schema/axgf-1.1.schema.json), where the values are enumerated; the meaning of each value and the standard it follows are in the specification, indexed in [1.1 §6](./SPEC_1.1.md#6-vocabulary-index). 1.0's own closed lists — gender, union type, event and link categories, source and document types — are defined in [SPEC_1.0.md](./SPEC_1.0.md) and marked *closed* in the tables.

---

## Keeping this page true

A catalogue that silently falls behind is worse than none. Run

```bash
python3 tools/check_data_catalogue.py
```

after any change to a schema. It derives the attribute list from the schemas and checks that every attribute in the schema appears here and every attribute here exists in the schema, that each row's kind, version, class and 1.1 vocabularies match the schema, that every vocabulary link points at its `$defs` entry, and that every specification link lands on a heading. It exits non-zero on any disagreement.

<!-- Vocabulary links: one per $defs/vocab_* entry, at its line in the schema. Checked by tools/check_data_catalogue.py. -->

[v-address_use]: ./schema/axgf-1.1.schema.json#L2999
[v-allergy_severity]: ./schema/axgf-1.1.schema.json#L2840
[v-allergy_type]: ./schema/axgf-1.1.schema.json#L2835
[v-artefact_type]: ./schema/axgf-1.1.schema.json#L2609
[v-assessment_instrument]: ./schema/axgf-1.1.schema.json#L2914
[v-assessment_severity]: ./schema/axgf-1.1.schema.json#L2922
[v-autopsy]: ./schema/axgf-1.1.schema.json#L2986
[v-blood_group]: ./schema/axgf-1.1.schema.json#L2791
[v-body_hair]: ./schema/axgf-1.1.schema.json#L2697
[v-body_region]: ./schema/axgf-1.1.schema.json#L2600
[v-build]: ./schema/axgf-1.1.schema.json#L2649
[v-carrier_status]: ./schema/axgf-1.1.schema.json#L2971
[v-case_outcome]: ./schema/axgf-1.1.schema.json#L3161
[v-clinical_significance]: ./schema/axgf-1.1.schema.json#L2958
[v-consent]: ./schema/axgf-1.1.schema.json#L2618
[v-country]: ./schema/axgf-1.1.schema.json#L3004
[v-decision_style]: ./schema/axgf-1.1.schema.json#L3233
[v-dentition]: ./schema/axgf-1.1.schema.json#L2737
[v-device_kind]: ./schema/axgf-1.1.schema.json#L2826
[v-diagnosis_status]: ./schema/axgf-1.1.schema.json#L2808
[v-diet]: ./schema/axgf-1.1.schema.json#L3243
[v-disposition]: ./schema/axgf-1.1.schema.json#L2991
[v-distinction_kind]: ./schema/axgf-1.1.schema.json#L3061
[v-ear_shape]: ./schema/axgf-1.1.schema.json#L2727
[v-epigenetic_clock]: ./schema/axgf-1.1.schema.json#L2976
[v-eye_colour]: ./schema/axgf-1.1.schema.json#L2654
[v-eye_shape]: ./schema/axgf-1.1.schema.json#L2662
[v-eye_spacing]: ./schema/axgf-1.1.schema.json#L2670
[v-face_shape]: ./schema/axgf-1.1.schema.json#L2714
[v-facial_hair]: ./schema/axgf-1.1.schema.json#L2692
[v-freckles]: ./schema/axgf-1.1.schema.json#L2704
[v-gait]: ./schema/axgf-1.1.schema.json#L2755
[v-gender_identity]: ./schema/axgf-1.1.schema.json#L2628
[v-genomic_file_format]: ./schema/axgf-1.1.schema.json#L2932
[v-hair_colour]: ./schema/axgf-1.1.schema.json#L2671
[v-hair_texture]: ./schema/axgf-1.1.schema.json#L2679
[v-hairline]: ./schema/axgf-1.1.schema.json#L2684
[v-handedness]: ./schema/axgf-1.1.schema.json#L2773
[v-hearing_grade]: ./schema/axgf-1.1.schema.json#L2778
[v-iccs_section]: ./schema/axgf-1.1.schema.json#L3151
[v-icd10_chapter]: ./schema/axgf-1.1.schema.json#L2797
[v-implant_kind]: ./schema/axgf-1.1.schema.json#L2818
[v-income_quintile]: ./schema/axgf-1.1.schema.json#L3050
[v-inheritance_pattern]: ./schema/axgf-1.1.schema.json#L2963
[v-introversion_extraversion]: ./schema/axgf-1.1.schema.json#L3220
[v-isced_level]: ./schema/axgf-1.1.schema.json#L3042
[v-lab_analyte]: ./schema/axgf-1.1.schema.json#L2872
[v-lab_flag]: ./schema/axgf-1.1.schema.json#L2892
[v-lab_panel]: ./schema/axgf-1.1.schema.json#L2867
[v-lab_unit]: ./schema/axgf-1.1.schema.json#L2884
[v-language_proficiency]: ./schema/axgf-1.1.schema.json#L3037
[v-laterality]: ./schema/axgf-1.1.schema.json#L2599
[v-lineage]: ./schema/axgf-1.1.schema.json#L3261
[v-link_relation]: ./schema/axgf-1.1.schema.json#L3266
[v-lip_shape]: ./schema/axgf-1.1.schema.json#L2732
[v-malocclusion]: ./schema/axgf-1.1.schema.json#L2745
[v-mbti]: ./schema/axgf-1.1.schema.json#L3204
[v-membership_kind]: ./schema/axgf-1.1.schema.json#L3195
[v-metaboliser_status]: ./schema/axgf-1.1.schema.json#L2981
[v-military_rank_de]: ./schema/axgf-1.1.schema.json#L3104
[v-military_rank_fr]: ./schema/axgf-1.1.schema.json#L3082
[v-military_rank_gb]: ./schema/axgf-1.1.schema.json#L3116
[v-military_rank_pl]: ./schema/axgf-1.1.schema.json#L3093
[v-military_rank_ru]: ./schema/axgf-1.1.schema.json#L3140
[v-military_rank_us]: ./schema/axgf-1.1.schema.json#L3126
[v-military_service]: ./schema/axgf-1.1.schema.json#L3066
[v-mole_shape]: ./schema/axgf-1.1.schema.json#L2713
[v-mt_haplogroup]: ./schema/axgf-1.1.schema.json#L2945
[v-nationality_mode]: ./schema/axgf-1.1.schema.json#L3029
[v-nose_shape]: ./schema/axgf-1.1.schema.json#L2719
[v-nutrient]: ./schema/axgf-1.1.schema.json#L2897
[v-optical_correction]: ./schema/axgf-1.1.schema.json#L2783
[v-pathogen]: ./schema/axgf-1.1.schema.json#L2845
[v-pay_period]: ./schema/axgf-1.1.schema.json#L3051
[v-personality_instrument]: ./schema/axgf-1.1.schema.json#L3212
[v-pigmentation_mark]: ./schema/axgf-1.1.schema.json#L2705
[v-political_position]: ./schema/axgf-1.1.schema.json#L3187
[v-posture]: ./schema/axgf-1.1.schema.json#L2750
[v-prosthesis_kind]: ./schema/axgf-1.1.schema.json#L2813
[v-rank_category]: ./schema/axgf-1.1.schema.json#L3074
[v-reference_build]: ./schema/axgf-1.1.schema.json#L2927
[v-register_type]: ./schema/axgf-1.1.schema.json#L2641
[v-religion]: ./schema/axgf-1.1.schema.json#L3169
[v-rhesus]: ./schema/axgf-1.1.schema.json#L2792
[v-sacrament]: ./schema/axgf-1.1.schema.json#L3179
[v-sensitive_class]: ./schema/axgf-1.1.schema.json#L2594
[v-serology_result]: ./schema/axgf-1.1.schema.json#L2862
[v-sex_at_birth]: ./schema/axgf-1.1.schema.json#L2623
[v-skin_tone]: ./schema/axgf-1.1.schema.json#L2698
[v-skin_undertone]: ./schema/axgf-1.1.schema.json#L2703
[v-sleep_disorder]: ./schema/axgf-1.1.schema.json#L2906
[v-speech_register]: ./schema/axgf-1.1.schema.json#L2768
[v-sport_level]: ./schema/axgf-1.1.schema.json#L3238
[v-stress_tolerance]: ./schema/axgf-1.1.schema.json#L3228
[v-substance]: ./schema/axgf-1.1.schema.json#L3248
[v-tenure]: ./schema/axgf-1.1.schema.json#L3056
[v-title_kind]: ./schema/axgf-1.1.schema.json#L2633
[v-use_pattern]: ./schema/axgf-1.1.schema.json#L3256
[v-vaccination_status]: ./schema/axgf-1.1.schema.json#L2857
[v-vocal_timbre]: ./schema/axgf-1.1.schema.json#L2763
[v-y_haplogroup]: ./schema/axgf-1.1.schema.json#L2937
[v-zygosity]: ./schema/axgf-1.1.schema.json#L2953
