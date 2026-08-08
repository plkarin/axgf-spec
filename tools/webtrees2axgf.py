#!/usr/bin/env python3
## @file    webtrees2axgf.py
## @brief   Extract a complete, self-contained AXGF 1.0 bundle straight from a
##          live webtrees installation - including the media file *bytes* that
##          a GEDCOM export can only reference by name.
##
## @details GEDCOM's OBJE tag carries a filename, never the file: a webtrees
##          GEDCOM export lists every document as status "referenced" with no
##          payload. This tool reads the installation directly - the database
##          for the genealogy and the media directory for the files - and
##          emits Documents with status "present", real bytes, size and
##          sha256, producing a genuinely self-contained bundle. Media
##          recovery is the tool's entire reason to exist.
##
##          The genealogical heavy lifting is delegated to gedcom2axgf.py:
##          webtrees stores the complete raw GEDCOM record for every
##          individual and family in i_gedcom / f_gedcom, so those strings are
##          reassembled into a synthetic GEDCOM document and fed straight
##          through that module's battle-tested parser and bundle writer. This
##          tool's own work is joining media bytes and webtrees-only metadata
##          (coordinates, change timestamps, indexed name variants, link
##          relationships) onto the result.
##
##          Both PostgreSQL and MySQL/MariaDB webtrees back ends are
##          supported; the engine is detected silently from config.ini.php or
##          the port, and only the driver for the selected engine is imported.
##          Database access is strictly read-only and asserted in code.
##
## @author  Axiom / axgf-spec project
## @license CC0-1.0

import argparse
import os
import re
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

## gedcom2axgf lives next to this file; reuse it as a library rather than
## copying its parser or writer.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gedcom2axgf as g2a  # noqa: E402

GENERATOR = {"name": "webtrees2axgf", "version": "1.0.0",
             "url": "https://github.com/plkarin/axgf-spec"}

## Required tables (with the configured prefix). Missing any of these aborts.
REQUIRED_TABLES = ["individuals", "families", "media", "media_file", "link"]
## Optional enrichment tables - warn and continue when absent.
OPTIONAL_TABLES = ["places", "placelinks", "place_location", "name", "dates",
                   "change", "other", "sources", "gedcom", "gedcom_setting"]

## webtrees source_media_type -> AXGF document_type, confident mappings only.
## Anything else falls back to "photo" for images and "other" otherwise.
MEDIA_TYPE_MAP = {"photo": "photo", "tombstone": "gravestone_photo",
                  "newspaper": "newspaper_clipping", "audio": "audio",
                  "video": "video", "film": "video"}


# ---------------------------------------------------------------------------
# config.ini.php
# ---------------------------------------------------------------------------

def parse_config_ini(path):
    ## @brief  Parse a webtrees config.ini.php defensively.
    ## @details The file is PHP whose data lines are simple key="value" pairs,
    ##          possibly with a leading "; <?php ... ?>" guard line, comments,
    ##          unquoted values and varying whitespace.
    ## @return dict of lowercased keys -> string values.
    conf = {}
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        if line.startswith("<?") or line.startswith("?>"):
            continue
        m = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.*)$', line)
        if not m:
            continue
        key = m.group(1).lower()
        val = m.group(2).strip()
        ## strip an inline trailing comment on unquoted values
        if val[:1] not in ('"', "'"):
            val = re.split(r'\s+;', val, 1)[0].strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        conf[key] = val
    return conf


# ---------------------------------------------------------------------------
# engine selection + dialect
# ---------------------------------------------------------------------------

class Dialect:
    ## @brief Per-engine SQL differences, isolated so extraction logic stays
    ##        engine-agnostic. Every query the tool issues is portable ANSI
    ##        SQL; only identifier quoting and connection/read-only setup live
    ##        here.

    def __init__(self, engine):
        self.engine = engine  # "postgres" | "mysql"

    def quote(self, ident):
        ## @return identifier quoted for the engine.
        if self.engine == "postgres":
            return '"%s"' % ident.replace('"', '""')
        return "`%s`" % ident.replace("`", "``")


def detect_engine(conf, cli_db_type, cli_port):
    ## @brief  Resolve the database engine silently (see module docstring).
    ## @return "postgres" | "mysql" | None (None == try both).
    if cli_db_type:
        return _normalize_engine(cli_db_type)
    dbtype = (conf.get("dbtype") or "").lower()
    if dbtype:
        eng = _normalize_engine(dbtype)
        if eng:
            return eng
    port = cli_port or _int(conf.get("dbport"))
    if port == 5432:
        return "postgres"
    if port == 3306:
        return "mysql"
    return None  # ambiguous: caller will try both


