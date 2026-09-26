#!/usr/bin/env python3
## @file    check_data_catalogue.py
## @brief   Check DATA.md against the AXGF JSON Schemas.
## @details DATA.md is a catalogue of every attribute the format can carry.
##          It is useful only while it is complete and true, so this script
##          derives the attribute list from the schemas and compares it with
##          the attribute tables in DATA.md, both ways:
##
##            - every attribute in the schema appears in DATA.md;
##            - every attribute in DATA.md exists in the schema;
##
##          and, for each attribute listed, that its Kind, Since, Class and
##          Vocabulary cells agree with the schema, that each vocabulary
##          link points at its $defs entry, and that every Markdown link
##          in DATA.md -- to the specification or within the page -- lands
##          on a heading.
##
##          Vocabularies checked are the 1.1 closed vocabularies, the
##          $defs/vocab_* entries. 1.0's inline enumerations (gender,
##          union type, event category, ...) are frozen with 1.0 and are
##          not checked.
##
##          What counts as an attribute (the rule DATA.md follows):
##
##            Person   every top-level property; a top-level object
##                     (identity, birth, death, ai and the 1.1 blocks) is a
##                     container, and its properties are the attributes:
##                     identity.titles, morphology.height, ...
##            Family, Event, Link, Occupation, Source, Place, Document
##                     every top-level property, and every nested property
##                     that 1.1 added (Family.children[].lineage).
##
##          The entity envelope (id, type, axgf_version, created_at,
##          updated_at, version_num, created_by, tags, extensions) is common
##          to every entity and is not an attribute of any of them.
##
##          Exit status is 0 when everything agrees, 1 otherwise.
##
## @usage   python3 tools/check_data_catalogue.py [--list]
## @license CC0-1.0

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_10 = ROOT / "schema" / "axgf-1.0.schema.json"
SCHEMA_11 = ROOT / "schema" / "axgf-1.1.schema.json"
CATALOGUE = ROOT / "DATA.md"

ENTITIES = ["person", "family", "event", "link", "occupation",
            "source", "place", "document"]
KINDS = {"single", "series", "list"}
PATH_RE = re.compile(r"^`([A-Za-z_][\w.\[\]]*)`$")
VOCAB_REF_RE = re.compile(r"\[`?([a-z0-9_]+)`?\]\[v-([a-z0-9_]+)\]")
VOCAB_DEF_RE = re.compile(r"^\[v-([a-z0-9_]+)\]:\s*(\S+)\s*$", re.M)
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def deref(defs, node):
    """Follow a lone $ref to its definition."""
    while isinstance(node, dict) and "$ref" in node:
        node = defs[node["$ref"].rsplit("/", 1)[1]]
    return node


def is_claim(node):
    return any(isinstance(x, dict) and x.get("$ref", "").endswith("/claim")
               for x in node.get("allOf", []))


def envelope(defs):
    return set(defs["base_entity"]["properties"]) | {"type"}


def attributes(defs):
    """Map canonical path -> schema node, by the rule in the header."""
    out = {}
    skip = envelope(defs)
    for entity in ENTITIES:
        prefix = entity.capitalize()
        for name, node in defs[entity]["properties"].items():
            if name in skip:
                continue
            path = f"{prefix}.{name}"
            target = deref(defs, node)
            if entity == "person" and "properties" in target \
                    and not is_claim(target):
                for sub, subnode in target["properties"].items():
                    out[f"{path}.{sub}"] = subnode
            else:
                out[path] = node
    return out


def nested_additions(defs10, defs11):
    """Nested properties of non-Person entities that 1.1 added."""
    out = {}
    for entity in ENTITIES[1:]:
        old = defs10[entity]["properties"]
        for name, node in defs11[entity]["properties"].items():
            if name not in old:
                continue
            items = node.get("items", node)
            props = items.get("properties", {})
            old_items = old[name].get("items", old[name])
            old_props = old_items.get("properties", {})
            for sub, subnode in props.items():
                if sub not in old_props:
                    out[f"{entity.capitalize()}.{name}.{sub}"] = subnode
    return out


def vocabularies(defs, node, seen=None):
    """Every vocab_* definition reachable from a node."""
    seen = set() if seen is None else seen
    found = set()
    if isinstance(node, dict):
        ref = node.get("$ref")
        if ref:
            name = ref.rsplit("/", 1)[1]
            if name.startswith("vocab_"):
                found.add(name[len("vocab_"):])
            if name not in seen:
                seen.add(name)
                found |= vocabularies(defs, defs[name], seen)
        for key, value in node.items():
            if key != "$ref":
                found |= vocabularies(defs, value, seen)
    elif isinstance(node, list):
        for value in node:
            found |= vocabularies(defs, value, seen)
    return found


def kind(node):
    if node.get("type") == "array":
        return "series" if is_claim(node.get("items", {})) else "list"
    return "single"


def sensitive_class(node):
    return node.get("x-axgf-class") or node.get("items", {}).get("x-axgf-class")


def canonical(path):
    path = path.replace("[]", "")
    head = path.split(".", 1)[0]
    if head[:1].isupper():
        return path
    return "Person." + path


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def catalogue_rows(text):
    """Yield (line number, {column: cell}) for rows of attribute tables."""
    header = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            header = None
            continue
        cells = split_row(line)
        if header is None:
            header = cells if "Path" in cells else []
            continue
        if not header or set(line) <= set("|-: "):
            continue
        row = dict(zip(header, cells))
        match = PATH_RE.match(row.get("Path", ""))
        if match:
            yield number, match.group(1), row


