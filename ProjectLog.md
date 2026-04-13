## **Project Log: FraudScale**

---

### **Day 1: Infrastructure & Ingest Foundation**

**Progress Summary:**

* **Project Initialization:** Established a modular repository structure (API, Spark, Kafka, Embedding Service, Scripts).
* **Data Generation:** Developed `generate_data.py` to produce a realistic dataset of ~200,000 JSON reviews with timestamps, user IDs, and varied text patterns.
* **Kafka Backbone:** Successfully deployed **Apache Kafka 4.2.0** in **KRaft mode** (ZooKeeperless) to minimize resource footprint.
* **Ingest Pipeline:** Implemented and executed `producer.py`, achieving a stable throughput of ~1,000 events/sec into the `reviews` topic.

**Issues Solved:**

* **Kafka 4.2.0 Windows Pathing:** Resolved PowerShell "not recognized" errors by normalizing execution path to Kafka root (`D:\kafka`).
* **KRaft Configuration:** Fixed quorum/reconfiguration errors using `--standalone` storage formatting.
* **Resource Constraints:** Optimized broker storage/log directories on D: drive to avoid system drive issues.

**Status:**

* **Kafka:** Online (KRaft)
* **Ingest:** Complete (≈145K events streamed)
* **Next Phase:** Day 2 — Spark Structured Streaming & Heuristic Filtering

---

### **Day 2: Streaming Pipeline & Behavioral Feature Engineering**

**Progress Summary:**

* **Spark Setup:** Installed and configured **Apache Spark 3.5.x** with proper Windows environment (SPARK_HOME, HADOOP_HOME, PATH, winutils, native DLLs).
* **Kafka Integration:** Connected Spark Structured Streaming to Kafka using `spark-sql-kafka` connector.
* **Stream Parsing:** Implemented JSON parsing pipeline converting Kafka byte stream → structured DataFrame.
* **Stage 1 — Heuristic Filtering:** Removed low-quality data (null + short reviews) to reduce noise and processing load.
* **Stage 2 — Behavioral Features:** Built real-time windowed aggregation:

  * 2-minute sliding window
  * Per-user review counts
  * Watermarking (5 minutes) for state control
* **Modularization:** Refactored logic into:

  * `heuristics.py`
  * `behavior.py`
  * `streaming.py` (orchestrator)

---

**Issues Solved:**

* **Spark–Kafka Connector Missing:** Fixed using `--packages spark-sql-kafka-0-10_2.12`.
* **Version Mismatch:** Resolved PySpark 4.x incompatibility by aligning to Spark 3.5.x ecosystem.
* **Windows Hadoop Errors:** Fixed `NativeIO` crash by adding `winutils.exe` + `hadoop.dll`.
* **Environment Variables:** Corrected incorrect `SPARK_HOME`/`HADOOP_HOME` paths and made setup permanent.
* **Module Import Errors:** Fixed `ModuleNotFoundError: spark` using `PYTHONPATH` + `__init__.py`.
* **Streaming Output Mode:** Switched from `append` → `update` for aggregation compatibility.

---

**System Behavior (Validated):**

* Throughput: ~300–700 rows/sec processed
* Stable micro-batching (~3 sec trigger)
* Stateful aggregation working (≈3000 active state rows)
* Watermark advancing correctly
* Real-time output:

```text
window | user_id | review_count
```

---

**Key Capability Achieved:**

```text
Real-time behavioral signal extraction from streaming data
```

This forms the **core primitive for fraud detection**.

---

**Current Pipeline:**

```text
Kafka → Spark Streaming → Heuristic Filter → Window Aggregation → Console
```

---

**Status:**

* **Kafka:** Online
* **Spark Streaming:** Active
* **Pipeline:** Stable and validated
* **Next Phase:** Day 3 — Fraud Scoring & Detection Logic
