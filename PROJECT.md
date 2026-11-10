# Project: Vietnamese Cinema & Theatre Knowledge Graph

## Architecture
A three-tier knowledge graph engineering and social network analysis system:
1. **Extraction & NLP Pipeline (`src/cinema_extractor.py`, `src/crawl_vietnam_cinema.py`)**:
   - MediaWiki API crawler traversing 15 seed categories and 180 child categories across Vietnamese cinema and theatre.
   - Dual extraction engine: Infobox structured parsing (movies, persons, organizations) + Career/Biography OpenIE sentence-level pattern extraction.
   - Entity disambiguation and linking against domain catalog.
2. **Data Storage & Network Modeling (`src/cinema_models.py`, `data/`)**:
   - Typed entity models (`Person`, `Artwork`, `Organization`) with rich metadata.
   - 10 semantic relationship types with source text evidence provenance.
   - Dual export targets: CSV datasets (`vietnam_cinema_nodes.csv`, `vietnam_cinema_edges.csv`) and Cypher database ingestion script (`data/import_neo4j.cypher`) + Python Neo4j batch loader (`src/load_to_neo4j.py`).
3. **Analytics & Academic Reporting (`src/analyze_cinema_graph.py`, `src/generate_cinema_report_pdf.py`, `reports/`)**:
   - Graph topological metrics: density, reciprocity, components (WCC/SCC), degree distributions (log-log power-law fit).
   - Centrality measures: Degree, PageRank, HITS, Betweenness, Closeness.
   - Algorithmic community detection: Louvain modularity optimization.
   - Publication-grade academic reporting: >= 10-page Markdown report and 11-page full-color PDF with vector visualizations.

---

## Code Layout
```
f:\Wiki\
├── data\                                # Graph datasets and database scripts
│   ├── import_neo4j.cypher              # Neo4j Cypher ingestion script (sanitized, valid syntax)
│   ├── vietnam_cinema_edges.csv         # >= 5,000 (currently 18,122) directed edges with evidence
│   └── vietnam_cinema_nodes.csv         # >= 2,000 (currently 3,037) nodes with metadata
├── reports\                             # Academic deliverables
│   ├── BAO_CAO_BAI_TAP_LON_SNA.md       # >= 10-page Markdown academic report (7 required sections)
│   └── BAO_CAO_BAI_TAP_LON_SNA.pdf      # 11-page publication-quality PDF report with vector charts
├── src\                                 # Core source code
│   ├── analyze_cinema_graph.py          # SNA analytics (Degree, Betweenness, Closeness, PageRank, Louvain)
│   ├── cinema_extractor.py              # NLP extraction (infobox parsing, text regex, entity linking)
│   ├── cinema_models.py                 # Graph models, sanitizers, CSV & Cypher exporters
│   ├── crawl_vietnam_cinema.py          # Wikipedia crawler & knowledge graph builder
│   ├── generate_cinema_report_pdf.py    # 11-page PDF vector report compiler
│   └── load_to_neo4j.py                 # Neo4j Python batch loader with reproducible instructions
├── tests\                               # Test suite & verification harnesses
│   ├── test_cinema_extractor.py         # Unit tests for infobox & OpenIE text extraction
│   ├── test_cinema_models.py            # Unit tests for graph models, sanitization & export
│   ├── test_sna_metrics.py              # Unit tests for SNA centrality & community detection
│   └── verify_precision.py              # Independent precision verification against Wikipedia text
├── vietnam_cinema_articles_cache.json   # 38.4 MB cache of 2,253 crawled Wikipedia articles
├── requirements.txt                     # Python dependencies
└── README.md                            # Setup guide, Neo4j instructions, execution guide
```

---

