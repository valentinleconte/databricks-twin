CREATE OR REPLACE TABLE workspace.databricks_twin.support_tickets (
  ticket_id STRING NOT NULL,
  status STRING,
  priority STRING,
  assignee STRING,
  summary STRING,
  updated_at DATE
) TBLPROPERTIES (delta.enableChangeDataFeed = true);

INSERT INTO workspace.databricks_twin.support_tickets VALUES
  ('101', 'Open',        'High',   'Alice Martin', 'Vector Search index sync stuck in PROVISIONING', DATE'2026-08-20'),
  ('102', 'In Progress', 'Medium', 'Bob Chen',      'Add hybrid keyword+vector ranking to doc_chunks index', DATE'2026-08-21'),
  ('103', 'Resolved',    'Low',    'Carla Diaz',    'Genie space login redirect loop for SSO users', DATE'2026-08-18'),
  ('104', 'Open',        'High',   'Alice Martin',  'Model serving endpoint databricks-gpt-5-2 returns 404', DATE'2026-08-23'),
  ('105', 'Open',        'Medium', 'Deepak Rao',    'Unity Catalog table doc_chunks missing Change Data Feed on staging', DATE'2026-08-22'),
  ('106', 'In Progress', 'Low',    'Bob Chen',      'Improve chunking overlap for long Databricks doc pages', DATE'2026-08-19'),
  ('107', 'Resolved',    'Medium', 'Carla Diaz',    'App service principal missing CAN_RUN on Genie space', DATE'2026-08-17'),
  ('108', 'Closed',      'Low',    'Deepak Rao',    'Typo in agent system prompt routing instructions', DATE'2026-08-15');