def _normalize_engine(value):
    v = value.lower()
    if v in ("postgres", "postgresql", "pgsql", "pg", "psql"):
        return "postgres"
    if v in ("mysql", "mysqli", "mariadb", "maria"):
        return "mysql"
    if v in ("sqlite", "sqlite3", "sqlsrv", "mssql"):
        raise SystemExit("error: webtrees back end %r is not supported; this "
                         "tool targets PostgreSQL and MySQL/MariaDB." % value)
    return None


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def connect_postgres(host, port, user, password, dbname):
    ## @brief Open a read-only, autocommit PostgreSQL connection, importing
    ##        the driver lazily and printing the pip command if it is absent.
    try:
        import psycopg2  # type: ignore
        conn = psycopg2.connect(host=host, port=port, user=user,
                                password=password, dbname=dbname)
        conn.set_session(readonly=True, autocommit=True)
        return conn
    except ImportError:
        pass
    try:
        import psycopg  # type: ignore
    except ImportError:
        raise SystemExit("error: no PostgreSQL driver found. Install one:\n"
                         "    pip install psycopg2-binary")
    conn = psycopg.connect(host=host, port=port, user=user,
                           password=password, dbname=dbname, autocommit=True)
    with conn.cursor() as c:
        c.execute("SET default_transaction_read_only = on")
    return conn


def connect_mysql(host, port, user, password, dbname):
    ## @brief Open a read-only, autocommit MySQL/MariaDB connection.
    try:
        import pymysql  # type: ignore
    except ImportError:
        raise SystemExit("error: no MySQL driver found. Install one:\n"
                         "    pip install PyMySQL")
    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                           database=dbname, autocommit=True,
                           charset="utf8mb4")
    with conn.cursor() as c:
        ## best-effort: make the session refuse writes; the SELECT-only guard
        ## below is the real guarantee.
        try:
            c.execute("SET SESSION TRANSACTION READ ONLY")
        except Exception:
            pass
    return conn


class ReadOnlyDB:
    ## @brief  A connection wrapper that will execute nothing but SELECT.
    ## @details The requirement is that a tool pointed at a production
    ##          genealogy database be provably harmless; every data query
    ##          therefore passes through select()/select_one(), which assert
    ##          the statement is a SELECT before it reaches the server.

    def __init__(self, conn, dialect):
        self.conn = conn
        self.dialect = dialect

    def _assert_select(self, sql):
        head = sql.lstrip().split(None, 1)[0].upper() if sql.strip() else ""
        if head not in ("SELECT", "WITH"):
            raise RuntimeError("refusing non-SELECT statement: %r" % sql[:60])

    def select(self, sql, params=None):
        ## @return list of tuples for a SELECT.
        self._assert_select(sql)
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or ())
            return cur.fetchall()
        finally:
            cur.close()

    def select_one(self, sql, params=None):
        rows = self.select(sql, params)
        return rows[0] if rows else None

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# schema introspection
# ---------------------------------------------------------------------------

def introspect_schema(db, prefix, base_names):
    ## @brief  Read information_schema for the columns of each prefixed table.
    ## @return dict base_name -> set(column names); empty set means absent.
    wanted = [prefix + name for name in base_names]
    placeholders = ",".join(["%s"] * len(wanted))
    rows = db.select(
        "SELECT table_name, column_name FROM information_schema.columns "
        "WHERE table_name IN (%s)" % placeholders, wanted)
    found = {name: set() for name in base_names}
    lut = {prefix + name: name for name in base_names}
    for table_name, column_name in rows:
        base = lut.get(table_name) or lut.get(str(table_name).lower())
        if base:
            found[base].add(str(column_name).lower())
    return found


# ---------------------------------------------------------------------------
# MIME sniffing from magic bytes
# ---------------------------------------------------------------------------

def sniff_mime(head):
    ## @brief  Detect a MIME type from a file's leading bytes.
    ## @details multimedia_format in webtrees is a user-editable field and can
    ##          lie, so the real type is taken from the content, never that
    ##          field.
    ## @param  head First bytes of the file (>= 16 recommended).
    ## @return MIME type string.
    if head[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if head[:4] == b"%PDF":
        return "application/pdf"
    if head[:4] in (b"II*\x00", b"MM\x00*"):
        return "image/tiff"
    if head[:2] == b"BM":
        return "image/bmp"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head[4:8] == b"ftyp":
        return "video/mp4"
    if head[:3] == b"ID3" or head[:2] == b"\xff\xfb":
        return "audio/mpeg"
    if head[:4] == b"OggS":
        return "audio/ogg"
    if head[:4] == b"PK\x03\x04":
        return "application/zip"
    return "application/octet-stream"


def mime_from_extension(ext):
    ## @brief Fallback MIME from a filename extension (used for known_missing
    ##        files whose bytes we never see).
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "gif": "image/gif", "pdf": "application/pdf", "tif": "image/tiff",
            "tiff": "image/tiff", "bmp": "image/bmp", "webp": "image/webp",
            "mp4": "video/mp4", "mp3": "audio/mpeg", "wav": "audio/wav",
            "txt": "text/plain"}.get(ext.lower(), "application/octet-stream")


