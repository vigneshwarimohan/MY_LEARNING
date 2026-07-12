-- Create or replace a learning BigQuery table with sample data.
-- Change the project, dataset, and table names via environment variables or use the defaults in the Python script.

CREATE OR REPLACE TABLE `{{PROJECT_ID}}.{{DATASET}}.{{TABLE}}` AS
SELECT * FROM UNNEST([
  STRUCT(1 AS id, 'Product 1' AS name, 'Learning' AS category, 11.0 AS price),
  STRUCT(2 AS id, 'Product 2' AS name, 'Learning' AS category, 12.0 AS price),
  STRUCT(3 AS id, 'Product 3' AS name, 'Learning' AS category, 13.0 AS price),
  STRUCT(4 AS id, 'Product 4' AS name, 'Learning' AS category, 14.0 AS price),
  STRUCT(5 AS id, 'Product 5' AS name, 'Learning' AS category, 15.0 AS price),
  STRUCT(6 AS id, 'Product 6' AS name, 'Learning' AS category, 16.0 AS price),
  STRUCT(7 AS id, 'Product 7' AS name, 'Learning' AS category, 17.0 AS price),
  STRUCT(8 AS id, 'Product 8' AS name, 'Learning' AS category, 18.0 AS price),
  STRUCT(9 AS id, 'Product 9' AS name, 'Learning' AS category, 19.0 AS price),
  STRUCT(10 AS id, 'Product 10' AS name, 'Learning' AS category, 20.0 AS price)
]);
