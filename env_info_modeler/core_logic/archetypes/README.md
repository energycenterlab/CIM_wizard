# Residential archetype reference tables (Torino / Piedmont, climate zone E)

Config, not code: the mapper in `core/archetypes.py` only reads these files,
and `app/archetype_assignment.py` decides the call order. New surveys, new
thresholds or a bigger server never touch the classes.

## Why these periods and classes

TABULA's eight periods (`_01`…`_08`) cut time at 1900/1920/1945/1960/1975/1990/2005,
which matches neither the census nor DBGT. The nine canonical periods here are the
ISTAT census ones (`E8`…`E16`, also used by the EPISCOPE Italy country page and the
URBEM PoliMI workbooks), so a census distribution can join a building directly:

| period_id | label | istat | EPISCOPE Piedmont | URBEM apartment sheets |
|---|---|---|---|---|
| P1 | before_1918 | E8 | Before 1919 | `<1930` (proxy, covers 1919-1929 too) |
| P2 | 1919_1945 | E9 | 1919 - 1945 | `1931-1940` + `1941-1950` blended |
| P3 | 1946_1960 | E10 | 1946 - 1960 | `1941-1950` + `1951-1960` blended |
| P4 | 1961_1970 | E11 | 1961 - 1970 | `1961-1970` exact |
| P5 | 1971_1980 | E12 | 1971 - 1980 | `1971-1980` exact |
| P6 | 1981_1990 | E13 | 1981 - 1990 | `1981-1990` exact |
| P7 | 1991_2000 | E14 | 1991 - 2000 | `1991-2000` exact |
| P8 | 2001_2005 | E15 | 2001 - 2005 | `2001-2010` (proxy, covers 2006-2010 too) |
| P9 | after_2005 | E16 | After 2005 | `2001-2010` + `2011-` blended |

Classes are `SFH` (one dwelling), `MFH` (2-8 dwellings) and `Apartments`
(9+ dwellings, the URBEM apartment-block scale). TABULA `TH_xx` is deliberately
unused: one-dwelling rows map to `SFH` even if terraced.

## Sources (nothing invented)

| file | source | what it carries |
|---|---|---|
| `periods.csv` | ISTAT census via `census_service.py` (E8-E16) + EPISCOPE Italy page + URBEM sheets + TABULA suffixes | canonical periods and every crosswalk |
| `building_classes.csv` | project decision 2026-09 | class definitions and assignment rules |
| `envelope_archetypes.csv` | `cim-database/tabula.csv` (Politecnico di Torino XLS, opaque U) + `cim-database/RES_APPBLOCK_E_PIE.xlsx` (EPC windows, wall/roof descriptions) | U wall/roof/ceiling/floor per period x class; window U for Apartments only |
| `systems.csv` | same URBEM workbook (EPC, Piedmont, zone E) + UNI EN 16798-1 (gains/ventilation standards) | heating/DHW/carrier shares, powers, operating times per period (Apartments) |
| `stock_weights.csv` | URBEM record counts | apartment sample sizes; EPISCOPE counts still TODO |
| `episcope_piedmont_aggregates.csv` | EPISCOPE Italy country page (ISTAT Census 2011) | region-wide heating fuel shares; the rest TODO |
| `mapping_rules.yaml` | project configuration | residential gate, precedence, thresholds, provenance |

`cim_wizard_integrated_2026/` was read for the census E-codes only. Nothing was changed there.

## How blends were computed

For a canonical period merging URBEM sheets with record counts `n`:

- share distributions: record-weighted mean of each category, renormalised to 100 %
- numeric mean `m` and std `s`: pooled mean, pooled std
  `pooled_var = sum(n * (s^2 + m^2)) / N - pooled_mean^2`
- medians and quartiles cannot be pooled, so blends leave them empty;
  single-sheet proxies (P1, P8) keep theirs

## Gaps, stated plainly

- Window `g` values: not extracted anywhere in the repo. Column stays empty;
  use the TABULA national window table or defaults, do not invent.
- SFH/MFH systems and windows: the SFH/MFH URBEM workbooks are not in the repo.
  Their rows stay empty; do not copy Apartments values across classes.
- Refurbishment shares: EPISCOPE S-1.2.1 reports them per apartment by age, not by
  class. Nothing conditioned on SFH/MFH exists, so `stock_weights.csv` leaves them
  empty instead of fabricating a conditioning.
- EPISCOPE S-1.1/S-2.1/S-2.5 tables: still to transcribe from
  `https://episcope.eu/building-typology/country/it.html`; fuel shares in
  `episcope_piedmont_aggregates.csv` are marked VERIFY before publication.
- `data_quality_flag` in `systems.csv` marks three workbook cells whose
  mean/median/quartile order is inconsistent (P4 DHW power, P5/P6 heating power).

## Answering the U-value question

For "hollow brick masonry with thermal insulation (MCV02)" with "reinforced
concrete floor slab (SOL04)": the U values do not live in the URBEM workbook
(it only records the UNI/TR 11552:2014 codes plus EPC window statistics).
Filter `envelope_archetypes.csv` by period and class and read the TABULA
construction codes, e.g. P5/Apartments gives `AB_05` with wall 1.086/1.262,
roof 2.217, ceiling 1.664, floor 1.318 W/m2K. The layer stacks behind those U
values are in `cim-database/materiale-tabula/` per the frozen extraction guide.

## Mapping a building

1. Keep residential usages (`mapping_rules.yaml`; mixed-residential counts, flagged).
2. Year (or range midpoint, or open-bound cap) into one of P1-P9.
3. Census dwelling count into SFH/MFH/Apartments; floors/height fallback only.
4. Join `(period_id, building_class)` against the envelope and systems tables.
5. Sample refurbishment/system variants only with an explicit `random_seed`,
   and only once the shares exist.