## Feature Inventory
Every feature identified during Survey mapped to an implementation or verification milestone:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | NLP Entity Linking Precision | Tighten regex & filter candidate mentors to Person entities only; prevent artwork/committee false positives | M1 | Survey (Explorer 1 & 2) |
| 2 | Metadata Cleaning & Sanitization | Clean `roles` (remove wiki templates), extract missing artwork years, remove wiki markup from evidence | M1 | Survey (Explorer 1 & 2) |
| 3 | Entity Label Integrity Fix | Revert 5 misclassified movies (`Bên trong vỏ kén vàng`, etc.) back to `Artwork` and fix override logic | M1 | Survey (Explorer 2 & 3) |
| 4 | Cypher Syntax Sanitization | Eliminate 105 corrupted lines in `import_neo4j.cypher`; ensure clean single-line Cypher statements | M2 | Survey (Explorer 3) |
| 5 | Python Neo4j Driver Loader | Create `src/load_to_neo4j.py` for batch insertion via `neo4j` Python driver, with Docker & setup guide | M2 | Survey (Explorer 3) |
| 6 | Full SNA Centrality Suite | Implement Betweenness and Closeness Centrality in `src/analyze_cinema_graph.py` | M2 | Survey (Explorer 3) |
| 7 | Algorithmic Community Detection | Implement Louvain modularity algorithm; compute modularity $Q$ and true community partition | M2 | Survey (Explorer 3) |
| 8 | Academic Markdown Report Expansion | Expand `BAO_CAO_BAI_TAP_LON_SNA.md` to $\ge 10$ pages ($\ge 700$ lines) covering all 7 mandatory sections | M3 | Survey (Explorer 3) |
| 9 | PDF Report Synchronization | Update `src/generate_cinema_report_pdf.py` with real Betweenness, Closeness, Louvain, and verified precision | M3 | Survey (Explorer 3) |
| 10 | Independent Precision Verification | Create `tests/verify_precision.py` to evaluate representative sample ($N=300$) against cached wikitext ($\ge 90\%$) | M4 (Final / E2E) | Survey (Explorer 1, 2, 3) |
| 11 | Comprehensive Unit Tests | Test NLP extraction, graph models, Cypher sanitization, SNA centrality, and Louvain partitioning | M4 (Final / E2E) | Survey (Explorer 1 & 3) |
| 12 | Environment & Package Config | Create `requirements.txt` with all dependencies (`neo4j`, `networkx`, `python-louvain`, etc.) | M2 | Survey (Explorer 1 & 3) |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | NLP Extraction & Data Cleaning | Fix `cinema_extractor.py`, `crawl_vietnam_cinema.py`; fix label mutations, sanitize `nodes.csv` and `edges.csv` | none | DONE |
| M2 | Neo4j Integration & Full SNA Analytics | Fix Cypher generation in `cinema_models.py`, generate clean `import_neo4j.cypher`, create `load_to_neo4j.py`, add Betweenness/Closeness/Louvain in `analyze_cinema_graph.py`, add `requirements.txt` | M1 | DONE |
| M3 | Academic Reporting (Markdown & PDF) | Expand `BAO_CAO_BAI_TAP_LON_SNA.md` to $\ge 10$ pages with 7 sections; synchronize `generate_cinema_report_pdf.py` and compile 11-page PDF | M2 | DONE |
| M4 | E2E Testing, Precision Verification & Hardening | Opaque-box E2E testing, run independent precision verification on representative sample ($\ge 90\%$), audit full compliance | M1, M2, M3 | PLANNED |

---

## Interface Contracts

### M1 ↔ M2 (Data Engine ↔ Database & Analytics)
- `data/vietnam_cinema_nodes.csv`:
  - Columns: `id,name,label,roles,type,year,in_degree,out_degree` (UTF-8-SIG).
  - Constraints: `label` $\in$ `{"Person", "Artwork", "Organization"}`. `roles` sanitized plain text without raw wikitext `{{...}}` or `[[...]]`.
  - Node count: $\ge 2,000$ (expected ~3,037).
- `data/vietnam_cinema_edges.csv`:
  - Columns: `source_id,source_name,target_id,target_name,rel_type,evidence` (UTF-8-SIG).
  - Constraints: `rel_type` $\in$ 10 specific relation types. `evidence` non-empty plain string without `<ref>` tags.
  - Edge count: $\ge 5,000$ (expected ~18,100+).

### M2 ↔ M3 (Analytics ↔ Academic Report)
- `src/analyze_cinema_graph.py`:
  - Output metrics dictionary / JSON containing:
    - Global: $N$, $E$, $\rho$ (density), reciprocity, $\bar{k}$ (average degree), WCC count & giant component ratio, SCC count & giant component ratio.
    - Centrality Top-10: In-degree, Out-degree, PageRank, Betweenness, Closeness, HITS Hub/Auth.
    - Community: Louvain modularity score $Q$, cluster count, size of top 4 clusters, dominant artist/director hubs per cluster.
- `src/generate_cinema_report_pdf.py` and `reports/BAO_CAO_BAI_TAP_LON_SNA.md`:
  - Ingest true computed metrics from `analyze_cinema_graph.py` and verified precision from `tests/verify_precision.py`.

### M1/M2/M3 ↔ M4 (System ↔ E2E Verification)
- Verification script `tests/verify_precision.py`:
  - Input: `data/vietnam_cinema_edges.csv`, `vietnam_cinema_articles_cache.json`.
  - Stratified sample: 300 edges (Infobox: 180, Inferred: 80, OpenIE: 40).
  - Output: Exit code 0 if overall precision $\ge 90.0\%$, formatted table of per-relation precision printed and saved to `reports/precision_evaluation.json`.
- Test runner:
  - `pytest tests/ -v` passes 100%.
