# HanduFlow

**HanduFlow** is an architecture-agnostic data movement and transformation framework designed to manage evolving data reliably across modern data platforms.

It provides a standardized way to ingest, transform, and evolve data across layers (for example, bronze → silver → gold), while supporting change data capture (CDC), SCD Type 2, schema enforcement, and automated lineage generation.

HanduFlow focuses on **consistency, reusability, and production readiness**, without locking users into a specific architecture or vendor.

---

## Why HanduFlow?

Modern data platforms commonly struggle with:

* Inconsistent CDC implementations
* Repeated and fragile SCD logic
* Hard-to-maintain transformation pipelines
* Missing or incomplete data lineage

HanduFlow centralizes these concerns into a **single, reusable framework**, allowing teams to focus on business logic instead of rebuilding data plumbing for every pipeline.

---

## Key Capabilities

### Data Movement & Load Patterns

HanduFlow supports multiple ingestion and evolution strategies:

* **Full Load**
* **Append Load**
* **Incremental CDC**
* **SCD Type 2**

All load patterns follow a consistent, configurable execution model across datasets.

---

### Architecture-Agnostic Design

HanduFlow works naturally with **Medallion-style architectures**, but it is **not dependent** on any specific architectural pattern.

It can be used with:

* Bronze / Silver / Gold layers
* Hub-and-spoke models
* Custom layered designs
* Single-layer analytical tables

---

### Transformation Framework

* Clear separation of ingestion, validation, transformation, and persistence
* Reusable transformation logic
* Declarative and programmatic execution styles

---

### Schema & Data Quality Enforcement

* Schema alignment and enforcement at ingestion
* Built-in standard data quality checks
* Support for custom, query-based validations
* Pre-load and post-load validation stages

---

### Lineage Generation

HanduFlow can generate **feed-level lineage**, including:

* Source datasets
* Intermediate transformations
* Target tables

Lineage output can be exported for visualization and governance use cases.

---

## Technology Stack

HanduFlow is designed for distributed, production-grade environments:

* **Apache Spark**
* **Delta Lake**
* Cloud object storage (S3 / ADLS / GCS)
* Databricks (tested environment)

---

## About the Project

HanduFlow is created and maintained by **Harsh Handoo**, Data Engineer. Thats why the name "handuflow", pronounced "hundooh-flow"

The framework was built to standardize common data movement patterns, reduce boilerplate, and improve reliability in real-world Spark and Delta Lake workloads.

---

## Installation

```bash
pip install handuflow
```

---

## Requirements

### Cluster Resources (Typical)

| Workload                       | Minimum              | Recommended             |
| ------------------------------ | -------------------- | ----------------------- |
| Local development              | 4 vCPU, 8 GB RAM     | 8 vCPU, 16 GB RAM       |
| Small datasets (<10M rows)     | 2 executors × 4 GB   | 4 executors × 8 GB      |
| Medium datasets (10–100M rows) | 4 executors × 8 GB   | 8 executors × 16 GB     |
| Large datasets (>100M rows)    | 8+ executors × 16 GB | Cluster-specific tuning |

---

### Recommended Production Setup

* Linux-based Spark cluster
* Spark FAIR scheduler enabled
* Delta Lake tables on cloud object storage
* Versioned releases via PyPI and GitHub

---

### Supported Storage

* Local filesystem (development only)
* HDFS / ADLS / S3 / GCS (recommended)
* DBFS (Databricks)

---

### Operating Systems

* Linux (recommended)
* macOS
* Windows (WSL recommended)

⚠️ Production deployments are strongly recommended on Linux-based systems.

**Note:** HanduFlow is currently tested on Databricks.

---

## Usage

### Prerequisites

1. Create a dedicated directory for HanduFlow configuration and metadata
   Example:

   ```bash
   /handuflow_dir/
   ```

2. Configure `config.ini`

    ```ini
    [DEFAULT]
    outbound_directory_name=handuflow_outbound
    log_directory_name=handuflow_logs
    temp_log_location=/handuflow_dir/temp
    file_hunt_path=/handuflow_dir/
    log_retention_policy_in_days=7
    max_concurrent_batches=4

    [FILES]
    master_spec_name=master_specs.xlsx

    [LINEAGE_DIAGRAM]
    BOX_WIDTH=4.4
    BOX_HEIGHT=2.2
    X_GAP=2.0
    Y_GAP=2.5
    ROOT_GAP=2.0
    ```

---

### Master Specification

The master specification file (`master_specs.xlsx`) defines feeds and dependencies.

Required fields include:

* feed_id
* system_name
* subsystem_name
* category
* data_flow_direction
* residing_layer
* feed_name
* load_type
* target_schema_name
* target_table_name
* parent_feed_id
* is_active

---

### Feed Specification (JSON)

Each feed defines schema, quality checks, and load behavior.

```json
{
  "primary_key": "col1",
  "partition_keys": [],
  "vacuum_hours": 168,
  "source_table_name": "test.test",
  "selection_schema": {
    "type": "struct",
    "fields": [
      { "name": "col1", "type": "string", "nullable": true },
      { "name": "col2", "type": "string", "nullable": true }
    ]
  },
  "standard_checks": [
    {
      "check_sequence": ["_check_primary_key"],
      "column_name": "col1",
      "threshold": 0
    }
  ]
}
```

---

### Spark Configuration (FAIR Scheduler)

```bash
spark.scheduler.mode FAIR
```

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
        .appName("HanduFlow")
        .config("spark.scheduler.mode", "FAIR")
        .getOrCreate()
)
```

---

## Execution

```python
import configparser
from handuflow import Orchestrator

cfg = configparser.ConfigParser()
cfg.read("/handuflow_dir/config.ini")

orchestrator = Orchestrator(spark, config=cfg)
orchestrator.run()
```

---

## Logging

* Logs are written to the directory defined in `config.ini`
* Log retention and rotation are configurable
* Execution-level and feed-level logs are supported

---

## License

Apache License (Version 2.0, January 2004)
<http://www.apache.org/licenses/>
