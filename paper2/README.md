# Paper 2 — CIM Wizard: Provenance-Aware Multi-Method Digital Twin

High-level structure for the second CIM Wizard paper.

| File | Purpose |
|------|---------|
| [`PAPER2-outline.md`](PAPER2-outline.md) | Outline: objectives (engineering) + **quantitative reframing (H1–H6)** + evaluation pillars |
| [`latex/main.tex`](latex/main.tex) | IEEE conference article (compile on Overleaf or local TeX) |
| [`latex/references.bib`](latex/references.bib) | Bibliography |
| [`latex/sections/`](latex/sections/) | Section files (`01-introduction` … `08-conclusion`) |
| [`latex/tables/`](latex/tables/) | Hypothesis, methodology, and results tables (T1–T7) |

**Compile locally:**

```bash
cd paper2/latex
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

Or upload `paper2/latex/` to Overleaf and set `main.tex` as the root document.

**Working title:** *Confidence-Aware Urban Building Modeling via Semi Data Warehouse, UBEM Ontology Stack, and LLM-Automated Virtual Knowledge Graph*

**North star:** Urban models are hard to validate at scale. Paper 2 assigns **confidence levels** to feature values based on **data source quality** and **calculator method agreement**, instead of presenting a single opaque number.

**Six objectives (O1–O6):**

| ID | Objective |
|----|-----------|
| O1 | Semi data warehouse (`datalake/`, STAC) |
| O2 | UBEM ontology stack (`semantic/ontop/`) |
| O3 | CIM text-to-SQL dataset (`ai4db/`) |
| O4 | Fine-tune + validate LLM (`txt2ssql/`, `assist_cim/`) |
| O5 | Multi-agent VKG / OBDA automation (LLM4VKG + fine-tuned SQL) |
| O6 | Integrate warehouse + VKG into CIM Wizard for provenance & confidence |

**Relationship to Paper 1:** Priority-based method fallback → **all methods** + provenance + confidence scoring.
