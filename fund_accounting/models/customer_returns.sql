SELECT 
  cs.name AS customer,
  f.name AS fund,
  cs.shareclass_name AS shareclass,
  max(fr.returns) AS maxreturn
FROM {{ref('customer_shareclasses')}} cs 
INNER JOIN read_parquet('../data/20220623.1553/funds.parquet') f ON cs.fund_name = f.name
INNER JOIN read_parquet('../data/20220623.1553/fund_returns.parquet') fr ON f.name = fr.fund
GROUP BY cs.name, f.name, shareclass
