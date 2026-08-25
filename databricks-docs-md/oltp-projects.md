---
title: Lakebase Postgres
source_url: https://docs.databricks.com/aws/en/oltp/projects/
---

# Lakebase Postgres

Source: https://docs.databricks.com/aws/en/oltp/projects/

Last updated on **Aug 4, 2026**

# Lakebase Postgres

Lakebase is a fully managed Postgres database integrated into the Databricks platform. Build real-time transactional applications alongside your lakehouse data, with automatic scaling, instant branching, and native Unity Catalog integration.

* **Build low-latency apps:** Connect Databricks Apps or any application to Lakebase for transactional workloads.
* **Serve lakehouse data:** Sync Unity Catalog tables into Lakebase so applications can query them at low latency.
* **Store Postgres changes:** Store Postgres changes as Delta tables for downstream pipelines and audit.
* **AI and ML:** Use Lakebase as an online feature store for ML models, or as a state store for agents.

![Lakebase integration with Databricks services](/aws/en/assets/images/lakebase-full-functional-d09be2f4160cf6b806b63f5b395f2789.png)

## Get started[​](#get-started "Direct link to Get started")

* + [Get a Postgres database](/aws/en/oltp/projects/get-started)
  + Create a project, branch, and database. Connect with `psql` or any Postgres driver.
* + [Serve lakehouse data](/aws/en/oltp/projects/quickstart-synced-tables)
  + Sync Unity Catalog tables into Postgres for low-latency app reads.
* + [Store Postgres changes in the lakehouse](/aws/en/oltp/projects/quickstart-lakebase-cdf)
  + (Public Preview) Store Postgres changes as Delta with full change history.
* + [Build applications](/aws/en/oltp/projects/build-applications)
  + Build apps backed by Lakebase using Databricks Apps, external integrations, or the Data API.

## Key features[​](#key-features "Direct link to Key features")

Explore features that optimize performance, reduce costs, and enable flexible development workflows.

* + [Autoscaling](/aws/en/oltp/projects/autoscaling)
  + Automatically adjust compute resources based on workload demand.
* + [Scale to zero](/aws/en/oltp/projects/scale-to-zero)
  + Automatically suspend inactive computes to minimize costs.
* + [Branches](/aws/en/oltp/projects/branches)
  + Create isolated branches for development and testing.
* + [Read replicas](/aws/en/oltp/projects/read-replicas)
  + Create read-only replicas to scale read operations.
* + [Instant restore](/aws/en/oltp/projects/point-in-time-restore)
  + Create a new branch from any point in time within your history window.
* + [High availability](/aws/en/oltp/projects/manage-high-availability)
  + Configure automatic failover to keep your database available during compute failures.

* + [Disaster recovery](/aws/en/oltp/projects/disaster-recovery)
  + Replicate to a Secondary Workspace in another region for manual failover.

## Connect and query[​](#connect-and-query "Direct link to Connect and query")

Use various tools and interfaces to connect to and query your database.

* + [Connect to your database](/aws/en/oltp/projects/connect)
  + Learn different ways to connect to your Lakebase database.
* + [Query with SQL Editor](/aws/en/oltp/projects/sql-editor)
  + Use the built-in SQL Editor to query and manage your database.
* + [Tables editor](/aws/en/oltp/projects/table-editor)
  + Use the visual interface to view, edit, and manage data and schemas.
* + [Postgres clients](/aws/en/oltp/projects/postgres-clients)
  + Connect using standard Postgres clients and tools.
* + [Querying data at a point in time](/aws/en/oltp/projects/point-in-time-branching)
  + Query data using point-in-time branches.

## Learn more[​](#learn-more "Direct link to Learn more")

* + [Use cases](/aws/en/oltp/projects/use-cases)
  + Lakebase patterns: serve lakehouse data, replicate to the lakehouse, application backend, agents and ML.
* + [Region availability](/aws/en/oltp/projects/manage-projects#availability)
  + Supported regions for Lakebase Postgres.

On this page

* [Get started](#get-started)* [Key features](#key-features)* [Connect and query](#connect-and-query)* [Learn more](#learn-more)
