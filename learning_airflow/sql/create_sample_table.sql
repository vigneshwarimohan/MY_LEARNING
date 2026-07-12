-- This SQL is just a learning sample and is not used by the sample Python DAG.
-- In a production Airflow DAG, this could be executed by a BigQuery operator.
CREATE TABLE IF NOT EXISTS `project.dataset.learning_sample_table` (
  id INT64,
  name STRING,
  category STRING,
  price FLOAT64
);