def slug(heading):
    """GitHub's anchor for a Markdown heading."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(markdown):
    seen, out = {}, set()
    for line in markdown.splitlines():
        match = re.match(r"^#{1,6}\s+(.*)$", line)
        if not match:
            continue
        base = slug(match.group(1))
        n = seen.get(base, 0)
        out.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    return out


def schema_lines(path):
    """Line number of each $defs entry in a schema file."""
    out = {}
    for number, line in enumerate(path.read_text().splitlines(), 1):
        match = re.match(r'^\s{4}"([a-z0-9_]+)":\s*\{', line)
        if match:
            out.setdefault(match.group(1), number)
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Check DATA.md against the AXGF JSON Schemas.")
    parser.add_argument("--list", action="store_true",
                        help="print the schema's attribute list and exit")
    args = parser.parse_args()

    defs10 = json.loads(SCHEMA_10.read_text())["$defs"]
    defs11 = json.loads(SCHEMA_11.read_text())["$defs"]
    schema = attributes(defs11)
    schema.update(nested_additions(defs10, defs11))
    in_10 = set(attributes(defs10))

    if args.list:
        for path in schema:
            node = schema[path]
            print(path, kind(node), "1.0" if path in in_10 else "1.1",
                  sensitive_class(node) or "-",
                  ",".join(sorted(vocabularies(defs11, node))) or "-")
        return 0

    text = CATALOGUE.read_text()
    errors = []
    listed = {}
    for number, raw, row in catalogue_rows(text):
        path = canonical(raw)
        where = f"DATA.md:{number}: `{raw}`"
        if path in listed:
            errors.append(f"{where} listed twice (first at line {listed[path]})")
            continue
        listed[path] = number
        node = schema.get(path)
        if node is None:
            continue

        want = kind(node)
        got = row.get("Kind", "")
        if got not in KINDS or (got == "single") != (want == "single") \
                or (want == "series" and got != "series"):
            errors.append(f"{where} Kind is '{got}', schema says {want}")

        want = "1.0" if path in in_10 else "1.1"
        if row.get("Since") != want:
            errors.append(f"{where} Since is '{row.get('Since')}', schema says {want}")

        want = sensitive_class(node)
        got = row.get("Class", "").strip("`* ")
        if (got if got not in ("—", "-", "") else None) != want:
            errors.append(f"{where} Class is '{got}', schema says {want or 'none'}")

        # A nested attribute listed on its own row carries its own
        # vocabularies; its parent's row need not repeat them.
        want = vocabularies(defs11, node)
        for other, child in schema.items():
            if other.startswith(path + "."):
                want -= vocabularies(defs11, child)
        got = set()
        for label, target in VOCAB_REF_RE.findall(row.get("Vocabulary", "")):
            if label != target:
                errors.append(f"{where} vocabulary link [{label}] points at v-{target}")
            got.add(target)
        if got != want:
            if want - got:
                errors.append(f"{where} Vocabulary omits {', '.join(sorted(want - got))}")
            if got - want:
                errors.append(f"{where} Vocabulary names {', '.join(sorted(got - want))}, "
                              "which the schema does not use here")

    missing = [p for p in schema if p not in listed]
    extra = [p for p in listed if p not in schema]
    for path in missing:
        errors.append(f"missing from DATA.md: {path}")
    for path in extra:
        errors.append(f"DATA.md:{listed[path]}: {path} is not in the schema")

    # Vocabulary link definitions: one per vocab_* in the schema, each at
    # the line of its $defs entry.
    lines = schema_lines(SCHEMA_11)
    rel = "./" + str(SCHEMA_11.relative_to(ROOT))
    defined = dict(VOCAB_DEF_RE.findall(text))
    all_vocabs = {k[len("vocab_"):] for k in defs11 if k.startswith("vocab_")}
    for name in sorted(all_vocabs - set(defined)):
        errors.append(f"no link definition [v-{name}] in DATA.md")
    for name, target in sorted(defined.items()):
        if name not in all_vocabs:
            errors.append(f"[v-{name}] names no vocabulary in the schema")
            continue
        want = f"{rel}#L{lines[f'vocab_{name}']}"
        if target != want:
            errors.append(f"[v-{name}] is {target}, should be {want}")

    # Links anywhere in DATA.md, to the specification or within the page,
    # must land on a heading.
    heads = {}
    for target in sorted(set(LINK_RE.findall(text))):
        file, _, anchor = target.partition("#")
        if file == "":
            file = CATALOGUE.name
        if not file.endswith(".md") or file.startswith("http"):
            continue
        doc = ROOT / file
        if not doc.exists():
            errors.append(f"link to missing file {target}")
            continue
        if anchor:
            if doc not in heads:
                heads[doc] = anchors(doc.read_text())
            if anchor not in heads[doc]:
                errors.append(f"link to missing heading {target}")

    for error in errors:
        print(error)
    documented = len([p for p in listed if p in schema])
    print(f"schema -> DATA.md: {len(schema) - len(missing)} of {len(schema)} "
          f"schema attributes are in DATA.md")
    print(f"DATA.md -> schema: {documented} of {len(listed)} "
          f"DATA.md attributes are in the schema")
    print(f"vocabularies: {len(set(defined) & all_vocabs)} of {len(all_vocabs)} linked")
    print("OK" if not errors else f"{len(errors)} problem(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
