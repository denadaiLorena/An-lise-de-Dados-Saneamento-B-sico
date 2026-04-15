import os

import basedosdados as bd


BILLING_PROJECT_ID =  "analise-saneamento"

sql = """
SELECT *
FROM `basedosdados.br_mme_saneamento.municipio`
WHERE sigla_uf = 'ES'
LIMIT 1000
"""

df = bd.read_sql(query=sql, billing_project_id=BILLING_PROJECT_ID)
print(df.head())