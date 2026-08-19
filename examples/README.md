# Worked examples

Each file here is a **complete, schema-valid AXGF 1.0 entity** — the same
examples the [top-level README](../README.md) shows inline, expanded from the
excerpt to a whole entity so that they actually validate.

| File | Shows |
| --- | --- |
| [`person-minimal.json`](./person-minimal.json) | The smallest valid person: identity, gender, living flag, one dated birth with a confidence score |
| [`person-japanese-name.json`](./person-japanese-name.json) | Per-component transliteration and furigana — `display_latin`, `reading`, `reading_system`, `display_order: family_first` |
| [`person-hebrew-name.json`](./person-hebrew-name.json) | A right-to-left name with a patronymic component and Latin transliteration per component |
| [`person-multi-calendar-date.json`](./person-multi-calendar-date.json) | One birth date expressed simultaneously in Gregorian, Japanese-era and Hebrew calendars via `alternatives[]` |

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
v = Draft202012Validator(json.load(open("schema/axgf-1.0.schema.json")))
for f in sorted(glob.glob("examples/*.json")):
    errs = list(v.iter_errors(json.load(open(f))))
    print(("FAIL " if errs else "OK   ") + f)
    for e in errs:
        print("   ", list(e.path), e.message)
PY
```

Run it from the repository root. All four files report `OK`.

To validate a whole `.axgf` **bundle** — schema plus the semantic checks
(dangling references, cycles, chronology) — use the reference library's CLI:

```bash
cargo install axgf-rs
axgf validate my-family.axgf
```

## Bundle layout

These files are single entities. Inside a `.axgf` bundle they would live at
`persons/{uuid}.json`; see [Bundle structure](../README.md#bundle-structure)
in the README and [`SPEC_1.0.md`](../SPEC_1.0.md) §3 for the full archive
layout.
