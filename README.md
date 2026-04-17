# FraudScale 

FraudScale is a high-performance, real-time fraud detection system designed to identify coordinated bot behavior and fraudulent activity in streaming review data. By combining **Apache Spark Structured Streaming**, **Kafka**, and **AI-based semantic embeddings**, the system moves beyond simple rule-based detection to a sophisticated, continuous fraud-scoring model.

---

## System Architecture

FraudScale utilizes a modular, containerized architecture to handle high-throughput data processing and real-time visualization.


1.  **Ingestion:** A Python-based producer simulates realistic review traffic (~1,000 events/sec) into **Apache Kafka** (KRaft mode).
2.  **Stream Processing:** **Apache Spark** consumes the stream, performing stateful windowed aggregations to extract behavioral features (review counts and rates).
3.  **AI Layer:** The system uses **SentenceTransformers (MiniLM)** and **FAISS** to generate semantic embeddings and perform intra-batch similarity searches to detect "text spinning" or coordinated content.
4.  **Scoring Engine:** A weighted, normalized scoring model aggregates signals into a final fraud probability.
5.  **Serving & Visualization:** Processed data is synced to a dual-layer storage (Parquet/JSON) and served via a **FastAPI** backend to a live **Streamlit** dashboard.

---

## Key Features

* **Continuous Fraud Scoring:** Moves away from binary "fraud/not-fraud" flags to a weighted score: 
    * `0.5 * Similarity + 0.3 * Review Rate + 0.2 * Review Count`.
* **Semantic Duplicate Detection:** Integrated **FAISS vector search** to identify semantically similar reviews in real-time.
* **Stateful Streaming:** Utilizes Spark watermarking and sliding windows (2-minute) to track user behavior over time.
* **Production-Ready Orchestration:** Fully containerized using **Docker Compose** with dual-listener Kafka configurations for hybrid development.
* **Real-time Analytics:** A Streamlit-based dashboard providing live metrics on throughput, active bots, and fraud trends.

---

## Tech Stack

| Component | Technology |
| :--- | :--- |
| **Streaming** | Apache Kafka (KRaft), Apache Spark Structured Streaming |
| **AI/ML** | SentenceTransformers (MiniLM), FAISS (Vector Search) |
| **Backend** | FastAPI, Python |
| **Frontend** | Streamlit |
| **Storage** | Apache Parquet, JSON |
| **Infrastructure** | Docker, Docker Compose |

---

## Getting Started

### Prerequisites
* Docker & Docker Compose
* Python 3.9+ (for local Spark development)

### Quick Start (Dockerized)
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Dishan18/FraudScale.git](https://github.com/Dishan18/FraudScale.git)
    cd fraudscale
    ```

2.  **Launch the infrastructure:**
    ```bash
    docker-compose up -d
    ```

3.  **Access the Dashboard:**
    Open `http://localhost:8501` in your browser to view real-time fraud metrics.

---

## Engineering Highlights & Fixes

Throughout development, several critical distributed systems challenges were addressed:
* **Memory Management:** Implemented an `IndexIDMap` with a sliding window for FAISS to prevent unbounded memory growth during long-running streams.
* **Checkpoint Management:** Resolved Spark restart replay issues by fine-tuning `startingOffsets` and checkpoint intervals to ensure data consistency.
* **Service Discovery:** Configured containerized networking to allow the API to seamlessly communicate with the Spark-generated file sinks using absolute path mounting.
* **Normalization:** Introduced capped normalization for behavioral features to prevent score explosion and ensure realistic detection thresholds.

---

## Project Roadmap

- [x] Kafka Ingestion Pipeline
- [x] Spark Behavioral Feature Engineering
- [x] AI Embedding & Similarity Search
- [x] Multi-signal Fraud Scoring Engine
- [x] Docker Orchestration
- [ ] Real-time Alerting Layer (Email/Slack triggers)
- [ ] Health and Metrics Monitoring Endpoints (`/health`, `/metrics`)

---

## Key Learnings
* **Streaming ≠ Batch:** Managing state and offsets is the most critical aspect of building reliable real-time pipelines.
* **Hybrid Signals:** Semantic similarity combined with behavioral patterns is significantly more effective than either signal used in isolation.
* **Scalability:** Vector search requires strict memory control strategies to remain stable in a streaming environment.