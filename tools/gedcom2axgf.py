#!/usr/bin/env python3
## @file    gedcom2axgf.py
## @brief   GEDCOM 5.5.1 -> AXGF 1.0 converter.
## @details Converts one or more GEDCOM files into a single AXGF bundle
##          (.axgf ZIP archive) with a concordance file mapping original
##          GEDCOM cross-references to AXGF UUIDs.
##
##          Mapping follows AXGF Specification 1.0, section 11.1:
##            INDI      -> person
##            FAM       -> family (+ marriage event)
##            NAME      -> person.identity.name / identity.names[]
##            BIRT/DEAT -> person.birth / person.death
##            HUSB/WIFE -> family.union.persons[]
##            CHIL      -> family.children[]
##            OCCU      -> occupation
##            SOUR      -> source
##            OBJE      -> document (status=referenced or present)
##            NOTE      -> notes
##            PLAC      -> place (deduplicated)
##
## @author  Axiom / axgf-spec project
## @license CC0-1.0

import argparse
import hashlib
import json
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

AXGF_VERSION = "1.0"
GENERATOR = {"name": "gedcom2axgf", "version": "1.0.0",
             "url": "https://gitlab.com/leonardkarin/axgf-spec"}

## Month tokens -> month number. Full tokens looked up first, then the
## 3-letter prefix. Covers English GEDCOM plus Polish and French webtrees
## exports (which localize month names and date qualifiers).
MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
          "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
          # Polish (3-letter prefixes of full names align with these)
          "STY": 1, "LUT": 2, "KWI": 4, "MAJ": 5, "CZE": 6, "LIP": 7,
          "SIE": 8, "WRZ": 9, "PAŹ": 10, "PAZ": 10, "LIS": 11, "GRU": 12,
          # French (full tokens where the prefix is ambiguous)
          "JANV": 1, "FÉVR": 2, "FEVR": 2, "MARS": 3, "AVR": 4,
          "JUIN": 6, "JUIL": 7, "AOÛT": 8, "AOUT": 8, "SEPT": 9,
          "DÉC": 12}

## Localized GEDCOM date qualifiers (webtrees exports localize these).
CIRCA_PREFIXES = ("ABT", "EST", "CAL", "OK", "OKOŁO", "OKOLO",
                  "VERS", "ENV", "ENVIRON", "UM", "CIRCA", "CA")
BEFORE_PREFIXES = ("BEF", "PRZED", "AVANT", "VOR")
AFTER_PREFIXES = ("AFT", "PO", "APRÈS", "APRES", "NACH")
BETWEEN_RE = re.compile(
    r"^(?:BET\.?|MIĘDZY|MIEDZY|ENTRE|ZWISCHEN)\s+(.+?)\s+"
    r"(?:AND|I|ET|UND)\s+(.+)$", re.IGNORECASE)

## GEDCOM calendar escapes -> AXGF calendar identifiers.
CALENDARS = {"DGREGORIAN": "gregorian", "DJULIAN": "julian",
             "DHEBREW": "hebrew", "DFRENCH R": "republican_french",
             "DROMAN": "roman", "DISLAMIC": "hijri"}

## GEDCOM line pattern: LEVEL [@XREF@] TAG [VALUE]
LINE_RE = re.compile(r"^\s*(\d+)\s+(?:(@[^@]+@)\s+)?(\w+)(?:\s(.*))?$")


# ---------------------------------------------------------------------------
# GEDCOM parsing
# ---------------------------------------------------------------------------

class Record:
    ## @brief One GEDCOM record node (level, tag, value, children).

    __slots__ = ("level", "xref", "tag", "value", "children")

    def __init__(self, level, xref, tag, value):
        self.level = level
        self.xref = xref
        self.tag = tag
        self.value = value or ""
        self.children = []

    def first(self, tag):
        ## @return First child with the given tag, or None.
        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def all(self, tag):
        ## @return All children with the given tag.
        return [c for c in self.children if c.tag == tag]

    def sub_value(self, *path):
        ## @return Value of the child found by walking the tag path, or "".
        node = self
        for tag in path:
            node = node.first(tag)
            if node is None:
                return ""
        return node.value


