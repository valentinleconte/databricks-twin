---
title: DatabricksUnity Catalogtable types
source_url: https://docs.databricks.com/aws/en/tables/delta-table
---

# DatabricksUnity Catalogtable types

Source: https://docs.databricks.com/aws/en/tables/delta-table

Last updated on **Jul 10, 2026**

# Databricks Unity Catalog table types

Unity Catalog supports three primary table types: managed, external, and foreign tables. Each type differs in how data is stored, managed, and governed.

## Managed tables[​](#managed-tables "Direct link to managed-tables")

Managed tables are the default and recommended table type. Unity Catalog manages the data lifecycle, storage location, and optimizations. When you drop a managed table, both the metadata and underlying data files are deleted.

Managed tables are backed by Delta Lake or Apache Iceberg and provide:

* Automatic optimization for reduced storage and compute costs
* Faster query performance across all client types
* Automatic table maintenance
* Secure access for non-Databricks clients via open APIs
* Automatic upgrades to the latest platform features

Data files are stored in the schema or catalog containing the table. See [Unity Catalog managed tables for Delta Lake and Apache Iceberg](/aws/en/tables/managed).

## External tables[​](#external-tables "Direct link to external-tables")

External tables reference data stored in cloud object storage that you manage. Unity Catalog governs data access but doesn't manage data lifecycle, optimizations, or storage layout. When you drop an external table, only the catalog metadata is removed and the underlying data files remain.

Unity Catalog external tables support the Delta Lake, CSV, JSON, AVRO, PARQUET, ORC, and TEXT formats. Databricks recommends that you use the Delta Lake format because it has transactional guarantees and performance optimizations that the other formats don't.

Use external tables when you need to:

* Register existing data that isn't compatible with Unity Catalog managed tables
* Provide direct data access from non-Databricks clients that don't support other external access patterns

See [Work with external tables](/aws/en/tables/external).

## Foreign tables[​](#foreign-tables "Direct link to foreign-tables")

Foreign tables (also called federated tables) are read-only tables managed by a foreign catalog registered in Unity Catalog. External systems manage the data and metadata, while Unity Catalog adds data governance for querying.

Databricks supports two methods for registering foreign tables:

* **Query federation**: Uses secure JDBC connections to external data systems like PostgreSQL and MySQL
* **Catalog federation**: Connects external catalogs to query data directly in file storage

Foreign tables using the Delta Lake format lack many optimizations available in Unity Catalog managed tables. For production workloads or frequently queried datasets, migrate to Unity Catalog managed tables for better performance. See [Work with foreign tables](/aws/en/tables/foreign).

## Comparison of table types[​](#comparison-of-table-types "Direct link to comparison-of-table-types")

The following table compares the three table types:

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Feature Managed tables External tables Foreign tables|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Data lifecycle management Unity Catalog manages You manage External system manages|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Storage location Unity Catalog manages You specify External system manages|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Automatic optimizations Yes Limited No|  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Formats supported Delta Lake, Apache Iceberg Delta Lake (recommended), CSV, JSON, AVRO, PARQUET, ORC, TEXT Depends on external system|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Data deleted on `DROP TABLE` Yes No No|  |  |  |  | | --- | --- | --- | --- | | Best for Production workloads, frequently queried data Legacy integrations, existing data Migration from external systems, temporary access | | | | | | | | | | | | | | | | | | | | | | | | | | | |

|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Feature Managed tables External tables Foreign tables|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Data lifecycle management Unity Catalog manages You manage External system manages|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Storage location Unity Catalog manages You specify External system manages|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Automatic optimizations Yes Limited No|  |  |  |  |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | Formats supported Delta Lake, Apache Iceberg Delta Lake (recommended), CSV, JSON, AVRO, PARQUET, ORC, TEXT Depends on external system|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | Data deleted on `DROP TABLE` Yes No No|  |  |  |  | | --- | --- | --- | --- | | Best for Production workloads, frequently queried data Legacy integrations, existing data Migration from external systems, temporary access | | | | | | | | | | | | | | | | | | | | | | | | | | | |

## Other table types[​](#other-table-types "Direct link to other-table-types")

Databricks also supports specialized table types for specific use cases:

* **Streaming tables**: Lakeflow pipelines datasets backed by Delta Lake with incremental processing logic
* **Materialized views**: Lakeflow pipelines datasets backed by Delta Lake that materialize query results using managed flow logic

## Legacy table types[​](#legacy-table-types "Direct link to legacy-table-types")

The following legacy table types are supported for backward compatibility but aren't recommended for new development.

### Hive tables[​](#hive-tables "Direct link to hive-tables")

Hive tables are managed by the legacy Hive metastore and use legacy patterns, including Hive SerDe codecs and Hive SQL syntax. By default, tables registered using the legacy Hive metastore store data in the legacy DBFS root.

Databricks recommends that you migrate all tables from the legacy HMS to Unity Catalog. See [Database objects in the legacy Hive metastore](/aws/en/database-objects/hive-metastore).

You can optionally federate a Hive metastore to Unity Catalog, and access the tables as foreign tables in Unity Catalog. See [Hive metastore federation: enable Unity Catalog to govern tables registered in a Hive metastore](/aws/en/query-federation/hms-federation-concepts).

Apache Spark supports registering and querying Hive tables, but Hive SerDe codecs aren't optimized for Databricks. Register Hive tables only when you need to support queries on data written by external systems. See [Hive table (legacy)](/aws/en/archive/legacy/hive-tables).

### Live tables[​](#live-tables "Direct link to live-tables")

The term *live tables* refers to an earlier implementation of functionality now available as *materialized views*. Update legacy code that references live tables to use materialized view syntax. See [Spark Declarative Pipelines](/aws/en/ldp/) and [Materialized views](/aws/en/ldp/concepts/materialized-views).

On this page

* [Managed tables](#managed-tables)* [External tables](#external-tables)* [Foreign tables](#foreign-tables)* [Comparison of table types](#comparison-of-table-types)* [Other table types](#other-table-types)* [Legacy table types](#legacy-table-types)
            + [Hive tables](#hive-tables)+ [Live tables](#live-tables)
