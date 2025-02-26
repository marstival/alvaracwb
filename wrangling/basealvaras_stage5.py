#%%
import re
import config
import pandas as pd
import numpy as np
from datetime import datetime
import os
#%%
staging_data_home = config.get_data_home()
dataset_home = config.get_existing_data_home()

df = pd.read_parquet(staging_data_home + 'stages/base_alvaras_stage04.parquet')

dfcnae = pd.read_parquet(dataset_home + 'CNAE_Subclasses_2_3_tabular.parquet')

#%%
def transform_value(value: str) -> str:
    if (pd.isna(value)):
        return None
    
    # Extract the substring between the first digit sequence and the last '-'
    match = re.search(r'(\d+\.\d+\.\d+-\d+/\d+)-', value)
    if match:
        extracted = match.group(1)
        # Remove the dots between the first three numbers
        transformed = re.sub(r'(?<=\d)\.(?=\d)', '', extracted, count=2)
        return transformed
    return None  # Return None if the pattern does not match

# %%

df['SUBCLASS'] = df.CNAE_ATIVIDADE_PRINCIPAL.apply(transform_value)
#%%
df = pd.merge(df, dfcnae, on='SUBCLASS', how='left')

#%%
df["DATA_EMISSAO"] = df["DATA_EMISSAO"].astype("datetime64[ms]")
df["INICIO_ATIVIDADE"] = df["INICIO_ATIVIDADE"].astype("datetime64[ms]")
df["REFERENCIA_max"] = df["REFERENCIA_max"].astype("datetime64[ms]")
df["REFERENCIA_min"] = df["REFERENCIA_min"].astype("datetime64[ms]")
df["DATA_EXPIRACAO"] = df["DATA_EXPIRACAO"].astype("datetime64[ms]")


#%%
# cria um backup do arquivo com a geo localizacao dos enderecos
now = datetime.strftime(datetime.today(), f'%Y-%m-%d-%H_%M_%S')
backup_parquet = dataset_home + f"base_alvaras_curitiba_{now}.parquet"
os.rename(dataset_home+'base_alvaras_curitiba.parquet', backup_parquet)
#%%
df.to_parquet(dataset_home+'base_alvaras_curitiba.parquet')

df.to_csv(staging_data_home+'stages/base_alvaras_stage05.csv', sep=';', encoding='utf-8', index=False)
#%%
