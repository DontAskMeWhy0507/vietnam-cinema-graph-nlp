# E2E Test Infra: Vietnamese Cinema & Theatre Knowledge Graph

## Test Philosophy
- Requirement-driven, opaque-box testing derived directly from `ORIGINAL_REQUEST.md`.
- No reliance on internal module assumptions: test against output datasets (`data/vietnam_cinema_nodes.csv`, `data/vietnam_cinema_edges.csv`), Cypher script (`data/import_neo4j.cypher`), analytics outputs, precision verification harness, and report deliverables (`reports/BAO_CAO_BAI_TAP_LON_SNA.md`, `reports/BAO_CAO_BAI_TAP_LON_SNA.pdf`).
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

---

## Feature Inventory & Test Mapping
| # | Feature | Source | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Cross-Feature) | Tier 4 (Application) |
|---|---------|--------|:----------------:|:-----------------:|:----------------------:|:--------------------:|
| F1 | Node Scale & Typed Classification | R1 / Acceptance | 5 | 5 | ✓ | ✓ |
| F2 | Edge Scale & 10 Relation Types | R1 / Acceptance | 5 | 5 | ✓ | ✓ |
| F3 | Source Text Evidence Provenance | R1 / Acceptance | 5 | 5 | ✓ | ✓ |
| F4 | NLP Precision against Wikipedia Text | Acceptance | 5 | 5 | ✓ | ✓ |
| F5 | Neo4j Cypher Script Syntax & Constraints | R2 / Acceptance | 5 | 5 | ✓ | ✓ |
| F6 | Neo4j Python Loader Script & Guide | R2 / Acceptance | 5 | 5 | ✓ | ✓ |
| F7 | SNA Centrality (Degree, Betweenness, Closeness, PageRank) | R2 | 5 | 5 | ✓ | ✓ |
| F8 | SNA Community Detection (Louvain Modularity) | R2 | 5 | 5 | ✓ | ✓ |
| F9 | Academic Markdown Report (>= 10 pages, 7 sections) | R3 / Acceptance | 5 | 5 | ✓ | ✓ |
| F10 | Academic PDF Report (>= 10 pages, charts, visual polish) | R3 / Acceptance | 5 | 5 | ✓ | ✓ |

---

## Test Architecture
- **E2E Test Runner**: `pytest tests/test_e2e_acceptance.py -v`
- **Verification Harness**: `python tests/verify_precision.py`
- **Unit Test Runner**: `pytest tests/ -v`
- **Pass/Fail Semantics**:
  - Exit code 0 indicates 100% pass across all assertions.
  - Precision verification must assert $\ge 90.0\%$ overall accuracy on a stratified 300-edge sample.
  - Cypher validator must assert 0 corrupted lines and 100% valid statement syntax.
  - Report validator must assert Markdown line count corresponds to $\ge 10$ pages and PDF page count $\ge 10$ with valid text layers and charts.

---

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full Knowledge Graph Ingestion in Neo4j | F1, F2, F5, F6 | High |
| 2 | Key Influencer Identification via Multi-Centrality (PageRank vs Betweenness vs Closeness) | F1, F2, F7 | High |
| 3 | Cinema vs Theatre Artistic Cluster Discovery via Louvain | F1, F2, F8 | High |
| 4 | End-to-End Precision Audit on Controversial / Complex Relationships (Mentorship & Founding) | F2, F3, F4 | High |
| 5 | Publication-Ready Academic Dossier Generation (Markdown + PDF) | F7, F8, F9, F10 | Medium |

---

## Coverage Thresholds
- Tier 1: $\ge 50$ test cases (5 per feature across 10 features).
- Tier 2: $\ge 50$ boundary and negative test cases.
- Tier 3: $\ge 10$ cross-feature integration test cases.
- Tier 4: 5 realistic application-level scenarios.
- **Target Total: $\ge 115$ automated assertions / test checks**.