# ---------------------------------------------------------------------------
# extractor
# ---------------------------------------------------------------------------

class WebtreesExtractor:
    ## @brief Reads one webtrees tree and produces an AXGF bundle.

    def __init__(self, db, prefix, schema, media_dir, tree_id, args):
        self.db = db
        self.prefix = prefix
        self.schema = schema
        self.media_dir = media_dir
        self.tree_id = tree_id
        self.args = args
        self.converter = g2a.Converter(
            default_confidence=args.default_confidence, lang=args.lang)
        ## sets for classifying wt_link endpoints
        self.indi_ids = set()
        self.fam_ids = set()
        self.source_ids = set()
        ## media xref (m_id) -> [document UUID, ...] for wt_link joining,
        ## covering the rare case of several files under one media record.
        self.docs_by_media = {}
        ## reporting counters
        self.report = {"media_present": 0, "media_missing": 0,
                       "media_unreadable": 0, "payload_bytes": 0,
                       "documents": 0, "places_with_coords": 0,
                       "updated_at_set": 0, "name_variants_added": 0,
                       "links_extra": 0}
        self.enrichment_notes = []

    def tbl(self, base):
        return self.prefix + base

    def has(self, base, *cols):
        ## @return True if the optional table exists (and, if given, all cols).
        present = self.schema.get(base)
        if not present:
            return False
        return all(c in present for c in cols)

    # -- record extraction -------------------------------------------------

    def build_synthetic_gedcom(self):
        ## @brief Reassemble i_gedcom / f_gedcom / notes / sources for the
        ##        chosen tree into one GEDCOM document with a minimal HEAD and
        ##        TRLR, ready for the gedcom2axgf parser.
        q = self.db.select
        parts = ["0 HEAD", "1 SOUR webtrees", "1 GEDC", "2 VERS 5.5.1",
                 "2 FORM LINEAGE-LINKED", "1 CHAR UTF-8"]

        for (i_id, gedcom) in q(
                "SELECT i_id, i_gedcom FROM %s WHERE i_file = %%s"
                % self.tbl("individuals"), (self.tree_id,)):
            self.indi_ids.add(i_id)
            if gedcom:
                parts.append(gedcom.rstrip("\n"))

        for (f_id, gedcom) in q(
                "SELECT f_id, f_gedcom FROM %s WHERE f_file = %%s"
                % self.tbl("families"), (self.tree_id,)):
            self.fam_ids.add(f_id)
            if gedcom:
                parts.append(gedcom.rstrip("\n"))

        ## SOUR records: prefer wt_sources, fall back to wt_other.
        if self.has("sources", "s_gedcom"):
            for (s_id, gedcom) in q(
                    "SELECT s_id, s_gedcom FROM %s WHERE s_file = %%s"
                    % self.tbl("sources"), (self.tree_id,)):
                self.source_ids.add(s_id)
                if gedcom:
                    parts.append(gedcom.rstrip("\n"))

        ## NOTE / SOUR / REPO / SUBM live in wt_other; include them so inline
        ## xref references (1 NOTE @Nx@) resolve during parsing.
        if self.has("other", "o_gedcom"):
            for (o_id, o_type, gedcom) in q(
                    "SELECT o_id, o_type, o_gedcom FROM %s WHERE o_file = %%s"
                    % self.tbl("other"), (self.tree_id,)):
                if o_type == "SOUR":
                    self.source_ids.add(o_id)
                if gedcom:
                    parts.append(gedcom.rstrip("\n"))

        parts.append("0 TRLR")
        return "\n".join(parts)

    # -- media -------------------------------------------------------------

    def media_rows(self):
        ## @brief  Fetch media records + their file rows for the tree.
        ## @return list of (m_id, [file_row, ...]) where each file_row is a
        ##         dict with keys multimedia_file_refn / multimedia_format /
        ##         source_media_type / descriptive_title.
        ## @details webtrees 2.x reads wt_media_file. webtrees 1.x has no such
        ##          table, so the file rows are reconstructed from the OBJE
        ##          record text in wt_media.m_gedcom (best-effort - see README).
        q = self.db.select
        media_ids = [r[0] for r in q(
            "SELECT m_id FROM %s WHERE m_file = %%s"
            % self.tbl("media"), (self.tree_id,))]

        if self.schema.get("media_file"):
            cols = ["m_id", "multimedia_file_refn", "multimedia_format",
                    "source_media_type", "descriptive_title"]
            avail = [c for c in cols
                     if c in self.schema.get("media_file", set())]
            file_map = {}
            for row in q("SELECT %s FROM %s WHERE m_file = %%s"
                         % (", ".join(avail), self.tbl("media_file")),
                         (self.tree_id,)):
                d = dict(zip(avail, row))
                file_map.setdefault(d["m_id"], []).append(d)
            return [(mid, file_map.get(mid, [])) for mid in media_ids]

        ## webtrees 1.x fallback: parse FILE/FORM/TITL out of m_gedcom.
        file_map = {}
        if self.has("media", "m_gedcom"):
            for (m_id, gedcom) in q(
                    "SELECT m_id, m_gedcom FROM %s WHERE m_file = %%s"
                    % self.tbl("media"), (self.tree_id,)):
                for refn in re.findall(r"^\d+ FILE (.+)$", gedcom or "",
                                       re.MULTILINE):
                    fm = re.search(r"^\d+ FORM (.+)$", gedcom, re.MULTILINE)
                    tt = re.search(r"^\d+ TITL (.+)$", gedcom, re.MULTILINE)
                    file_map.setdefault(m_id, []).append({
                        "multimedia_file_refn": refn.strip(),
                        "multimedia_format": (fm.group(1).strip()
                                              if fm else ""),
                        "source_media_type": "",
                        "descriptive_title": (tt.group(1).strip()
                                              if tt else "")})
        return [(mid, file_map.get(mid, [])) for mid in media_ids]

    def attach_media(self):
        ## @brief The core of the tool: turn every media file on disk into a
        ##        Document with real bytes, sha256 and content-sniffed MIME;
        ##        record documented gaps as known_missing.
        conv = self.converter
        titles = self._media_titles()      # m_id -> title from m_gedcom
        for m_id, files in self.media_rows():
            if not files:
                ## media record with no file row: still emit a documented gap
                self._emit_document(m_id, None, titles.get(m_id, ""),
                                    primary=True)
                continue
            for idx, fr in enumerate(files):
                self._emit_document(m_id, fr, titles.get(m_id, ""),
                                    primary=(idx == 0))

    def _media_titles(self):
        ## @brief Extract the OBJE-level TITL from each m_gedcom (fallback
        ##        caption when descriptive_title is empty).
        titles = {}
        if not self.has("media", "m_gedcom"):
            return titles
        for (m_id, gedcom) in self.db.select(
                "SELECT m_id, m_gedcom FROM %s WHERE m_file = %%s"
                % self.tbl("media"), (self.tree_id,)):
            if gedcom:
                m = re.search(r"^\d+ TITL (.+)$", gedcom, re.MULTILINE)
                if m:
                    titles[m_id] = m.group(1).strip()
        return titles

    def _emit_document(self, m_id, file_row, obje_title, primary):
        ## @brief Build one Document entity (present / known_missing) and add
        ##        it to the converter, streaming bytes from disk one at a time.
        conv = self.converter
        ## primary file of a media record keeps the media xref's UUID so that
        ## INDI/FAM `OBJE @Mx@` references resolve to it; extra files get fresh
        ## UUIDs and are linked through wt_link only.
        doc_id = conv._uuid_for("@%s@" % m_id) if primary else conv._new_id()
        refn = (file_row or {}).get("multimedia_file_refn") or ""
        fmt = ((file_row or {}).get("multimedia_format") or "").lower()
        smt = ((file_row or {}).get("source_media_type") or "").lower()
        caption = ((file_row or {}).get("descriptive_title") or obje_title
                   or "")
        ext = (Path(refn).suffix.lstrip(".").lower() or fmt or "bin")

        doc = conv._base("document", doc_id)
        doc["filename"] = Path(refn).name or (m_id + "." + ext)
        doc["caption"] = caption
        doc["linked_to"] = []

        local = (self.media_dir / refn) if refn else None
        present, size, sha, mime = self._read_file(local)
        if present:
            doc["status"] = "present"
            doc["mime_type"] = mime
            doc["file"] = {"path": "documents/files/%s.%s" % (doc_id, ext),
                           "size_bytes": size, "sha256": sha}
            doc["_local_path"] = str(local)
            self.report["media_present"] += 1
            self.report["payload_bytes"] += size
        else:
            doc["status"] = "known_missing"
            doc["mime_type"] = mime_from_extension(ext)
            if refn:
                doc["url"] = refn
            self.report["media_missing"] += 1
        doc["document_type"] = self._document_type(smt, doc["mime_type"])
        conv.documents[doc_id] = doc
        self.docs_by_media.setdefault(m_id, []).append(doc_id)
        self.report["documents"] += 1

    def _read_file(self, local):
        ## @brief  Read a media file in chunks: compute size + sha256 without
        ##         holding the whole file in memory, and sniff its MIME.
        ## @return (present, size_bytes, sha256_hex, mime) - present is False
        ##         for a missing or unreadable file (both documented as gaps).
        if not local or not local.is_file():
            return False, 0, "", "application/octet-stream"
        try:
            h = hashlib.sha256()
            size = 0
            head = b""
            with open(local, "rb") as fh:
                while True:
                    chunk = fh.read(1 << 20)
                    if not chunk:
                        break
                    if not head:
                        head = chunk[:16]
                    h.update(chunk)
                    size += len(chunk)
            return True, size, h.hexdigest(), sniff_mime(head)
        except (OSError, PermissionError) as exc:
            ## An unreadable file (permissions) is a documented gap, not a
            ## crash.
            self.report["media_unreadable"] += 1
            sys.stderr.write("warning: cannot read media %s: %s\n"
                             % (local, exc))
            return False, 0, "", "application/octet-stream"

    def _document_type(self, source_media_type, mime):
        mapped = MEDIA_TYPE_MAP.get(source_media_type)
        if mapped:
            return mapped
        return "photo" if mime.startswith("image/") else "other"

    # -- webtrees-only enrichment -----------------------------------------

    def link_documents(self):
        ## @brief Link Documents to their subjects using wt_link (l_to = media
        ##        id). This is webtrees-authoritative and also covers family
        ##        and source links that the INDI-side OBJE parsing misses.
        if not self.has("link", "l_from", "l_to", "l_type"):
            self.enrichment_notes.append("wt_link: absent - no document links")
            return
        conv = self.converter
        docs_by_media = self.docs_by_media
        rows = self.db.select(
            "SELECT l_from, l_to FROM %s WHERE l_file = %%s AND l_type = 'OBJE'"
            % self.tbl("link"), (self.tree_id,))
        linked = 0
        for l_from, l_to in rows:
            etype = ("person" if l_from in self.indi_ids else
                     "family" if l_from in self.fam_ids else
                     "source" if l_from in self.source_ids else None)
            if etype is None:
                continue
            entity_id = conv._uuid_for("@%s@" % l_from)
            for doc_id in docs_by_media.get(l_to, []):
                doc = conv.documents.get(doc_id)
                if not doc:
                    continue
                existing = {(x["entity_type"], x["entity_id"])
                            for x in doc["linked_to"]}
                if (etype, entity_id) not in existing:
                    doc["linked_to"].append({"entity_type": etype,
                                             "entity_id": entity_id,
                                             "role": "subject"})
                    linked += 1
                ## mirror onto the family record (persons already carry
                ## documents from the INDI-side OBJE parse)
                if etype == "family" and entity_id in conv.families:
                    fam = conv.families[entity_id]
                    refs = fam.setdefault("documents", [])
                    if all(r.get("document_id") != doc_id for r in refs):
                        refs.append({"document_id": doc_id})
        self.enrichment_notes.append(
            "wt_link: %d OBJE rows, %d document-subject links" % (len(rows),
                                                                  linked))

    def enrich_coordinates(self):
        ## @brief Attach real lat/lon to Place entities from
        ##        wt_place_location, so places carry coordinates rather than a
        ##        bare name string.
        if not self.has("place_location", "place", "latitude", "longitude"):
            self.enrichment_notes.append("wt_place_location: absent - no "
                                         "coordinates")
            return
        coords = {}
        for row in self.db.select(
                "SELECT place, latitude, longitude FROM %s"
                % self.tbl("place_location")):
            place, lat, lon = row
            if place is None or lat is None or lon is None:
                continue
            coords[self._norm_place(place)] = (float(lat), float(lon))
        if not coords:
            self.enrichment_notes.append("wt_place_location: 0 usable rows")
            return
        applied = 0
        for place in self.converter.places.values():
            name = place["names"][0]["value"]
            key = self._norm_place(name)
            leaf = self._norm_place(name.split(",")[0])
            hit = coords.get(key) or coords.get(leaf)
            if hit:
                place["coordinates"] = {"lat": hit[0], "lon": hit[1]}
                applied += 1
        self.report["places_with_coords"] = applied
        self.enrichment_notes.append(
            "wt_place_location: %d located places, %d matched into bundle"
            % (len(coords), applied))

    def enrich_updated_at(self):
        ## @brief Carry wt_change last-modified timestamps into updated_at.
        if not self.has("change", "xref", "change_time"):
            self.enrichment_notes.append("wt_change: absent - no timestamps")
            return
        conv = self.converter
        latest = {}
        for xref, ctime in self.db.select(
                "SELECT xref, change_time FROM %s WHERE gedcom_id = %%s"
                % self.tbl("change"), (self.tree_id,)):
            if ctime is None:
                continue
            if xref not in latest or ctime > latest[xref]:
                latest[xref] = ctime
        applied = 0
        for xref, ctime in latest.items():
            uuid_ = conv._xref_map.get("@%s@" % xref)
            if not uuid_:
                continue
            iso = self._iso(ctime)
            for coll in (conv.persons, conv.families, conv.documents,
                         conv.sources):
                if uuid_ in coll:
                    coll[uuid_]["updated_at"] = iso
                    applied += 1
                    break
        self.report["updated_at_set"] = applied
        self.enrichment_notes.append(
            "wt_change: %d changed records, %d updated_at set"
            % (len(latest), applied))

    def enrich_name_variants(self):
        ## @brief Add name variants webtrees indexed in wt_name that are not
        ##        already present on the person from the GEDCOM NAME parse.
        if not self.has("name", "n_id", "n_full"):
            self.enrichment_notes.append("wt_name: absent - no variants")
            return
        conv = self.converter
        rows = self.db.select(
            "SELECT n_id, n_full, n_type FROM %s WHERE n_file = %%s"
            % self.tbl("name"), (self.tree_id,))
        added = 0
        for n_id, n_full, n_type in rows:
            if not n_full:
                continue
            uuid_ = conv._xref_map.get("@%s@" % n_id)
            person = conv.persons.get(uuid_) if uuid_ else None
            if not person:
                continue
            display = re.sub(r"\s+", " ", n_full.replace("/", " ")).strip()
            identity = person["identity"]
            known = {identity["name"]["display"]}
            known.update(n.get("display", "")
                         for n in identity.get("names", []))
            if display and display not in known:
                identity.setdefault("names", []).append(
                    {"display": display, "components": [], "type": "alias"})
                added += 1
        self.report["name_variants_added"] = added
        self.enrichment_notes.append(
            "wt_name: %d indexed names, %d new variants added"
            % (len(rows), added))

    def inspect_links(self):
        ## @brief Report the distinct wt_link relationship types present, so
        ##        the operator can see what webtrees tracked. Genealogical
        ##        types (FAMC/FAMS/HUSB/WIFE/CHIL/OBJE/NOTE/SOUR) are already
        ##        represented by the GEDCOM records and media; anything else is
        ##        surfaced as a note.
        if not self.has("link", "l_type"):
            return
        rows = self.db.select(
            "SELECT l_type, COUNT(*) FROM %s WHERE l_file = %%s "
            "GROUP BY l_type ORDER BY l_type" % self.tbl("link"),
            (self.tree_id,))
        summary = ", ".join("%s=%d" % (t, n) for t, n in rows)
        self.enrichment_notes.append("wt_link types: %s" % (summary or "none"))

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _norm_place(name):
        return re.sub(r"\s+", " ", (name or "").strip().lower())

    @staticmethod
    def _iso(value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
        text = str(value).strip().replace(" ", "T")
        if text and not text.endswith("Z"):
            text += "Z"
        return text

    # -- orchestration -----------------------------------------------------

    def run(self):
        ## @brief Full extraction pipeline. Returns the gedcom2axgf Converter,
        ##        fully populated, ready to write.
        text = self.build_synthetic_gedcom()
        source_name = "webtrees:tree%s" % self.tree_id

        if self.args.skip_media:
            ## structure only: parse genealogy, emit documents as referenced
            ## (name only, no disk access) - the fast, GEDCOM-equivalent path.
            self.converter.convert_text(text, source_name, base_dir=None)
            self._referenced_only_media()
        else:
            ## seed media Documents before individuals are converted, so the
            ## INDI-side `OBJE @Mx@` references resolve to real Documents and
            ## person.documents links are produced for free.
            self.converter.convert_text(
                text, source_name, base_dir=None,
                pre_convert=lambda conv: self.attach_media())
            self.link_documents()

        self.inspect_links()
        self.enrich_coordinates()
        self.enrich_updated_at()
        self.enrich_name_variants()
        return self.converter

    def _referenced_only_media(self):
        ## @brief --skip-media: document metadata without touching the disk.
        conv = self.converter
        titles = self._media_titles()
        for m_id, files in self.media_rows():
            fr = files[0] if files else {}
            doc_id = conv._uuid_for("@%s@" % m_id)
            refn = fr.get("multimedia_file_refn") or ""
            ext = Path(refn).suffix.lstrip(".").lower() or "bin"
            doc = conv._base("document", doc_id)
            doc["filename"] = Path(refn).name or m_id
            doc["mime_type"] = mime_from_extension(ext)
            doc["caption"] = (fr.get("descriptive_title")
                              or titles.get(m_id, "") or "")
            doc["status"] = "referenced"
            if refn:
                doc["url"] = refn
            doc["document_type"] = self._document_type(
                (fr.get("source_media_type") or "").lower(), doc["mime_type"])
            doc["linked_to"] = []
            conv.documents[doc_id] = doc
            self.docs_by_media.setdefault(m_id, []).append(doc_id)
            self.report["documents"] += 1
        self.link_documents()


# ---------------------------------------------------------------------------
# tree resolution
# ---------------------------------------------------------------------------

def list_trees(db, prefix, schema):
    ## @return list of (tree_id, name) available in the database.
    if schema.get("gedcom"):
        rows = db.select("SELECT gedcom_id, gedcom_name FROM %sgedcom "
                         "ORDER BY gedcom_id" % prefix)
        trees = [(r[0], r[1]) for r in rows if r[0] and int(r[0]) > 0]
        if trees:
            return trees
    ## fall back to distinct i_file values
    rows = db.select("SELECT DISTINCT i_file FROM %sindividuals "
                     "ORDER BY i_file" % prefix)
    return [(r[0], "tree %s" % r[0]) for r in rows]


def tree_title(db, prefix, schema, tree_id):
    if schema.get("gedcom_setting"):
        row = db.select_one(
            "SELECT setting_value FROM %sgedcom_setting WHERE gedcom_id = %%s "
            "AND setting_name = 'title'" % prefix, (tree_id,))
        if row and row[0]:
            return row[0]
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser():
    p = argparse.ArgumentParser(
        prog="webtrees2axgf",
        description="Extract a self-contained AXGF 1.0 bundle (including media "
                    "bytes) directly from a live webtrees database.")
    p.add_argument("--config", help="Path to webtrees config.ini.php "
                   "(reads host, port, user, password, dbname, prefix, "
                   "engine - so no password is ever typed).")
    p.add_argument("--media-dir", help="webtrees media directory "
                   "(default: <config-dir>/media).")
    p.add_argument("--tree-id", help="Tree (gedcom_id) to extract.")
    p.add_argument("-o", "--output", default="webtrees.axgf",
                   help="Output bundle path (default: webtrees.axgf).")

    p.add_argument("--db-type", choices=["postgres", "mysql"],
                   help="Override engine detection (rarely needed).")
    p.add_argument("--db-host")
    p.add_argument("--db-port", type=int)
    p.add_argument("--db-name")
    p.add_argument("--db-user")
    p.add_argument("--db-password-env",
                   help="Name of an environment variable holding the DB "
                        "password (never pass a password on the command "
                        "line).")

    p.add_argument("--list-trees", action="store_true",
                   help="List available trees and exit.")
    p.add_argument("--default-confidence", type=float, default=0.8,
                   help="Confidence applied to imported facts (default 0.8).")
    p.add_argument("--lang", default="en",
                   help="BCP 47 tag for place names (default en).")
    p.add_argument("--skip-media", action="store_true",
                   help="Structure only: emit documents as referenced without "
                        "reading media files (fast dry run).")
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would be extracted; write nothing.")
    return p


def resolve_connection(args):
    ## @brief  Merge config.ini.php with CLI flags and open the connection.
    ## @return (ReadOnlyDB, prefix, config_dict, engine).
    conf = {}
    if args.config:
        if not Path(args.config).is_file():
            raise SystemExit("error: config not found: %s" % args.config)
        conf = parse_config_ini(args.config)

    host = args.db_host or conf.get("dbhost") or "localhost"
    port = args.db_port or _int(conf.get("dbport"))
    user = args.db_user or conf.get("dbuser")
    dbname = args.db_name or conf.get("dbname")
    prefix = conf.get("tblpfx") or "wt_"

    ## password: env var (preferred) or config file. Never a CLI flag, never
    ## a hardcoded default.
    password = None
    if args.db_password_env:
        password = os.environ.get(args.db_password_env)
        if password is None:
            raise SystemExit("error: environment variable %r is not set"
                             % args.db_password_env)
    elif conf.get("dbpass") is not None:
        password = conf.get("dbpass")
    elif os.environ.get("WEBTREES_DB_PASSWORD") is not None:
        password = os.environ["WEBTREES_DB_PASSWORD"]

    if not user or not dbname or password is None:
        raise SystemExit(
            "error: incomplete database credentials. Provide --config "
            "pointing at config.ini.php, or --db-user/--db-name plus a "
            "password via --db-password-env. This tool refuses to run with a "
            "default password.")

    engine = detect_engine(conf, args.db_type, port)
    dialect_engine, conn = open_connection(engine, host, port, user, password,
                                           dbname)
    return (ReadOnlyDB(conn, Dialect(dialect_engine)), prefix, conf,
            dialect_engine)


def open_connection(engine, host, port, user, password, dbname):
    ## @brief Open the connection, trying both engines when detection was
    ##        ambiguous. Returns (resolved_engine, connection).
    attempts = []
    if engine == "postgres":
        attempts = [("postgres", 5432)]
    elif engine == "mysql":
        attempts = [("mysql", 3306)]
    else:
        attempts = [("postgres", 5432), ("mysql", 3306)]

    last_err = None
    for eng, default_port in attempts:
        use_port = port or default_port
        try:
            if eng == "postgres":
                return eng, connect_postgres(host, use_port, user, password,
                                             dbname)
            return eng, connect_mysql(host, use_port, user, password, dbname)
        except SystemExit:
            raise
        except Exception as exc:  # connection failure - try the next engine
            last_err = exc
    raise SystemExit("error: could not connect to the database: %s" % last_err)


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    db, prefix, conf, engine = resolve_connection(args)
    try:
        ## schema introspection up front
        schema = introspect_schema(db, prefix,
                                   REQUIRED_TABLES + OPTIONAL_TABLES)
        missing = [prefix + t for t in REQUIRED_TABLES
                   if not schema.get(t)]

        ## webtrees 1.x fallback: no wt_media_file but wt_media present.
        one_x = (not schema.get("media_file")) and bool(schema.get("media"))
        if one_x and "media_file" in [m[len(prefix):] for m in missing]:
            sys.stderr.write(
                "warning: wt_media_file absent but wt_media present - this "
                "looks like webtrees 1.x. Media support is best-effort and "
                "untested on 1.x; documents may degrade to known_missing.\n")
            missing = [m for m in missing if m != prefix + "media_file"]

        if missing:
            raise SystemExit(
                "error: required tables missing: %s\n"
                "This tool targets webtrees 2.x (PostgreSQL or MySQL)."
                % ", ".join(missing))

        found_opt = sorted(t for t in OPTIONAL_TABLES if schema.get(t))
        skipped_opt = sorted(t for t in OPTIONAL_TABLES if not schema.get(t))

        if args.list_trees:
            print("engine: %s" % engine)
            for tid, name in list_trees(db, prefix, schema):
                print("  tree %s: %s" % (tid, name))
            return 0

        ## resolve tree
        trees = list_trees(db, prefix, schema)
        if args.tree_id is not None:
            tree_id = _int(args.tree_id)
            if tree_id not in [t[0] for t in trees]:
                raise SystemExit("error: tree-id %s not found. Available: %s"
                                 % (args.tree_id,
                                    ", ".join(str(t[0]) for t in trees)))
        elif len(trees) == 1:
            tree_id = trees[0][0]
        else:
            raise SystemExit(
                "error: multiple trees present; choose one with --tree-id.\n"
                + "\n".join("  tree %s: %s" % t for t in trees))

        ## media directory
        media_dir = None
        if args.media_dir:
            media_dir = Path(args.media_dir)
        elif args.config:
            media_dir = Path(args.config).resolve().parent / "media"
        if not args.skip_media:
            if media_dir is None:
                raise SystemExit("error: --media-dir is required (could not "
                                 "derive it from --config).")
            if not media_dir.is_dir():
                raise SystemExit("error: media directory not found: %s"
                                 % media_dir)

        title = tree_title(db, prefix, schema, tree_id)

        print("engine:            %s" % engine)
        print("tree:              %s (%s)" % (tree_id, title or "untitled"))
        print("optional tables:   found: %s" % (", ".join(found_opt) or "-"))
        print("                   skipped: %s" % (", ".join(skipped_opt)
                                                  or "-"))
        if not args.skip_media:
            print("media dir:         %s" % media_dir)

        extractor = WebtreesExtractor(db, prefix, schema, media_dir, tree_id,
                                      args)
        converter = extractor.run()

        stats = converter.manifest()["stats"]
        print("\nextracted:")
        print("  " + ", ".join("%s=%s" % (k, v) for k, v in stats.items()))
        r = extractor.report
        print("  media: present=%d missing=%d unreadable=%d payload=%s"
              % (r["media_present"], r["media_missing"], r["media_unreadable"],
                 _human(r["payload_bytes"])))
        print("  places with coordinates: %d" % r["places_with_coords"])
        print("  updated_at from wt_change: %d" % r["updated_at_set"])
        print("  wt_name variants added: %d" % r["name_variants_added"])
        print("\nwebtrees-only tables:")
        for note in extractor.enrichment_notes:
            print("  - %s" % note)

        if args.dry_run:
            print("\ndry-run: no bundle written.")
            return 0

        schema_path = Path(__file__).resolve().parent.parent / \
            "schema" / "axgf-1.0.schema.json"
        bundle, concordance = converter.write_bundle(
            args.output, family_name=title,
            schema_path=str(schema_path) if schema_path.is_file() else None)

        total = Path(bundle).stat().st_size
        print("\nbundle:      %s (%s)" % (bundle, _human(total)))
        print("concordance: %s" % concordance)
        if total > 200 * 1024 * 1024:
            print("WARNING: bundle exceeds 200 MB; axgf-cms loads the whole "
                  "bundle into memory.")
        return 0
    finally:
        db.close()


def _human(n):
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unit == "GiB":
            return "%.1f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0


if __name__ == "__main__":
    sys.exit(main())
