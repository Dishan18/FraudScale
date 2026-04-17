
---

# **Project Log: FraudScale**

---

## **Day 1: Infrastructure & Ingest Foundation**

**Progress Summary:**

* Initialized modular project structure (API, Spark, Kafka, AI, Scripts)
* Built `generate_data.py` to simulate ~200K realistic review events
* Deployed **Apache Kafka (KRaft mode)** without ZooKeeper
* Implemented Kafka producer with ~1000 events/sec throughput

**Issues Solved:**

* Kafka path issues (Windows) → fixed via correct working directory
* KRaft quorum/config errors → fixed via storage formatting
* Log directory failures → moved to non-system drive

**Status:**

* Kafka: Stable
* Ingestion: Complete
* Next: Streaming pipeline

---

## **Day 2: Streaming Pipeline & Behavioral Features**

**Progress Summary:**

* Set up **Spark Structured Streaming (3.5.x)** with Kafka
* Built streaming pipeline: Kafka → DataFrame
* Implemented:

  * Timestamp parsing + watermarking
  * Sliding window aggregation (2 min)
  * Behavioral features:

    * `review_count`
    * `review_rate`
* Modularized pipeline (`heuristics.py`, `behavior.py`, `streaming.py`)

**Issues Solved:**

* Spark-Kafka connector mismatch → corrected package version
* Windows Hadoop issues → configured `winutils`
* Import issues → fixed using `PYTHONPATH`
* Output mode mismatch → corrected

**System Behavior:**

* Stable micro-batching (3–5 sec)
* Stateful aggregation working

**Pipeline:**

```
Kafka → Spark → Behavioral Aggregation
```

---

## **Day 3: Embedding-Based Similarity Detection**

**Progress Summary:**

* Integrated **SentenceTransformers (MiniLM)**
* Implemented batch embedding using `mapInPandas`
* Added **FAISS similarity search**
* Designed similarity logic:

  * historical similarity (top-k)
  * intra-batch similarity

**Key Upgrade:**

```
Binary detection → Continuous similarity scoring
```

**Issues Solved:**

* Model download crashes → used local caching
* Schema mismatch → fixed missing columns
* Similarity always 0 → fixed via top-k + batch comparison

**System Behavior:**

* Similarity range stabilized (~0.3–0.9)
* Bot clusters detectable

**Pipeline:**

```
Kafka → Spark → Behavior → Embeddings → Similarity
```

---

## **Day 4: Fraud Scoring Engine**

**Progress Summary:**

Implemented weighted scoring:

```
fraud_score =
  0.5 * similarity_score +
  0.3 * review_rate +
  0.2 * review_count
```

* Added normalization:

  * capped `review_rate`
  * capped `review_count`
* Implemented fraud classification (`threshold = 0.7`)

**Key Upgrade:**

```
Rule-based → Multi-signal scoring system
```

**Issues Solved:**

* Score explosion (>1.0) → fixed via normalization
* Unrealistic fraud spikes → fixed generator entropy

**Pipeline:**

```
Kafka → Spark → Behavior → AI → Scoring → Fraud Label
```

---

## **Day 5: Storage Layer & Dashboard**

**Progress Summary:**

* Implemented dual output:

  * `output/live` → JSON for dashboard
  * `output/fraud` → Parquet for storage
* Built **Streamlit dashboard**:

  * Throughput
  * Fraud cases
  * Fraud rate
  * Active bots

**Issues Solved:**

* No data output → fixed Spark write mode (`append`)
* Dashboard crashes → fixed state handling
* Large data overload → limited read size

**System Behavior:**

* Real-time metrics updating correctly
* Stable UI

---

## **Day 6: Stability, Scaling & Streaming Fixes**

**Progress Summary:**

* Fixed Spark restart behavior:

  * used `startingOffsets = latest`
  * understood checkpoint vs offset interaction
* Improved performance:

  * batching
  * `maxOffsetsPerTrigger`
* Fixed FAISS memory issue:

  * implemented **IndexIDMap + sliding window**

**Issues Solved:**

* OffsetOutOfRange errors → fixed via offset config + checkpoint reset
* Full data replay → corrected offset strategy
* Memory growth → bounded vector index
* Spark crashes → model preload + stability fixes

**System Behavior:**

* Stable long-running streaming
* Controlled memory usage

---

## **Day 7: Dockerization & System Integration**

**Progress Summary:**

* Containerized:

  * Kafka (KRaft)
  * FastAPI
  * Streamlit dashboard
* Set up **Docker Compose orchestration**
* Connected services via Docker network
* Mounted shared volume:

```
./output → /app/output
```

---

**Critical Issues Solved:**

* **Dashboard showing zero values**

  * Cause: `localhost` inside container
  * Fix: switched to `http://api:8000`

* **API not reading Spark output**

  * Cause: path mismatch
  * Fix: used absolute paths:

    ```
    /app/output/live
    /app/output/fraud
    ```

* **Empty API responses**

  * Cause: `_SUCCESS`, `.crc` files
  * Fix: filtered `part-*` files only

* **JSON parsing failures**

  * Cause: nested schema (`embedding`, `window`)
  * Fix: dropped incompatible columns

* **Kafka connectivity split**

  * Implemented dual listeners:

    * `localhost:9094` (host)
    * `kafka:9092` (containers)

---

**System Behavior:**

* Full pipeline works across hybrid setup:

```
Local Spark → Docker Kafka → Docker API → Dashboard
```

---

## **Final Architecture**

```
Producer → Kafka → Spark Streaming
              ↓
      Behavioral Features
              ↓
        AI Embeddings
              ↓
        Similarity Engine
              ↓
        Fraud Scoring
              ↓
     ┌───────────────┬───────────────┐
     ↓               ↓
 Parquet Storage   Live JSON → API → Dashboard
```

---

## **Current Status**

* Kafka: Stable (KRaft mode)
* Spark: Stable streaming
* AI Layer: Functional
* Scoring: Normalized
* API: Serving correctly
* Dashboard: Real-time visualization
* System: Fully working end-to-end

---

## **Next Steps**

* Add alerting layer (fraud triggers)
* Add monitoring endpoints (`/health`, `/metrics`)
* Optional deployment (Render / EC2)

---

## **Key Learnings**

* Streaming systems require careful **offset + checkpoint management**
* Behavioral + semantic signals outperform rule-based detection
* Real-world systems use **continuous scoring, not binary logic**
* Vector search requires **memory control strategies**
* Container networking ≠ localhost (service discovery matters)
* File-based pipelines require **strict schema handling**

---

## **Project Outcome**

Built a **real-time fraud detection system** that:

* Processes high-volume streaming data
* Detects coordinated bot behavior
* Uses semantic similarity + behavioral signals
* Produces interpretable fraud scores
* Visualizes results in real time via dashboard

---
