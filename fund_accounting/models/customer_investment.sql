{{
  config(
    materialized='table'
  )
}}

SELECT c.name, i.shareclass_name, c.turnover
FROM  read_parquet('../data/20220623.1553/customers.parquet') c 
INNER JOIN read_parquet('../data/20220623.1553/investment.parquet') i ON c.name = i.customer_name