def read_gedcom_text(path):
    ## @brief  Read a GEDCOM file with encoding detection.
    ## @return Decoded text (str).
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def parse_records(text):
    ## @brief  Parse GEDCOM text into a list of level-0 Record trees.
    ## @return List of Record.
    roots = []
    stack = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = LINE_RE.match(line)
        if not match:
            continue
        level = int(match.group(1))
        rec = Record(level, match.group(2), match.group(3), match.group(4))

        if rec.tag in ("CONC", "CONT") and stack:
            parent_value = stack[-1]
            sep = "\n" if rec.tag == "CONT" else ""
            parent_value.value += sep + rec.value
            continue

        while stack and stack[-1].level >= level:
            stack.pop()
        if stack:
            stack[-1].children.append(rec)
        else:
            roots.append(rec)
        stack.append(rec)
    return roots


# ---------------------------------------------------------------------------
# Field converters
# ---------------------------------------------------------------------------

def parse_gedcom_date(value):
    ## @brief  Convert a GEDCOM date string to an AXGF date object.
    ## @param  value GEDCOM DATE value (e.g. "ABT 12 APR 1923").
    ## @return AXGF date dict, or None when unparseable.
    if not value:
        return None
    text = value.strip()
    calendar = "gregorian"

    escape = re.match(r"^@#(\w[\w ]*)@\s*(.*)$", text)
    if escape:
        calendar = CALENDARS.get(escape.group(1).upper(), "gregorian")
        text = escape.group(2)

    def fallback():
        ## Unparseable value: keep the original text as a note.
        return {"calendar": calendar, "precision": "unknown", "circa": False,
                "note": value}

    upper = text.upper()
    circa = False
    for prefix in CIRCA_PREFIXES:
        if upper.startswith(prefix + " "):
            circa = True
            text = text[len(prefix):].strip()
            upper = text.upper()
            break

    between = BETWEEN_RE.match(text)
    if between:
        earliest = _simple_date(between.group(1))
        latest = _simple_date(between.group(2))
        if earliest is None and latest is None:
            return fallback()
        bounds = {}
        if earliest:
            bounds["earliest"] = earliest
        if latest:
            bounds["latest"] = latest
        return {"calendar": calendar, "precision": "unknown", "circa": False,
                "range": bounds}

    for prefixes, side in ((BEFORE_PREFIXES, "latest"),
                           (AFTER_PREFIXES, "earliest")):
        for prefix in prefixes:
            if upper.startswith(prefix + " "):
                bound = _simple_date(text[len(prefix):].strip())
                if bound is None:
                    return fallback()
                return {"calendar": calendar, "precision": "unknown",
                        "circa": False, "range": {side: bound}}

    simple = _simple_date(text)
    if simple is None:
        result = fallback()
        result["circa"] = circa
        return result
    simple["calendar"] = calendar
    simple["circa"] = circa
    return simple


def _month(token):
    ## @return Month number for a localized token, or None.
    upper = token.upper()
    return MONTHS.get(upper) or MONTHS.get(upper[:3])


def _simple_date(text):
    ## @brief  Parse "12 APR 1923" / "SIERPIEŃ 1944" / "1923 R" into
    ##         value+precision.
    ## @return Partial AXGF date dict, or None.
    parts = text.strip().split()
    ## Polish year suffix "R"/"R." (rok) after the year.
    if parts and parts[-1].upper().rstrip(".") in ("R", "ROKU"):
        parts = parts[:-1]
    try:
        if len(parts) == 3:
            day = int(parts[0])
            month = _month(parts[1])
            year = int(parts[2])
            if month is None:
                return None
            return {"value": f"{year:04d}-{month:02d}-{day:02d}",
                    "precision": "exact"}
        if len(parts) == 2:
            month = _month(parts[0])
            year = int(parts[1])
            if month is None:
                return None
            return {"value": f"{year:04d}-{month:02d}", "precision": "month"}
        if len(parts) == 1:
            year = int(parts[0])
            return {"value": f"{year:04d}", "precision": "year"}
    except (ValueError, KeyError):
        return None
    return None


