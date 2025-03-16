# Temporal Medical Record Knowledge Graphs for AI-Driven Healthcare Insights

## Project Overview

Medical records and doctor-patient transcripts contain valuable insights that can significantly improve healthcare decision-making. However, these records are often unstructured, making it difficult to extract and analyze patient history over time. Our project proposes a **Temporal Medical Record Knowledge Graph (TMKG)** that transforms doctor transcripts into structured, queryable knowledge graphs. This system enables healthcare professionals to ask complex medical questions spanning multiple patient histories and time periods, unlocking deeper insights for diagnosis, treatment, and research.

## Problem Statement

Currently, medical records exist as disparate text-based documents, making it challenging to:
- Extract meaningful relationships between patient encounters, conditions, and treatments.
- Analyze patient health trajectories over time.
- Perform efficient retrieval of relevant information for clinical decision-making.

Our solution addresses these challenges by leveraging knowledge graph techniques combined with Large Language Models (LLMs) and temporal data representations to structure and organize medical transcripts.

---

## Proposed Solution

### 1. Data Acquisition & Preprocessing
- We use the **MIMIC dataset** to ensure compliance with privacy regulations while maintaining realistic medical records.
- Transcripts are structured into JSON format using **Claude AI** for initial transformation.
- Data includes key patient attributes such as demographics, conditions, immunizations, and observations.

### 2. Knowledge Graph Construction
- **Nodes**: Represent medical entities such as Patients, Conditions, Observations, Immunizations, and Encounters.
- **Relationships (Triples)**: Define meaningful medical connections, e.g.,
  - `(Patient) -[has_condition]-> (Condition)`
  - `(Patient) -[received]-> (Immunization)`
  - `(Patient) -[had_encounter]-> (Encounter)`
  - `(Patient) -[has_measurement]-> (Observation)`
- **Temporal Data Handling**: Time-sensitive events (e.g., diagnosis dates, vaccination records) are incorporated for longitudinal patient tracking.

### 3. Graph-Based Retrieval & Analytics
- **Vector Search for Triples**: Instead of relying on complex Cypher queries, our system uses vector embeddings for efficient retrieval.
- **Chunk-Based Information Extraction**: Each relationship is linked to summarized chunks of medical data for easier interpretation.
- **Temporal Querying**: Allows users to retrieve medical insights across different time frames.

---

## Implementation Tools & Frameworks

- **Data Preprocessing**: Python (Pandas)
- **Knowledge Graph Construction**: Neo4j, GraphDB
- **Vector Search**: langchain
- **Language Model for Text Processing**: OpenAI GPT
- **Web Interface for Queries**: Streamlit / Flask
- **Frontend**: Electron.js

---

## Outcomes

- A functional prototype that converts medical transcripts into a structured temporal knowledge graph.
- A queryable interface where users can ask complex medical questions.
- Demonstration of real-world healthcare insights derived from the graph.

---

## Steps to Set Up the Project

### Prerequisites
1. **Node.js** and **npm** installed on your machine.
2. **Python 3.8+** installed.
3. **Neo4j** database set up and running.

### Installation

#### Frontend (Electron.js)
1. Clone the repository:
```
git clone 
```
2. Navigate to the project directory and install npm packages:
```
npm install
```
3. Insall python packages for AI and knowledge graph generation:
```
pip install -r requirements.txt
```

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **MIMIC Dataset** for providing realistic medical records.
- **OpenAI GPT** for text processing and transformation.
- **Neo4j** for knowledge graph construction and management.
