## **Project Log: FraudScale**

---

### **Day 1: Infrastructure & Ingest Foundation**

**Progress Summary:**

* **Project Initialization:** Established a modular repository structure (API, Spark, Kafka, Embedding Service, Scripts).
* **Data Generation:** Developed `generate_data.py` to produce a realistic dataset of ~200,000 JSON reviews with timestamps, user IDs, and varied text patterns.
* **Kafka Backbone:** Successfully deployed **Apache Kafka 4.2.0** in **KRaft mode** (ZooKeeperless) to minimize resource footprint.
* **Ingest Pipeline:** Implemented and executed producer pipeline, achieving a stable throughput of ~1,000 events/sec into the `reviews` topic.

**Issues Solved:**

* Kafka Windows path issues fixed via correct working directory usage.
* KRaft quorum/config issues resolved via proper storage formatting.
* Disk/log directory issues fixed by relocating to non-system drive.

**Status:**

* Kafka: Online (KRaft)
* Ingest: Complete
* Next: Spark Streaming

---

### **Day 2: Streaming Pipeline & Behavioral Feature Engineering**

**Progress Summary:**

* Configured **Apache Spark 3.5.x** with Kafka integration.
* Built structured streaming pipeline from Kafka → DataFrame.
* Implemented:

  * Heuristic filtering (noise reduction)
  * Timestamp parsing + watermarking
  * Sliding window aggregation (2 min window)
  * Per-user behavioral features:

    * `review_count`
    * `review_rate`
* Modularized pipeline:

  * `heuristics.py`
  * `behavior.py`
  * `streaming.py`

**Issues Solved:**

* Spark-Kafka connector mismatch fixed via correct package version.
* Windows Hadoop dependency issues fixed (`winutils`, DLLs).
* Module import issues resolved via `PYTHONPATH`.
* Output mode corrected (`append → update`).

**System Behavior:**

* Stable micro-batching (~3–5 sec)
* Stateful aggregation working correctly
* Watermark progressing properly

**Pipeline:**

```
Kafka → Spark → Heuristics → Behavioral Aggregation
```

**Status:**

* Streaming stable
* Next: AI similarity + fraud scoring

---

### **Day 3: Embedding-Based Similarity Detection (AI Layer)**

**Progress Summary:**

* Integrated **SentenceTransformers (MiniLM)** for semantic embedding.
* Implemented `mapInPandas` pipeline for batch embedding generation.
* Added **FAISS vector index** for similarity search.
* Designed similarity system:

  * Historical similarity (top-k search)
  * Intra-batch similarity (duplicate detection)
* Switched from binary similarity → **continuous similarity score**

**Key Design Upgrade:**

```
Binary rule → Continuous signal
```

**Issues Solved:**

* Spark crashes due to model download → fixed using local model caching (`local_files_only=True`)
* Schema mismatch (`review_rate missing`) → fixed by extending schema
* Similarity = 0 issue → fixed via:

  * top-k aggregation
  * intra-batch similarity
  * generator improvements

**System Behavior:**

* Similarity now produces meaningful range (~0.3–0.9)
* Bots form detectable semantic clusters

**Pipeline:**

```
Kafka → Spark → Behavior → Embeddings → Similarity
```

**Status:**

* AI layer stable
* Next: scoring system

---

### **Day 4: Fraud Scoring Engine**

**Progress Summary:**

* Implemented weighted fraud scoring:

```
fraud_score =
  0.5 * similarity_score +
  0.3 * review_rate +
  0.2 * review_count
```

* Introduced **score normalization (critical fix)**:

  * Capped `review_count`
  * Capped `review_rate`
* Added final classification:

  * `is_fraud` based on threshold (0.7)

**Key Upgrade:**

```
Rule-based detection → multi-signal scoring model
```

**Issues Solved:**

* Score explosion (>1.0) fixed via normalization
* Unrealistic 100% fraud rates corrected
* Generator redesigned for realistic entropy

**Pipeline:**

```
Kafka → Spark → Behavior → AI → Scoring → Fraud Label
```

**Status:**

* Detection logic stable and realistic
* Next: storage + dashboard

---

### **Day 5: Storage Layer & Dashboard Integration**

**Progress Summary:**

* Implemented dual sink output:

  * `output/live` (JSON → dashboard)
  * `output/fraud` (Parquet → storage)
* Built **Streamlit dashboard**:

  * Total records
  * Fraud cases
  * Fraud rate
  * Active bots
* Connected dashboard → live output

**Issues Solved:**

* No data issue → fixed Spark write mode (`append`)
* Dashboard crashes → limited read size (tail / latest file)
* State errors (`prev[...]`) → fixed via session state initialization

**System Behavior:**

* Real-time metrics update correctly
* Stable visualization without overload

---

### **Day 6: System Stability & Scaling Fixes**

**Progress Summary:**

* Fixed **Spark restart replay issue**:

  * Understood checkpoint vs offsets
  * Switched to `startingOffsets = latest`
* Established correct runtime flow:

```
Kafka → Spark → Producer
```

* Fixed FAISS memory growth:

  * Implemented **IndexIDMap + sliding window**
* Improved embedding pipeline performance:

  * batching
  * reduced offsets per trigger

**Issues Solved:**

* Full replay after restart → checkpoint handling
* Kafka topic corruption → full reset via log deletion
* Spark job crashes → model preload + network isolation
* Memory growth → proper index management

---

### **Final System Architecture**

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
 Parquet Storage   Live JSON → Dashboard
```

---

### **Current Status**

* Kafka: Stable (KRaft mode)
* Spark: Stable streaming with checkpointing
* AI Layer: Functional and realistic
* Scoring: Normalized and meaningful
* Dashboard: Live and stable
* System: End-to-end working

---

### **Next Step**

**Dockerization**

* Containerize:

  * Kafka
  * Spark
  * Producer
  * Dashboard
* Enable one-command deployment

---

### **Key Learnings**

* Streaming ≠ batch → checkpointing is critical
* Similarity is noisy → must be combined with behavior
* Real systems use continuous scoring, not binary rules
* Memory management is essential in vector search systems
* Data realism (generator quality) directly impacts model behavior

---

### **Project Outcome**

Built a **real-time fraud detection system** that:

* Processes streaming data
* Detects coordinated bot behavior
* Uses AI-based semantic similarity
* Produces interpretable fraud scores
* Visualizes results in real time

---
