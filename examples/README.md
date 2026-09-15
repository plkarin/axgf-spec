# Worked examples

Each file here is a **complete, schema-valid AXGF entity** — the same examples
the [top-level README](../README.md) and the specifications show inline,
expanded from the excerpt to a whole entity so that they actually validate. The
1.0 files validate against both schemas, because 1.1 is a superset; the `-1.1`
files use 1.1 attributes and validate against the 1.1 schema only.

| File | Shows |
| --- | --- |
| [`person-minimal.json`](./person-minimal.json) | The smallest valid person: identity, gender, living flag, one dated birth with a confidence score |
| [`person-japanese-name.json`](./person-japanese-name.json) | Per-component transliteration and furigana — `display_latin`, `reading`, `reading_system`, `display_order: family_first` |
| [`person-hebrew-name.json`](./person-hebrew-name.json) | A right-to-left name with a patronymic component and Latin transliteration per component |
| [`person-multi-calendar-date.json`](./person-multi-calendar-date.json) | One birth date expressed simultaneously in Gregorian, Japanese-era and Hebrew calendars via `alternatives[]` |
| [`person-profile-1.1.json`](./person-profile-1.1.json) | A deceased person with claims in most of the 1.1 profile groups — dated series, closed vocabularies, sensitive-class attributes, a per-person `class_visibility`, and an artefact reference ([SPEC_1.1](../SPEC_1.1.md) §8) |
| [`family-lineage-1.1.json`](./family-lineage-1.1.json) | A family whose children carry `lineage` — a stepchild and a biological child of the same union (§5.13) |
| [`link-relation-1.1.json`](./link-relation-1.1.json) | A godparent Link typed with `relation` beside its words in `label` and `label_reverse` (§5.13) |

The README shows the `identity.name` block alone for the Japanese and Hebrew
cases; a person also requires `id`, `type`, `axgf_version`, and
`identity.gender` / `identity.is_living`, so the files carry those too.

## Validate them

Any JSON Schema draft 2020-12 validator works. With Python:

```bash
pip install jsonschema
python3 - <<'PY'
import json, glob
from jsonschema import Draft202012Validator

def check(schema_path, path):
    schema = json.load(open(schema_path))
    entity = json.load(open(path))
    # Validate against the definition for the entity's own type, so an error
    # names the field rather than every branch of the top-level oneOf.
    v = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/" + entity["type"]})
    return list(v.iter_errors(entity))

for path in sorted(glob.glob("examples/*.json")):
    versions = ["1.1"] if path.endswith("-1.1.json") else ["1.0", "1.1"]
    for ver in versions:
        errs = check(f"schema/axgf-{ver}.schema.json", path)
        print(("FAIL " if errs else "OK   ") + ver + "  " + path)
        for e in errs:
            print("   ", list(e.path), e.message)
PY
```

Run it from the repository root. Every line reports `OK`.

To validate a whole `.axgf` **bundle** — schema plus the semantic checks
(dangling references, cycles, chronology) — use the reference library's CLI:

```bash
cargo install axgf-rs
axgf validate my-family.axgf
```

## Bundle layout

These files are single entities. Inside a `.axgf` bundle they would live at
`persons/{uuid}.json`, `families/{uuid}.json` and `links/{uuid}.json`; see [Bundle structure](../README.md#bundle-structure)
in the README and [`SPEC_1.0.md`](../SPEC_1.0.md) §3 for the full archive
layout.
