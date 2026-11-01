# Proposal 0002 — Ties of rite and custom: naming them in `link_relation`

**Status:** proposed for AXGF 1.2 · **Changes:** adds terms to the closed
vocabulary `link_relation` (1.1 §5.13.2) and one field to Link; no 1.1
bundle stops being valid, and nothing is removed.

## The question

1.1 records a godmother as a Link with `relation: godparent`, and that is the
only tie of rite its vocabulary names. Many families hold others, and their
traditions treat them as kinship:

- a **milk mother** and **milk siblings**, which in Islamic law make a family
  and forbid marriage as birth does;
- **kafala**, the Islamic fostering of a child without the filiation an
  adoption gives;
- the **compadre**, the bond between a child's parents and the child's
  godparents (Latin America, the Philippines, the Mediterranean);
- the Slavic **kum** and the Greek **koumbaros**, wedding sponsors who are
  often godparents too;
- the **sandek** and the **kvatter** at a brit milah;
- **rakhi** siblings, the **guru** and the disciple;
- **sworn siblings**, the Japanese **nakōdo** and **name-giver**, and the
  Chinese **gān qīn** (godparents);
- the **namesake** (*ndoyi* in Lingala, *somo* in Swahili), the **initiation**
  sponsor and the **blood pact**;
- the Hawaiian **hānai** and the Lakota **hunka**;
- **civil godparenthood**.

Today a writer has two choices, and both lose the fact. It can store the
nearest term (`godparent`, `guardian`, `other`), so that every reader sees a
milk sister as "other". Or it can keep the term in vendor data, so that no
other reader sees it at all. The reference application does the second, under
`extensions["axgf-cms:kinship/v1"]` (axgf-cms ADR 0020), while waiting for
this proposal.

## The principle

**A tie a tradition names is a tie the format can name.** 1.1 §3 asks for a
closed vocabulary wherever the answers can be known in advance, so that two
implementations store the same word for the same thing. The ties above are
known in advance and are stable: each has centuries of practice behind it.
The words people use for them vary by language, and that is what `label` and
`label_reverse` are for.

A rite is not descent. A milk sister is not a sister in `Family.children`,
and a hānai child stays a Link unless the family records a customary adoption
as `lineage: adoptive` or `foster`. The format keeps a family's structure and
a tradition's ties apart, as readers expect: a reader draws the first as a
family and the second beside it. How a reader places these ties among a
person's relatives, and draws them, is in [KINSHIP.md](../KINSHIP.md) §5
and §6.

## Proposed text (1.2)

### §5.13.2 `link_relation`: new terms

The existing terms keep their meaning. These are added; "from" is the Link's
`from` end. A pair marked **mutual** is the same tie both ways, and a writer
SHOULD set `bidirectional: true`.

| Term | Meaning | Category it is stored with |
|---|---|---|
| `baptism_sponsor` | From is a godparent at the to-end's baptism. | spiritual |
| `confirmation_sponsor` | From is a sponsor at the to-end's confirmation or chrismation. | spiritual |
| `wedding_sponsor` | From sponsored the to-end's marriage (padrino de boda, ninong, koumbaros, kum). The to-end MAY be the Family of the union. | spiritual |
| `co_parent` | **Mutual.** A child's parent and the child's godparent (compadrazgo). | spiritual |
| `brit_sponsor` | From held (sandek) or carried in (kvatter) the to-end at the brit milah. | spiritual |
| `milk_parent` | From nursed the to-end, or is the nurse's husband, as Islamic law reckons milk kinship. | spiritual |
| `milk_child` | The reverse of `milk_parent`. | spiritual |
| `milk_sibling` | **Mutual.** Nursed by the same woman. | spiritual |
| `kafil` | From took in and raises the to-end under kafala. | legal |
| `makful` | The reverse of `kafil`. | legal |
| `ritual_sibling` | **Mutual.** Siblings by rite or oath: rakhi, sworn siblings, blood pact. | social |
| `spiritual_teacher` | From is the to-end's guru or spiritual teacher. | spiritual |
| `disciple` | The reverse of `spiritual_teacher`. | spiritual |
| `name_giver` | From gave the to-end their name (nazuke-oya). | social |
| `go_between` | From arranged and witnessed the to-end's marriage (nakōdo). | social |
| `namesake` | **Mutual.** People tied by bearing the same name (ndoyi, somo). | social |
| `initiation_sponsor` | From guided the to-end through an initiation. | spiritual |
| `customary_parent` | From raises or adopted the to-end by custom, outside any legal adoption (hānai, hunka). | social |
| `customary_child` | The reverse of `customary_parent`. | social |

`godparent` and `godchild` remain the general terms, for a record that does
not say at which rite.

### Link (1.0 §4.4): `tradition`

A Link MAY carry `tradition`, a closed vocabulary that says which tradition
the tie belongs to:

> `christian`, `orthodox`, `hispanic`, `jewish`, `islamic`, `south_asian`,
> `east_asian`, `african`, `indigenous`, `civil`

It is for grouping and for display. It is not a judgement on anyone's
belonging, and it is OPTIONAL.

### Words: `label` and `label_reverse`

`label` and `label_reverse` keep the words of the source: «matka chrzestna»,
«أخت من الرضاعة», «ndoyi». A reader SHOULD show them beside its own word for
the term.

## Reading a 1.1 bundle

A 1.2 reader meets 1.1 bundles that carry these ties in a writer's extension.
For the reference application's extension the mapping is:

| `axgf-cms:kinship/v1` `rite` | 1.2 term (from the sponsor's end) |
|---|---|
| `baptism`, `kum`, `koumbaros`, `padrino`, `ninong`, `gan-parent` | `baptism_sponsor` (`godparent` where the rite is not a baptism) |
| `confirmation` | `confirmation_sponsor` |
| `wedding-sponsor` | `wedding_sponsor` |
| `compadre` | `co_parent` |
| `sandek`, `kvatter` | `brit_sponsor` |
| `milk-parent` / `milk-sibling` | `milk_parent` / `milk_sibling` |
| `kafala` | `kafil` |
| `rakhi`, `sworn-sibling`, `blood-pact` | `ritual_sibling` |
| `guru` | `spiritual_teacher` |
| `name-giver` | `name_giver` |
| `nakodo` | `go_between` |
| `namesake` | `namesake` |
| `initiation` | `initiation_sponsor` |
| `hanai`, `hunka` | `customary_parent` |
| `civil-sponsor` | `godparent`, with `tradition: civil` |

## GEDCOM

GEDCOM 5.5.1 records an association as `ASSO` with a free `RELA`
("Godfather"). GEDCOM 7 adds `ROLE` with `GODP` (godparent), `WITN`
(witness) and `OTHER` with a `PHRASE`. A converter maps `GODP` and a
recognisable `RELA` to these terms, and keeps the source's words in
`label`. Every other `RELA` stays `other` with its words.

## What this does not change

- A **family's** structure: descent, unions, `lineage`. A tie of rite never
  makes a parent.
- **Visibility**: a Link keeps its own (proposal 0001).
- **1.1 bundles**: they stay valid and are read as before. A writer whose
  readers are still 1.1 tools keeps writing the 1.1 terms, with its own
  extension, until they move to 1.2.
