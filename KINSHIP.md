# Reading kinship from an AXGF bundle

**Status:** informative · **Applies to:** AXGF 1.0 and 1.1 · **Changes:**
nothing in the format. Where this page says SHOULD, it is advice to readers
that want two programs to name the same relationship in the same way. It
binds no bundle and no writer.

A bundle never says "third cousin". It says who is a child of which union,
who is partnered with whom, and which Links tie people. Everything else, a
great-aunt, a sister-in-law, a half-brother, a cousin twice removed, is a
path through those facts. AXGF keeps relationships off the person (1.0 P1,
1.1 Appendix A.3), so it is the reader that finds the path and names it.

This page says how. It also says where ties of rite and custom stand:
godparents, milk kinship, the kum, the compadre and the others. They sit
beside the family and never inside it.

The reference application, [axgf-cms](https://github.com/plkarin/axgf-cms),
does what this page describes (its ADR 0020).

- [1. What a bundle states](#1-what-a-bundle-states)
- [2. Descent](#2-descent)
- [3. Marriage](#3-marriage)
- [4. Care](#4-care)
- [5. Ties of rite and custom](#5-ties-of-rite-and-custom)
- [6. Related in several ways](#6-related-in-several-ways)
- [7. When nothing has a name](#7-when-nothing-has-a-name)
- [8. Privacy](#8-privacy)
- [9. Words in every language](#9-words-in-every-language)
- [10. A worked example](#10-a-worked-example)
- [11. Edge cases](#11-edge-cases)

---

## 1. What a bundle states

| Fact | Where it is | How a reader takes it |
|---|---|---|
| A union | `Family.union.persons` (1.0 §4.2) | Every two persons of the union are partners. |
| Married or not | `union.type` (1.0 §4.2.1) | `marriage`, `religious_only` and `polygamous` give a husband, a wife, a spouse. `civil_union`, `cohabitation` and `unknown` give a partner. |
| Ended | `union.status` | `ended_by_divorce`, `ended_by_separation` and `annulled` give a former husband, a former wife, a former partner. `ended_by_death` does not: a widow is still a wife. |
| A child | `Family.children[]` | Every person of the union is a parent of every child the Family lists, in the way the child's `lineage` says (1.1 §5.13). |
| By birth | `lineage` absent, `biological` or `unknown` | Descent. An absent `lineage` is the 1.0 reading: the record says nothing else. |
| By adoption | `lineage: adoptive` | Descent, through an adoption. |
| By care | `lineage: foster`, `guardianship`, `step` | A parent's place, not descent (§4). |
| A sibling group | a Family with `children` and no `union` (1.0 §4.2.3) | The children are brothers and sisters. They meet at parents nobody recorded, and nobody is named for them. |
| A tie | a Link (1.0 §4.4) | Beside the family, never in it (§5). |

One person can be a parent of the same child through two Families: a mother,
and the mother's second union, where the child is recorded `lineage: step`.
The strongest reading wins: birth, then adoption, then foster, guardianship,
step. She is the mother.

## 2. Descent

Two people are related by descent when they share an ancestor, or when one
descends from the other. A reader climbs from each, and where the two climbs
meet, it has:

- **`up`**, the generations from A to the shared ancestors;
- **`down`**, the generations from the shared ancestors to B.

The shared ancestors are the **closest** when the two paths meet there and
nowhere below.

**Full or half.** When both paths come down from the ancestor through the
same Family, that Family's couple is shared and the relationship is full.
When they come down through two Families of the ancestor (two unions), only
that ancestor is shared, and the relationship is half: a half-brother, a
half-uncle, a half first cousin.

**Adoption** is descent, and a reader MAY say so ("adoptive sister") when a
step of the path is an adoption.

**A family that married into itself** gives two paths: cousins who married,
and their grandchildren descend from one couple twice. Both are
relationships, and a reader SHOULD give both.

The names, in English:

| `up` | `down` | B is A's |
|---|---|---|
| 1 | 0 | parent |
| 2, 3, … | 0 | grandparent, great-grandparent, … |
| 0 | 1 | child |
| 0 | 2, 3, … | grandchild, great-grandchild, … |
| 1 | 1 | brother or sister |
| 2, 3, … | 1 | uncle or aunt, great-uncle or great-aunt, … |
| 1 | 2, 3, … | nephew or niece, great-nephew or great-niece, … |
| 2 or more | 2 or more | cousin |

**Cousins.** With *k* = min(`up`, `down`) − 1 and *r* = |`up` − `down`|, B is
a *k*-th cousin *r* times removed:

| `up` | `down` | B is A's |
|---|---|---|
| 2 | 2 | first cousin |
| 3 | 3 | second cousin |
| 3 | 2 | first cousin once removed: a first cousin of A's parent |
| 2 | 3 | first cousin once removed: a child of A's first cousin |
| 4 | 2 | first cousin twice removed |

**The degree of kinship.** The civil degree counts the steps of the path:
`up` + `down`. A sibling is in the 2nd degree, an uncle in the 3rd, a first
cousin in the 4th. Canon law counted the longer side alone, max(`up`,
`down`). A reader that shows a degree SHOULD say which one it counts.

## 3. Marriage

Marriage makes in-laws. A reader names the partner first, then the
relatives on either side:

| Path | B is A's | For example |
|---|---|---|
| partner | partner | husband, wife, former wife, partner |
| partner, then the partner's relative | relative by marriage | mother-in-law (the partner's parent), brother-in-law (the partner's brother), stepson (the partner's son, not A's) |
| relative, then the relative's partner | relative's partner | daughter-in-law (a child's wife), brother-in-law (a sister's husband), stepmother (a parent's wife, not A's mother), "wife of a nephew" |
| both | relative by marriage | the husband of the partner's sister |

The partner of a partner's relative is far. A reader SHOULD name it only
when no nearer way exists.

A stepparent can be found twice: as a parent's partner, and as `lineage:
step` on the child. A reader SHOULD say what the record states (§4), once.

## 4. Care

`lineage: foster`, `guardianship` and `step` each name one generation of
care: a foster parent and a foster child, a guardian and a ward, a
stepparent and a stepchild. None is descent. A foster child's children are
not the foster parent's grandchildren by descent, and two children fostered
by one couple are not brother and sister by birth. Beyond the one generation
the record states, a reader names nothing by care. The chain of facts still
connects the people (§7).

## 5. Ties of rite and custom

A godmother ties a child to another family. Many traditions make ties of that
kind. AXGF records them as **Links**, and they never enter the family's
structure:

- **They are never descent.** The godchild of an uncle is not a cousin. A
  milk sister is not in `Family.children`, even though Islamic law forbids
  her marriage as it forbids a sister's. A *hānai* child stays a Link
  unless the family records the customary adoption as `lineage: adoptive`
  or `foster`.
- **Their kind** is in `relation` (1.1 §5.13.2): `godparent` and
  `godchild`, and `guardian`, `ward`, `mentor`, `apprentice` and `witness`
  for the ties near those words. 1.1 has no term for the others. They are
  stored as `other`, with their words in `label` and `label_reverse`.
  [Proposal 0002](./proposals/0002-ties-of-rite-and-custom.md) asks 1.2 to
  name them: milk kinship, kafala, the compadre, the kum and koumbaros, the
  sandek and kvatter, rakhi, sworn siblings, the nakōdo, the namesake,
  hānai and hunka, among others.
- **A mutual tie** (milk siblings, compadres, namesakes) is one Link with
  `bidirectional: true`.
- **A Link to a Family** (the sponsors of a marriage) ties each partner of
  its union.
- **Drawing.** A reader SHOULD draw a tie of rite apart from the family's
  lines, for instance dotted and in a colour no family line uses, so that a
  godmother never looks like a mother. It SHOULD show the source's words
  («matka chrzestna», «кума», «ndoyi») beside its own.

## 6. Related in several ways

Two people can be related in more than one way: an aunt can also be a
godmother, and a cousin can be a sister-in-law too. A reader SHOULD give
every way, the closest first.

The reference application ranks each way by the number of steps on its path
plus a weight: 0 for descent and a union, 1 for care, 2 for marriage, 3 for
a tie of rite, 4 for a chain of facts. When two ways rank the same, the
lighter weight comes first. A tie of rite is one step, so it ranks 4, as a
first cousin does. Godparents are most often aunts, uncles and grandparents,
and those rank 2 or 3: an aunt who is also a godmother is first an aunt. A
second cousin ranks 6, so a second cousin who is also a godmother is first a
godmother.

## 7. When nothing has a name

The records can connect two people with no name for the link: the godson of
a wife's father. A reader MAY then give the chain of facts, step by step:
"wife, her father, his godson". It SHOULD say that it is a chain and not
invent a word.

## 8. Privacy

Visibility (1.0 §9) decides what a reader may see. It does not decide how
two people are related:

- **The path runs through the structure** of the family, whatever the reader
  may see. If it did not, a cousin would become unrelated because a parent
  between them is private.
- **A person the reader may not see** keeps their place in the path and is
  not named: "a person you may not see". A reader SHOULD NOT offer that
  person as a choice or list them among anyone's relatives.
- **A Link the reader may not see is not followed.** For that reader, the
  tie does not exist.

## 9. Words in every language

Languages name kin with facts that English does not need. A reader SHOULD
hand those facts to its translation layer, and SHOULD NOT build kinship
words out of pieces in code:

| Fact | Where a language needs it |
|---|---|
| the sex of each person | brother and sister; *frère* and *sœur* |
| the side of the family: the sex of A's parent the line climbs through | Arabic عم (a father's brother) and خال (a mother's brother); Swahili *baba mdogo* and *mjomba*; Chinese 外 for the mother's side |
| elder or younger, from the birth dates | Chinese 哥哥 and 弟弟; 伯父 (a father's elder brother) and 叔父 (his younger brother) |
| one male line | Chinese 堂 (cousins through brothers) and 表 (the others) |
| the parent half-siblings share | Russian единокровный (the same father) and единоутробный (the same mother) |
| the sibling a nephew comes from | Polish *bratanek* (a brother's son) and *siostrzeniec* (a sister's son) |
| composition | where English says "first cousin once removed" and "second cousin once removed", French says *cousin germain du père* and *fils d'une cousine issue de germain* |

When a fact is missing (a sex not recorded, a birth date unknown), the word
SHOULD stay neutral: "parent", "sibling", or the word a language uses when
it does not know.

## 10. A worked example

A fictional family:

| Entity | What it records |
|---|---|
| Family F1 | union of Jean and Marie (`marriage`); children Pierre and Claire |
| Family F2 | union of Pierre and Sophie (`marriage`); child Luc |
| Family F3 | union of Claire and Marc (`marriage`); child Emma |
| Family F4 | union of Jean and Agnès (`marriage`); child Henri |
| Family F5 | no union; children Rose and Lily |
| Link L1 | from Claire to Luc, `relation: godparent`, `label: "marraine"`, `label_reverse: "filleul"` |

What each person is to Luc:

| B | The path | `up`, `down` | B is Luc's | Degree |
|---|---|---|---|---|
| Pierre | — | 1, 0 | father | 1 |
| Jean | Pierre | 2, 0 | grandfather | 2 |
| Claire | Pierre, then Jean and Marie (F1 on both sides) | 2, 1 | aunt, and also godmother (L1) | 3 |
| Emma | Pierre, Jean and Marie, Claire | 2, 2 | first cousin | 4 |
| Henri | Pierre, Jean (F1 on one side, F4 on the other) | 2, 1, half | half-uncle | 3 |
| Marc | Claire's partner | by marriage | husband of an aunt | — |
| Agnès | Jean's partner, not Luc's grandmother | by marriage | wife of a grandfather | — |

Rose and Lily are sisters to each other, and related to nobody else.

## 11. Edge cases

- **Sex not recorded.** The neutral word: parent, sibling, cousin.
- **Couples of one sex.** Both partners are parents of the union's children.
  The words follow each person's own sex.
- **Polygamous unions.** A union lists all its spouses in `union.persons`,
  which the schema requires. (The example in 1.0 §4.2.2 writes
  `primary_person_id` and `unions[]`, which the schema does not define.)
  One Family cannot say which wife bore which child, nor that two co-wives
  are not married to each other. When the mother of each child is known,
  one Family per couple lets every reader find the half-siblings and the
  marriages.
- **A sibling group beside the family with the parents.** An import often
  keeps both: the same children in a Family with a union and in a sibling
  group. A reader SHOULD give the way through the recorded parents once,
  and take from the group only the children it alone holds.
- **People the bundle does not hold.** A partial bundle (1.0 §2.2) can name
  a person in a Family without carrying them. They keep their place in a
  path, unnamed, as in §8.
- **Inconsistent data.** A bundle can make someone their own ancestor. A
  reader SHOULD bound its climb and never loop. The reference application
  stops at 24 generations.
