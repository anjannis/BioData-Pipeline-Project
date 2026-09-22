# BioData Pipeline — Project Plan
**Jannis Angetter · B.Sc. AI, FAU Erlangen-Nürnberg · Semester 2**

---

## Context for Claude

This document is a project brief for Jannis, a second-semester B.Sc. AI student at FAU Erlangen-Nürnberg. He is currently taking:
- **Data Engineering** — covering SQL (DDL/DML, joins, normalization, relational algebra) and graph databases (Neo4j)
- **Applied Programming** — Python, NumPy, pandas, applied data science
- **Introduction to Molecular Biology** — gene expression, DNA/RNA, proteins (application domain)

His Python level is "fairly confident" — no need to explain basic syntax, loops, or classes. He knows SQL through BCNF normalization and is actively learning Neo4j. He prefers to attempt things himself first and receive targeted feedback rather than full solutions handed to him.

---

## Project Overview

**Name:** BioData Pipeline  
**Tagline:** An end-to-end data engineering pipeline over public biological databases, combining relational SQL storage, Python data processing, and a Neo4j graph layer.  
**CV description (target):** *"Built an end-to-end bioinformatics data pipeline: ingested and cleaned public gene expression and protein interaction data with Python/pandas, modelled it in a normalized PostgreSQL/SQLite schema, and represented protein interaction networks as a graph database in Neo4j — queried for hub proteins and interaction clusters."*

**Estimated time:** 4–6 weeks at ~5 hours/week alongside coursework  
**Language:** Python 3.11+  
**Version control:** Git + GitHub (public repo, clean README)

---

## Learning Goals

This project is designed to directly reinforce and extend current coursework:

| Skill | Course connection | How this project covers it |
|---|---|---|
| SQL schema design & normalization | Data Engineering | Designing the relational schema from scratch |
| Python data processing | Applied Programming | pandas/NumPy pipeline for cleaning & transforming |
| Graph databases (Neo4j) | Data Engineering | Modelling protein interactions as a property graph |
| Cypher query language | Data Engineering | Writing queries to find hub proteins, paths, clusters |
| Biological data formats | Molecular Biology | Working with real gene/protein data (FASTA, TSV) |
| Git workflow | Applied Programming | Structured commits, branches, README documentation |

---

## Datasets (Free & No Account Required)

