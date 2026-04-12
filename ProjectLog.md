
## **Project Log: FraudScale**

### **Day 1: Infrastructure & Ingest Foundation**

**Progress Summary:**
* **Project Initialization:** Established a modular repository structure (API, Spark, Kafka, Embedding Service, Scripts).
* **Data Generation:** Developed `generate_data.py` to produce a realistic dataset of 200,000 JSON reviews with timestamps, user IDs, and varied text patterns.
* **Kafka Backbone:** Successfully deployed **Kafka 4.2.0** in **KRaft mode** (ZooKeeperless) to minimize resource footprint.
* **Ingest Pipeline:** Implemented and executed `producer.py`, achieving a stable throughput of ~1,000 events/sec into the `reviews` topic.

**Issues Solved:**
* **Kafka 4.2.0 Windows Pathing:** Resolved PowerShell "not recognized" errors by normalizing the execution path to the Kafka root (`D:\kafka`).
* **KRaft Configuration:** Fixed "Controller Quorum" and "Reconfiguration" errors by utilizing the `--standalone` flag during storage formatting, bypassing the need for a complex multi-node cluster.
* **Resource Constraints:** Optimized the Kafka broker to run on the D: drive with manual log directory mapping to prevent system drive clutter and permission issues.

**Status:**
* **Kafka:** Online (KRaft)
* **Ingest:** Active (🏁 Streaming complete. Total sent: 145925)
* **Next Phase:** Day 2 — Spark Structured Streaming & Heuristic Filtering.
