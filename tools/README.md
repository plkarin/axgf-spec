# AXGF conversion tools

Command-line converters that turn genealogy data into an **AXGF 1.0** bundle
(a `.axgf` ZIP archive validated by `axgf validate`).

| Tool | Input | Recovers media bytes? | Needs |
| --- | --- | --- | --- |
| `gedcom2axgf.py` | one or more GEDCOM 5.5.1 files | no (documents stay `referenced`) | just the `.ged` file(s) |
| `webtrees2axgf.py` | a live webtrees database + media dir | **yes** (documents become `present`) | DB credentials + read access to the media directory |

Both emit the same bundle layout and a `*.concordance.json` mapping original
cross-references to AXGF UUIDs. `gedcom2axgf.py` is the reusable engine:
`webtrees2axgf.py` imports it, so its parser, date handling and bundle writer
are shared rather than duplicated.

> Deduplicating a converted bundle — the same person or couple entered twice —
> is `axgf dedup` in the reference library ([`axgf-rs`](https://crates.io/crates/axgf-rs)),
> not a script here.

---

## Which tool should I use?

* **No shell access to the server** (only a GEDCOM export)? Use
  `gedcom2axgf.py`. Every document keeps its filename but has **no payload**
  (`status: "referenced"`) — GEDCOM's `OBJE` tag carries a filename, never the
  file.
* **Shell / database + filesystem access to the webtrees host**? Use
  `webtrees2axgf.py`. It reads the installation directly and embeds the actual
  media **bytes** (`status: "present"`, with `size_bytes` and `sha256`),
  producing a genuinely self-contained bundle. It also recovers metadata a
  GEDCOM export drops: place coordinates, last-modified timestamps and indexed
  name variants.

That trade-off is exactly why both tools exist.

---

## `gedcom2axgf.py`

```
python3 gedcom2axgf.py tree.ged -o family.axgf --schema ../schema/axgf-1.0.schema.json
```

Handles multiple input files, Polish/French/German date qualifiers
(`PRZED`, `OK`, `PO`, `MIĘDZY … I …`), partial dates, `CONC`/`CONT`
continuations, `NOTE` cross-references, `PEDI` adoption, multiple `NAME`
entries and encoding detection.

---

## `webtrees2axgf.py`

```
# primary interface — reads everything (incl. engine + password) from the
# webtrees config file, so no password is ever typed:
python3 webtrees2axgf.py --config /var/www/webtrees/data/config.ini.php \
                         --tree-id 2 -o family.axgf

# list the trees in the database and exit
python3 webtrees2axgf.py --config .../config.ini.php --list-trees

# explicit connection (password always via an env var, never on the CLI):
WT_PW=secret python3 webtrees2axgf.py \
    --db-type postgres --db-host localhost --db-port 5432 \
    --db-name webtrees --db-user wtuser --db-password-env WT_PW \
    --media-dir /var/www/webtrees/data/media --tree-id 2 -o family.axgf
```

Useful flags: `--skip-media` (structure only, documents left `referenced`,
no disk access — a fast dry run), `--dry-run` (report what would be extracted,
write nothing), `--default-confidence` (default `0.8`), `--lang` (BCP 47 tag
for place names, default `en`).

### Credentials

The tool **refuses to run with a default password.** It reads credentials, in
order of precedence, from:

1. `--db-password-env NAME` — the name of an environment variable holding the
   password (never pass the password itself on the command line);
2. the `dbpass` line in the `--config` file;
3. the `WEBTREES_DB_PASSWORD` environment variable.

No password is ever written to the script, this repository, or the produced
bundle. If `--media-dir` is omitted it is derived from the config path
(`<config-dir>/media`).

### Access requirements

`webtrees2axgf.py` needs **database credentials** and **filesystem read access
to the media directory** — both the operator's responsibility. Run it on the
webtrees host, or over an SSH tunnel to the database with the media directory
mounted (e.g. `sshfs`). Users without that access should fall back to
`gedcom2axgf.py` and accept media as `status: "referenced"`.

### Safety

* Database access is **read-only and asserted in code**: the connection is
  opened `autocommit` and read-only (`SET default_transaction_read_only`
  / `SET SESSION TRANSACTION READ ONLY`), and every query is routed through a
  guard that refuses any statement that is not a `SELECT`.
* The tool never writes to the webtrees installation or its media directory.
* An unreadable media file (permissions) becomes `known_missing` with a
  warning — never a crash. A missing file is likewise `known_missing`: a
  documented gap is genealogical information and is never silently dropped.
* Media files are streamed one at a time, so a large media set never sits
  wholly in memory. The final bundle size is reported, with a warning above
  200 MB (axgf-cms loads the whole bundle into memory).

### Database engine — detected silently

webtrees runs on PostgreSQL or MySQL/MariaDB. The engine is resolved without
the user ever stating it:

1. the `dbtype` key in `config.ini.php` (`pgsql` → PostgreSQL, `mysql` →
   MySQL), else
2. inferred from the port (`5432` → PostgreSQL, `3306` → MySQL), else
3. both engines are tried and whichever connects is used.

`--db-type` overrides detection for a broken config but is never required. The
resolved engine is reported once in the summary. The matching driver
(`psycopg2`/`psycopg` for PostgreSQL, `PyMySQL` for MySQL) is imported **lazily,
only for the selected engine**; if it is missing, the exact `pip install`
command is printed instead of a traceback. Every query is portable SQL that
runs unmodified on both engines.

### webtrees version support

Written against **webtrees 2.2.4**. A startup schema check queries
`information_schema` and reports which optional tables were found and which
were skipped.

* **Required tables** (`wt_individuals`, `wt_families`, `wt_media`,
  `wt_media_file`, `wt_link`, with the configured prefix): a missing one aborts
  with a message naming exactly what is absent.
* **Optional tables** (`wt_places`, `wt_placelinks`, `wt_place_location`,
  `wt_name`, `wt_dates`, `wt_change`, `wt_other`, `wt_sources`, `wt_gedcom`):
  absence or column drift logs a warning and the enrichment is skipped — never
  an abort. Columns are read defensively.
* **webtrees 1.x**: detected by the absence of `wt_media_file` alongside the
  presence of `wt_media`; media references are then parsed out of `m_gedcom`
  instead of the table. This path is **best-effort and untested against a real
  1.x installation**; files it cannot resolve degrade to `known_missing`.

---

## What direct extraction recovers — comparison

Same family, two paths. GEDCOM baseline produced with the installed CLI
(`axgf convert-gedcom tree.ged`); webtrees bundle produced by
`webtrees2axgf.py` against a webtrees 2.x database loaded from the same family.
Both bundles pass `axgf validate` with **0 errors, 0 warnings**.

| Metric | `axgf convert-gedcom` (GEDCOM) | `webtrees2axgf` (direct) |
| --- | ---: | ---: |
| persons | 767 | 767 |
| families | 294 | 294 |
| sources | 1 | 1 |
| places | 114 | 115 |
| documents | 400 | 400 |
| &nbsp;&nbsp;· `present` (bytes embedded) | **0** | **393** |
| &nbsp;&nbsp;· `referenced` (name only) | 400 | 0 |
| &nbsp;&nbsp;· `known_missing` (documented gap) | 0 | 7 |
| media payload embedded | 0 B | ~44 KiB* |
| places with coordinates | **0** | **8** |
| `updated_at` from change log | 0 | 767 |
| indexed name variants added | 0 | 95 |
| bundle size | 640 KiB | 891 KiB* |

\* Payload/size reflect the test fixture's small placeholder image files; a
real installation embeds the full-resolution originals.

The genealogy core is identical (running `gedcom2axgf.py` — the same parser —
on the GEDCOM yields the very same 767 / 294 / 121 events / 87 occupations /
115 places), so the entire difference is what direct extraction adds: **real
media bytes, place coordinates, change timestamps and indexed name variants.**
That is the tool's whole justification.

### Why the database row counts differ from the GEDCOM export

At extraction time the database holds **866 individuals, 332 families, 407
media**, while the GEDCOM export of the family is **767 / 294 / 400**. The
difference is **multiple trees in one installation**: `wt_individuals`,
`wt_families` and `wt_media` carry rows for every tree, keyed by
`i_file` / `f_file` / `m_file`. Scoping to the target tree (`--tree-id`, here
tree 2) yields exactly the export's numbers; the remaining rows belong to a
second tree. Scoping to one tree is therefore mandatory, which is why the tool
resolves `--tree-id` before reading anything and refuses to guess when more
than one tree is present. (Privacy filtering at export time and records merged
by deduplication are the other usual suspects, but here the counts reconcile
completely on tree scope alone.)

---

## Engine test status

* **PostgreSQL** — exercised end-to-end.
* **MySQL / MariaDB** — exercised end-to-end against MariaDB 11; produces a
  byte-for-byte equivalent bundle that passes `axgf validate` (0/0).