### Module 1 — Protein Interaction Network (main module)
**Source:** [STRING Database](https://string-db.org/cgi/download)  
**What it is:** A database of known and predicted protein-protein interactions. Each interaction has a confidence score.  
**Files to download:**
- `9606.protein.links.v12.0.txt.gz` — human protein interactions (~12 MB compressed)
- `9606.protein.info.v12.0.txt.gz` — protein names and metadata

**Why this is good:** Protein interactions are *naturally* a graph. Each protein is a node; each interaction is an edge with a weight (confidence score). This makes the Neo4j layer feel motivated, not forced.

### Module 2 — Gene Expression Data (extension module)
**Source:** [NCBI Gene Expression Omnibus (GEO)](https://www.ncbi.nlm.nih.gov/geo/)  
**Suggested dataset:** GSE2034 — breast cancer gene expression (~200 samples, ~22k genes)  
**Download:** Use `GEOparse` Python library or direct FTP download  
**What it is:** A matrix of gene expression levels across samples. Rows = genes, columns = samples/conditions.

Start with Module 1. Add Module 2 only if time allows.

---

## Project Structure

```
biodata-pipeline/
│
├── README.md                  # Project overview, setup, how to run
├── requirements.txt           # Python dependencies
├── .gitignore
│
├── data/
│   ├── raw/                   # Downloaded raw files (gitignored if large)
│   └── processed/             # Cleaned CSV outputs
│
├── notebooks/
│   └── 01_exploration.ipynb   # Initial data exploration
│
├── src/
│   ├── ingest.py              # Download / load raw data
│   ├── clean.py               # pandas cleaning & transformation
│   ├── db_sql.py              # SQLite schema creation & data loading
│   ├── db_neo4j.py            # Neo4j connection & graph loading
│   └── queries.py             # Analysis queries (SQL + Cypher)
│
├── schema/
│   └── schema.sql             # DDL for the relational schema
│
└── results/
    └── findings.md            # Summary of query results / insights
```

---

## Phase Plan

### Phase 1 — Setup & Exploration (Week 1)
**Goal:** Environment ready, data downloaded, first look at the data.

Tasks:
- [ ] Create GitHub repo, add `.gitignore`, initial `README.md`
- [ ] Set up virtual environment (`uv` or `venv`), `requirements.txt`
- [ ] Download STRING protein links and info files
- [ ] Write `ingest.py`: load the `.txt.gz` files into pandas DataFrames
- [ ] Explore the data in a Jupyter notebook: shape, dtypes, nulls, value distributions
- [ ] Answer: What does one row represent? What are the score columns?

**Deliverable:** A notebook showing the raw data loaded and described.

---

### Phase 2 — Cleaning & Transformation (Week 2)
**Goal:** Clean, filtered data ready for storage.

Tasks:
- [ ] Write `clean.py` with the following steps:
  - Filter interactions to only high-confidence ones (combined score ≥ 700 is a common threshold)
  - Normalize protein identifiers (STRING uses Ensembl IDs like `9606.ENSP00000...` — strip the prefix)
  - Join interaction table with protein info table to add human-readable names
  - Handle missing values and duplicates
  - Output cleaned CSVs to `data/processed/`
- [ ] Use NumPy for any numerical transformations (e.g. normalizing scores to 0–1 range)

**Key question to answer:** After filtering to score ≥ 700, how many interactions remain? How many unique proteins?

---

### Phase 3 — Relational Database (Week 3)
**Goal:** Data stored in a normalized SQLite schema.

**Schema design (design this yourself first, then validate):**

Think about what entities you have and how they relate:
- A **Protein** has an ID, a name, and optionally an annotation
- An **Interaction** links two proteins and has a confidence score
- (Optional) A **Dataset** table recording where data came from and when it was loaded

Normalization checklist:
- Is the schema in 3NF? Are there any transitive dependencies?
- Is the interaction table a proper junction/association table?
- Are foreign key constraints defined?

Tasks:
- [ ] Write `schema/schema.sql` with `CREATE TABLE` statements
- [ ] Write `db_sql.py`:
  - Connect to SQLite (`sqlite3` module)
  - Create tables from schema
  - Load cleaned DataFrames into tables with `pandas.DataFrame.to_sql()`
  - Write 3–5 SQL queries answering biological questions (see query ideas below)

**SQL query ideas:**
```sql
-- How many interactions does each protein have? (degree)
SELECT protein_name, COUNT(*) AS degree
FROM interactions
JOIN proteins ON interactions.protein_a = proteins.protein_id
GROUP BY protein_name
ORDER BY degree DESC
LIMIT 20;

-- Which pairs of proteins have the highest confidence score?
SELECT p1.protein_name, p2.protein_name, i.combined_score
FROM interactions i
JOIN proteins p1 ON i.protein_a = p1.protein_id
JOIN proteins p2 ON i.protein_b = p2.protein_id
ORDER BY combined_score DESC
LIMIT 10;
```

**Deliverable:** A working SQLite database file, schema SQL file, query results in `findings.md`.

---

### Phase 4 — Graph Database with Neo4j (Week 4)
**Goal:** Same data modelled as a property graph in Neo4j, queried with Cypher.

**Graph model:**
```
(:Protein {id, name}) -[:INTERACTS_WITH {score}]-> (:Protein {id, name})
```

Each protein is a **Node** with label `Protein`.  
Each interaction is a **Relationship** with type `INTERACTS_WITH` and a `score` property.  
Since interactions are undirected biologically, create relationships in both directions or use undirected queries in Cypher.

**Setup:**
- Run Neo4j locally via Docker: `docker run -p 7474:7474 -p 7687:7687 neo4j`
- Or use [Neo4j AuraDB free tier](https://neo4j.com/cloud/platform/aura-graph-database/) (cloud, no Docker needed)
- Python driver: `pip install neo4j`

Tasks:
- [ ] Write `db_neo4j.py`:
  - Connect to Neo4j with the Python driver
  - Create `Protein` nodes from the proteins DataFrame
  - Create `INTERACTS_WITH` relationships from the interactions DataFrame
  - Use `UNWIND` in Cypher for batch inserts (much faster than one-by-one)
- [ ] Write Cypher queries (see below)

**Cypher query ideas:**
```cypher
// Find the top 10 most connected proteins (hub proteins)
MATCH (p:Protein)-[:INTERACTS_WITH]->()
RETURN p.name, COUNT(*) AS degree
ORDER BY degree DESC
LIMIT 10;

// Find all proteins interacting with TP53 (a well-known cancer gene)
MATCH (p:Protein {name: "TP53"})-[:INTERACTS_WITH]-(neighbor)
RETURN neighbor.name, neighbor.id;

// Find shortest path between two proteins
MATCH path = shortestPath(
  (p1:Protein {name: "TP53"})-[:INTERACTS_WITH*]-(p2:Protein {name: "BRCA1"})
)
RETURN path;

// Find proteins that are mutual interaction partners (triangles)
MATCH (a:Protein)-[:INTERACTS_WITH]-(b:Protein)-[:INTERACTS_WITH]-(c:Protein)-[:INTERACTS_WITH]-(a)
RETURN a.name, b.name, c.name
LIMIT 10;
```

**Deliverable:** Neo4j graph loaded, Cypher queries running, results documented.

---

### Phase 5 — Documentation & Polish (Week 5–6)
**Goal:** Project is presentable on GitHub and on a CV.

Tasks:
- [ ] Write a proper `README.md` covering:
  - What the project does and why (1 paragraph)
  - Tech stack (Python, pandas, NumPy, SQLite, Neo4j)
  - How to set up and run it (step by step)
  - Key findings / what you discovered
  - Schema diagram (even a simple ASCII one)
- [ ] Add docstrings to all functions in `src/`
- [ ] Make sure all commits are clean and descriptive
- [ ] (Optional) Add a simple visualization: NetworkX + matplotlib to plot a subgraph of the top 50 most connected proteins

---

## Technology Stack

| Tool | Purpose | Notes |
|---|---|---|
| Python 3.11+ | Core language | — |
| pandas | Data loading, cleaning, transformation | Already familiar |
| NumPy | Numerical operations, score normalization | Already familiar |
| SQLite (via `sqlite3`) | Relational database storage | Lightweight, no server needed |
| Neo4j | Graph database | Run via Docker or AuraDB free tier |
| `neo4j` (Python driver) | Connect Python to Neo4j | `pip install neo4j` |
| Jupyter | Exploration notebook | Optional but useful |
| Git + GitHub | Version control | Public repo for CV |
| `requests` or `GEOparse` | (Module 2 only) Fetch GEO data | Only if extending |
| Streamlit | (Phase 6 only) Web UI | `pip install streamlit` |
| pyvis | (Phase 6 only) Interactive graph visualization | Used inside Streamlit |

---

## Key Biological Concepts to Understand

These are things you'll encounter in the data and should be able to explain:

- **Protein-protein interactions (PPI):** Proteins rarely act alone — they form complexes and signalling networks. The STRING database captures these.
- **Hub proteins:** Proteins with many interactions. Often essential — removing them breaks the network. TP53 is a classic example (it's called the "guardian of the genome").
- **Confidence score:** STRING assigns scores based on evidence type (experimental, co-expression, literature). A combined score ≥ 700 is considered high-confidence.
- **Ensemble protein IDs (ENSP...):** The identifier system STRING uses. You'll need to strip the organism prefix (9606 = Homo sapiens).

Your Molecular Biology course will give you more context as the semester progresses — this project and the course will reinforce each other.

---

## Checkpoints & Self-Assessment Questions

After each phase, ask yourself:

**After Phase 1:**
- Can I describe what each column in the raw data means?
- Do I understand why the data needs cleaning before storing it?

**After Phase 2:**
- Why did I choose score ≥ 700 as a threshold? What would change at 400 or 900?
- Are there any proteins that appear in the interaction table but not in the info table? Why?

**After Phase 3:**
- Is my schema in 3NF? Could I explain why to an examiner?
- What would a JOIN look like to answer a biological question?

**After Phase 4:**
- What can the graph model express that the relational model cannot easily express?
- What is a hub protein, and can I find one with a Cypher query?

**After Phase 5:**
- Could a classmate clone this repo and run it from scratch using only the README?
- What would I add if I had another two weeks?

---

---

## Phase 6 — (Optional) Streamlit Web UI

**Goal:** A simple interactive web interface to query and visualize the pipeline data — something you can actually demo to someone.

**When to add this:** Only after Phases 1–5 are complete and the pipeline is solid. Don't touch this until the data layer works end-to-end.

**Why Streamlit and not Flask/FastAPI:** Streamlit is pure Python — no HTML, no JavaScript, no frontend framework. You write Python and it renders a UI. It's the standard tool in data science and research contexts, and takes an afternoon to learn.

**Install:** `pip install streamlit pyvis`  
**Run:** `streamlit run app.py`

### What to build

A single `app.py` at the project root with three pages, navigated via a sidebar:

**Page 1 — Protein Search (SQL backend)**
- Text input: enter a protein name
- Query SQLite for all interactions involving that protein
- Display results as a table (pandas DataFrame → `st.dataframe()`)
- Show the interaction count and average confidence score

**Page 2 — Network Visualization (Neo4j backend)**
- Text input: enter a protein name
- Query Neo4j for its direct neighbors (1-hop)
- Render the subgraph using `pyvis` → export to HTML → embed with `st.components.v1.html()`
- Nodes = proteins, edges = interactions, edge thickness = confidence score

**Page 3 — Statistics Dashboard**
- Top 20 hub proteins (bar chart via `st.bar_chart()`)
- Confidence score distribution (histogram)
- Total counts: proteins, interactions in the database

### Minimal app.py structure

```python
import streamlit as st
import sqlite3
import pandas as pd
from neo4j import GraphDatabase

st.set_page_config(page_title="BioData Pipeline", layout="wide")

page = st.sidebar.radio("Navigate", ["Protein Search", "Network View", "Statistics"])

if page == "Protein Search":
    st.title("Protein Search")
    query = st.text_input("Enter protein name (e.g. TP53)")
    if query:
        # query SQLite, display results
        ...

elif page == "Network View":
    st.title("Interaction Network")
    protein = st.text_input("Enter protein name")
    if protein:
        # query Neo4j, render pyvis graph
        ...

elif page == "Statistics":
    st.title("Database Statistics")
    # hub proteins bar chart, score histogram
    ...
```

### What this adds to your CV

The CV line becomes: *"Built an end-to-end bioinformatics data pipeline with a Streamlit web interface for interactive querying and network visualization."* The web UI turns a backend project into something demonstrable — significantly stronger in an interview or application context.

### Checkpoint questions
- Can a classmate open the app and find the interaction partners of TP53 without touching the terminal?
- Does the network visualization render correctly for proteins with 50+ neighbors?
- Is the app still fast enough when querying the full dataset?

---

## How to Use This Document in a New Chat

Paste this document (or attach it as a file) at the start of a new conversation with Claude and say something like:

> "I'm starting work on the BioData Pipeline project described in this plan. Today I want to work on [Phase X / specific task]. My preference is to attempt things myself and get targeted feedback — not full solutions upfront."

Claude will calibrate to your level and the project scope immediately.

---

*Document created: June 2026 · Update this file as the project evolves.*
