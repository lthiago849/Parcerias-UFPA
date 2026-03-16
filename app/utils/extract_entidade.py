import pandas as pd

df = pd.read_csv("app/utils/curriculos_componentes_materias.csv")


# Pegar apenas as colunas de universidade e remover as linhas duplicadas
df_univ = df[['nome_universidade', 'sigla_universidade', 'campus_universidade']].drop_duplicates().dropna()

# Pegar as colunas de instituto e também a sigla da universidade para fazer o vínculo
df_inst = df[['nome_instituto', 'sigla_instituto', 'sigla_universidade']].drop_duplicates().dropna()


df_univ.to_csv("app/statics/universidades.csv", index=False)
df_inst.to_csv("app/statics/institutos.csv", index=False)

