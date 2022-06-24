SELECT *
FROM {{ref('customer_investment')}} ci 
INNER JOIN read_parquet('../data/20220623.1553/shareclasses.parquet') s ON ci.shareclass_name = s.name