def parse_name(name_rec):
    ## @brief  Convert a GEDCOM NAME record to an AXGF name object.
    ## @param  name_rec NAME Record ("Jean /Pierre-Léonard/" + subtags).
    ## @return AXGF name dict.
    raw = name_rec.value.strip()
    match = re.match(r"^([^/]*)/([^/]*)/(.*)$", raw)
    if match:
        given = match.group(1).strip()
        family = match.group(2).strip()
        suffix = match.group(3).strip()
    else:
        given, family, suffix = raw, "", ""

    given = name_rec.sub_value("GIVN") or given
    family = name_rec.sub_value("SURN") or family

    components = []
    order = 1
    if given:
        components.append({"type": "given_name", "value": given,
                           "order": order})
        order += 1
    if family:
        components.append({"type": "family_name", "value": family,
                           "order": order})
        order += 1
    nickname = name_rec.sub_value("NICK")
    if nickname:
        components.append({"type": "nickname", "value": nickname,
                           "order": order})

    display = " ".join(filter(None, [given, family, suffix])) or "[Unknown]"
    return {"display": display, "components": components}


# ---------------------------------------------------------------------------
# Converter
# ---------------------------------------------------------------------------

class Converter:
    ## @brief GEDCOM -> AXGF conversion engine for one or more input files.

    def __init__(self, default_confidence=0.8, lang="und",
                 emit_parent_links=False):
        self.default_confidence = default_confidence
        self.lang = lang
        self.emit_parent_links = emit_parent_links
        self.now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.persons = {}
        self.families = {}
        self.events = {}
        self.links = {}
        self.occupations = {}
        self.sources = {}
        self.places = {}
        self.documents = {}

        ## Concordance: file name -> {gedcom xref -> axgf uuid}.
        self.concordance = {}
        ## Per-file xref -> uuid map used during conversion.
        self._xref_map = {}
        ## Normalized place name -> place uuid (global dedup).
        self._place_index = {}
        ## (family xref, child xref) -> PEDI value (adoption tracking).
        self._pedi = {}

    # -- helpers ----------------------------------------------------------

    def _new_id(self):
        return str(uuid.uuid4())

    def _base(self, entity_type, entity_id):
        return {"id": entity_id, "type": entity_type,
                "axgf_version": AXGF_VERSION,
                "created_at": self.now, "updated_at": self.now,
                "version_num": 1}

    def _uuid_for(self, xref):
        ## @brief Stable UUID for a GEDCOM xref within the current file.
        if xref not in self._xref_map:
            self._xref_map[xref] = self._new_id()
        return self._xref_map[xref]

    def _place_id(self, name):
        ## @brief Deduplicated place entity for a GEDCOM PLAC value.
        if not name:
            return None
        key = re.sub(r"\s+", " ", name.strip().lower())
        if key in self._place_index:
            return self._place_index[key]
        place_id = self._new_id()
        place = self._base("place", place_id)
        place["names"] = [{"lang": self.lang, "value": name.strip(),
                           "is_primary": True}]
        parts = [p.strip() for p in name.split(",") if p.strip()]
        if len(parts) > 1:
            place["region"] = ", ".join(parts[1:])
        self.places[place_id] = place
        self._place_index[key] = place_id
        return place_id

    def _fact(self, node):
        ## @brief  Build a birth/death style fact from a BIRT/DEAT record.
        ## @return Fact dict or None when the record carries no data.
        if node is None:
            return None
        fact = {}
        date = parse_gedcom_date(node.sub_value("DATE"))
        if date:
            date.setdefault("confidence", self.default_confidence)
            fact["date"] = date
        place_id = self._place_id(node.sub_value("PLAC"))
        if place_id:
            fact["place_id"] = place_id
        source = node.first("SOUR")
        if source and source.value.startswith("@"):
            fact["source_id"] = self._uuid_for(source.value)
        if not fact:
            return None
        fact["confidence"] = self.default_confidence
        return fact

    def _notes(self, rec, note_records):
        ## @brief Collect inline and referenced NOTE text for a record.
        chunks = []
        for note in rec.all("NOTE"):
            if note.value.startswith("@"):
                target = note_records.get(note.value)
                if target:
                    chunks.append(target.value)
            elif note.value:
                chunks.append(note.value)
        return "\n\n".join(chunks) or None

    # -- entity conversion -------------------------------------------------

    def convert_file(self, path):
        ## @brief Convert one GEDCOM file, merging into the current bundle.
        path = Path(path)
        self.convert_text(read_gedcom_text(path),
                          source_name=path.name, base_dir=path.parent)

    def convert_text(self, text, source_name, base_dir=None,
                     pre_convert=None):
        ## @brief  Convert an in-memory GEDCOM document, merging into the
        ##         current bundle. Exposed so callers that already hold the
        ##         records as strings (e.g. webtrees2axgf reading i_gedcom /
        ##         f_gedcom straight from the database) can reuse this parser
        ##         and every hard-won behaviour without touching the disk.
        ## @param  text        Full GEDCOM text (HEAD .. TRLR).
        ## @param  source_name Key recorded in the concordance for this batch.
        ## @param  base_dir    Directory OBJE FILE paths resolve against, or
        ##                     None to leave top-level OBJE records referenced.
        ## @param  pre_convert Optional callback invoked with this Converter
        ##                     after xrefs are reset and top-level SOUR/OBJE
        ##                     records are converted, but before individuals
        ##                     and families. It lets a caller seed extra
        ##                     entities (e.g. media Documents built from the
        ##                     database) so that INDI/FAM cross-references
        ##                     resolve to them during conversion.
        self._xref_map = {}
        self._pedi = {}
        roots = parse_records(text)

        note_records = {r.xref: r for r in roots
                        if r.tag == "NOTE" and r.xref}

        for rec in roots:
            if rec.tag == "SOUR" and rec.xref:
                self._convert_source(rec)
        for rec in roots:
            if rec.tag == "OBJE" and rec.xref and base_dir is not None:
                self._convert_document(rec, base_dir)
        if pre_convert is not None:
            pre_convert(self)
        for rec in roots:
            if rec.tag == "INDI":
                self._convert_individual(rec, note_records, base_dir)
        for rec in roots:
            if rec.tag == "FAM":
                self._convert_family(rec, note_records)

        self.concordance[source_name] = dict(self._xref_map)

    def _convert_source(self, rec):
        source_id = self._uuid_for(rec.xref)
        source = self._base("source", source_id)
        source["title"] = rec.sub_value("TITL") or rec.value or "Untitled source"
        source["source_type"] = "other"
        source["reliability"] = "unknown"
        source["confidence"] = self.default_confidence
        repo_name = rec.sub_value("REPO")
        author = rec.sub_value("AUTH")
        if repo_name and not repo_name.startswith("@"):
            source["repository"] = {"name": repo_name}
        if author:
            source["note"] = f"Author: {author}"
        self.sources[source_id] = source

    def _convert_document(self, rec, base_dir):
        doc_id = self._uuid_for(rec.xref)
        file_node = rec.first("FILE")
        file_ref = file_node.value if file_node else ""
        ## GEDCOM 5.5.1 (webtrees) nests FORM and TITL under FILE;
        ## older 5.5 exports keep them at OBJE level. Check both.
        title = (rec.sub_value("TITL")
                 or (file_node.sub_value("TITL") if file_node else "")
                 or Path(file_ref).name or "document")
        form = ((file_node.sub_value("FORM") if file_node else "")
                or rec.sub_value("FORM")).lower() \
            or Path(file_ref).suffix.lstrip(".").lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "gif": "image/gif", "pdf": "application/pdf",
                "tif": "image/tiff", "tiff": "image/tiff"}.get(form,
                                                    "application/octet-stream")
        doc = self._base("document", doc_id)
        doc["filename"] = Path(file_ref).name or title
        doc["mime_type"] = mime
        doc["document_type"] = "photo" if mime.startswith("image/") else "other"
        doc["caption"] = title
        doc["linked_to"] = []

        local = (base_dir / file_ref) if file_ref else None
        if local and local.is_file():
            data = local.read_bytes()
            doc["status"] = "present"
            doc["file"] = {
                "path": f"documents/files/{doc_id}{local.suffix.lower()}",
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest()}
            doc["_local_path"] = str(local)
        else:
            doc["status"] = "referenced"
            if file_ref:
                doc["url"] = file_ref
        self.documents[doc_id] = doc

    def _convert_individual(self, rec, note_records, base_dir):
        person_id = self._uuid_for(rec.xref)
        person = self._base("person", person_id)

        names = rec.all("NAME")
        primary = parse_name(names[0]) if names else \
            {"display": "[Unknown]", "components": []}

        sex = rec.sub_value("SEX").upper()
        gender = {"M": "M", "F": "F", "X": "NB"}.get(sex, "U")

        death_node = rec.first("DEAT")
        person["identity"] = {
            "name": primary,
            "gender": {"value": gender},
            "is_living": death_node is None,
            "visibility": "members"}

        if len(names) > 1:
            person["identity"]["names"] = []
            for extra in names[1:]:
                alias = parse_name(extra)
                alias["type"] = "alias"
                person["identity"]["names"].append(alias)

        birth = self._fact(rec.first("BIRT"))
        if birth:
            person["birth"] = birth
        death = self._fact(death_node)
        if death:
            cause = death_node.sub_value("CAUS") if death_node else ""
            if cause:
                death["cause"] = cause
            person["death"] = death

        chunks = []
        notes = self._notes(rec, note_records)
        if notes:
            chunks.append(notes)
        for titl in rec.all("TITL"):
            if titl.value:
                chunks.append(f"Title: {titl.value}")
        for fact in rec.all("FACT"):
            if fact.value:
                chunks.append(fact.value)
        if chunks:
            person["notes"] = "\n\n".join(chunks)

        ## Record pedigree (adoption etc.) declared on the child side.
        for famc in rec.all("FAMC"):
            pedi = famc.sub_value("PEDI")
            if pedi and famc.value.startswith("@"):
                self._pedi[(famc.value, rec.xref)] = pedi

        for obje in rec.all("OBJE"):
            if obje.value.startswith("@"):
                doc_id = self._uuid_for(obje.value)
                person.setdefault("documents", []).append(
                    {"document_id": doc_id})
                if doc_id in self.documents:
                    self.documents[doc_id]["linked_to"].append(
                        {"entity_type": "person", "entity_id": person_id,
                         "role": "subject"})

        for occu in rec.all("OCCU"):
            self._convert_occupation(occu, person_id)

        self.persons[person_id] = person

    def _convert_occupation(self, occu, person_id):
        occ_id = self._new_id()
        occ = self._base("occupation", occ_id)
        occ["person_id"] = person_id
        occ["title"] = occu.value or "Unknown occupation"
        occ["confidence"] = self.default_confidence
        date = parse_gedcom_date(occu.sub_value("DATE"))
        if date:
            occ["valid_from"] = {"date": date}
        place_id = self._place_id(occu.sub_value("PLAC"))
        if place_id:
            occ["place_id"] = place_id
        self.occupations[occ_id] = occ

    def _convert_family(self, rec, note_records):
        family_id = self._uuid_for(rec.xref)
        family = self._base("family", family_id)

        spouses = []
        for tag in ("HUSB", "WIFE"):
            member = rec.first(tag)
            if member and member.value.startswith("@"):
                spouses.append({"person_id": self._uuid_for(member.value),
                                "role": "spouse"})

        marriage = rec.first("MARR")
        divorce = rec.first("DIV")
        ## A family with no spouse pointer is a sibling group (spec §4.2.3):
        ## the union is optional, so omit it rather than fabricate a phantom
        ## person_id that would dangle. union.persons requires minItems 1,
        ## so it is only emitted when at least one spouse is present.
        if spouses:
            union = {"type": "marriage" if marriage else "unknown",
                     "persons": spouses,
                     "confidence": self.default_confidence}

            if marriage:
                start = {}
                date = parse_gedcom_date(marriage.sub_value("DATE"))
                if date:
                    start["date"] = date
                place_id = self._place_id(marriage.sub_value("PLAC"))
                if place_id:
                    start["place_id"] = place_id
                if start:
                    event_id = self._marriage_event(family_id, spouses, start)
                    start["event_id"] = event_id
                    union["start"] = start
                union["status"] = "ended_by_divorce" if divorce else "unknown"
            if divorce:
                end = {"reason": "divorce"}
                date = parse_gedcom_date(divorce.sub_value("DATE"))
                if date:
                    end["date"] = date
                union["end"] = end
                union["status"] = "ended_by_divorce"

            family["union"] = union

        children = []
        for chil in rec.all("CHIL"):
            if chil.value.startswith("@"):
                child_id = self._uuid_for(chil.value)
                child_entry = {"person_id": child_id,
                               "confidence": self.default_confidence}
                pedi = self._pedi.get((rec.xref, chil.value))
                if pedi and pedi.lower() != "birth":
                    child_entry["note"] = f"pedigree: {pedi}"
                children.append(child_entry)
                if self.emit_parent_links:
                    for spouse in spouses:
                        self._parent_link(spouse["person_id"], child_id)
        if children:
            family["children"] = children

        notes = self._notes(rec, note_records)
        if notes:
            family["notes"] = notes

        ## The schema requires a family to carry a union or children
        ## (anyOf). A FAM record with neither spouse pointer nor child
        ## carries no genealogical structure, so drop it rather than emit
        ## an entity that cannot validate.
        if "union" not in family and "children" not in family:
            return

        self.families[family_id] = family

    def _marriage_event(self, family_id, spouses, start):
        event_id = self._new_id()
        event = self._base("event", event_id)
        event["category"] = "marriage"
        event["date"] = start.get("date",
                                  {"precision": "unknown", "circa": False})
        if "place_id" in start:
            event["place_id"] = start["place_id"]
        event["participants"] = [
            {"entity_type": "person", "entity_id": s["person_id"],
             "role": f"spouse_{i+1}", "confidence": self.default_confidence}
            for i, s in enumerate(spouses)]
        event["participants"].append(
            {"entity_type": "family", "entity_id": family_id,
             "role": "created", "confidence": self.default_confidence})
        event["confidence"] = self.default_confidence
        self.events[event_id] = event
        return event_id

    def _parent_link(self, parent_id, child_id):
        link_id = self._new_id()
        link = self._base("link", link_id)
        link["from"] = {"entity_type": "person", "entity_id": parent_id}
        link["to"] = {"entity_type": "person", "entity_id": child_id}
        link["label"] = "parent_of"
        link["label_reverse"] = "child_of"
        link["category"] = "other"
        link["bidirectional"] = False
        link["confidence"] = self.default_confidence
        self.links[link_id] = link

    # -- bundle output -----------------------------------------------------

    def manifest(self, family_name=None):
        ## @return AXGF manifest dict for the converted data.
        manifest = {
            "axgf": AXGF_VERSION,
            "created_at": self.now,
            "updated_at": self.now,
            "generator": GENERATOR,
            "stats": {
                "persons": len(self.persons),
                "families": len(self.families),
                "events": len(self.events),
                "links": len(self.links),
                "occupations": len(self.occupations),
                "sources": len(self.sources),
                "places": len(self.places),
                "documents": len(self.documents)},
            "privacy": {
                "contains_living_persons": any(
                    p["identity"]["is_living"] for p in self.persons.values()),
                "living_persons_redacted": False,
                "gdpr_compliant": False},
            "compatibility": {"gedcom_source": "5.5.1"}}
        if family_name:
            manifest["family"] = {"name": family_name}
        return manifest

    def write_bundle(self, output_path, family_name=None, schema_path=None):
        ## @brief Write the .axgf ZIP bundle and the concordance file.
        output_path = Path(output_path)
        manifest = self.manifest(family_name)
        concordance = {"generated_at": self.now, "files": self.concordance}

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", _dumps(manifest))
            zf.writestr("concordance.json", _dumps(concordance))
            if schema_path and Path(schema_path).is_file():
                zf.writestr("schema/axgf-1.0.schema.json",
                            Path(schema_path).read_text(encoding="utf-8"))

            collections = (("persons", self.persons),
                           ("families", self.families),
                           ("events", self.events),
                           ("links", self.links),
                           ("occupations", self.occupations),
                           ("sources", self.sources),
                           ("places", self.places))
            for folder, entities in collections:
                for entity_id, entity in entities.items():
                    zf.writestr(f"{folder}/{entity_id}.json", _dumps(entity))

            ## documents/index.json is a map of uuid -> document metadata
            ## (the shape the axgf reader imports); binary payloads live as
            ## plain ZIP entries under documents/files/** and are streamed
            ## from disk one at a time so large media sets never sit wholly
            ## in memory. A present document either points at a local file
            ## (_local_path, streamed with ZipFile.write) or carries its
            ## bytes inline (_payload, e.g. read from a remote source).
            doc_index = {}
            for doc_id, doc in self.documents.items():
                local_path = doc.pop("_local_path", None)
                payload = doc.pop("_payload", None)
                if "file" in doc and doc["file"] and "path" in doc["file"]:
                    if local_path is not None:
                        zf.write(local_path, doc["file"]["path"])
                    elif payload is not None:
                        zf.writestr(doc["file"]["path"], payload)
                doc_index[doc_id] = doc
            zf.writestr("documents/index.json", _dumps(doc_index))

        concordance_path = output_path.with_suffix(".concordance.json")
        concordance_path.write_text(_dumps(concordance), encoding="utf-8")
        return output_path, concordance_path


def _dumps(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="gedcom2axgf",
        description="Convert one or more GEDCOM 5.5.1 files into a single "
                    "AXGF 1.0 bundle with a GEDCOM<->AXGF concordance file.")
    parser.add_argument("inputs", nargs="+",
                        help="GEDCOM input file(s) (.ged)")
    parser.add_argument("-o", "--output", default="output.axgf",
                        help="Output bundle path (default: output.axgf)")
    parser.add_argument("--family-name", default=None,
                        help="Family name recorded in the manifest")
    parser.add_argument("--lang", default="und",
                        help="BCP 47 language for place names (default: und)")
    parser.add_argument("--default-confidence", type=float, default=0.8,
                        help="Confidence applied to imported facts "
                             "(default: 0.8)")
    parser.add_argument("--emit-parent-links", action="store_true",
                        help="Also emit parent_of Link entities in addition "
                             "to Family children")
    parser.add_argument("--schema", default=None,
                        help="Path to axgf-1.0.schema.json to embed in the "
                             "bundle (looked up next to this script when "
                             "omitted)")
    parser.add_argument("--validate", action="store_true",
                        help="Validate produced entities with jsonschema "
                             "(requires the schema)")
    args = parser.parse_args(argv)

    schema_path = args.schema
    if schema_path is None:
        candidate = Path(__file__).parent / "axgf-1.0.schema.json"
        schema_path = candidate if candidate.is_file() else None

    converter = Converter(default_confidence=args.default_confidence,
                          lang=args.lang,
                          emit_parent_links=args.emit_parent_links)

    for input_path in args.inputs:
        if not Path(input_path).is_file():
            parser.error(f"input file not found: {input_path}")
        converter.convert_file(input_path)
        print(f"parsed: {input_path}")

    bundle, concordance = converter.write_bundle(
        args.output, family_name=args.family_name, schema_path=schema_path)

    stats = converter.manifest()["stats"]
    print(f"\nbundle:      {bundle}")
    print(f"concordance: {concordance}")
    print("stats:       " + ", ".join(f"{k}={v}" for k, v in stats.items()))

    if args.validate:
        _validate(converter, schema_path)
    return 0


def _validate(converter, schema_path):
    ## @brief Validate every produced entity against the AXGF JSON Schema.
    if not schema_path or not Path(schema_path).is_file():
        print("validate: schema not found, skipped", file=sys.stderr)
        return
    try:
        import jsonschema
    except ImportError:
        print("validate: jsonschema not installed, skipped", file=sys.stderr)
        return

    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    registry = schema.get("$defs", {})
    errors = 0
    groups = (("person", converter.persons), ("family", converter.families),
              ("event", converter.events), ("link", converter.links),
              ("occupation", converter.occupations),
              ("source", converter.sources), ("place", converter.places),
              ("document", converter.documents))
    for kind, entities in groups:
        sub_schema = {"$defs": registry, **registry.get(kind, {})}
        for entity_id, entity in entities.items():
            try:
                jsonschema.validate(entity, sub_schema)
            except jsonschema.ValidationError as exc:
                errors += 1
                print(f"validate: {kind}/{entity_id}: {exc.message}",
                      file=sys.stderr)
    print(f"validate: {'OK — 0 errors' if errors == 0 else f'{errors} errors'}")


if __name__ == "__main__":
    sys.exit(main())
