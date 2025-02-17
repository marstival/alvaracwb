import pandas as pd
import datetime as dt
import re
import config
import dask.dataframe as dd
from dask.distributed import Client, progress, LocalCluster
import time
import gc
import config
import logging
import sys
#from dask.dataframe import concat

data_home = config.get_data_home()
local = data_home + 'stages/'


def month_diff(a, b):
    return 12 * (a.year - b.year) + (a.month - b.month)


csvfiles = config.arquivos_to_append

#files = [local + 'base_alvaras_stage01b.parquet']
files = [local + re.sub(r'(?i)csv', 'parquet', f) for f  in csvfiles]

cluster = LocalCluster(processes=False, threads_per_worker=2,n_workers=1, memory_limit='12GB') 
client=Client(cluster)
print(client)
#%%
df = dd.read_parquet( files)

key_columns = [ 'NUMERO_DO_ALVARA',
    'NOME_EMPRESARIAL','DATA_EMISSAO'  ]

other_cols  = ['INICIO_ATIVIDADE','NOME_FANTASIA','ENDERECO' , 'NUMERO', 
       'UNIDADE', 'ANDAR', 'COMPLEMENTO', 'BAIRRO',
       'CEP',  'CNAE_ATIVIDADE_PRINCIPAL','ATIVIDADE_PRINCIPAL' ]


funcs = dict(zip(other_cols, ['last'] * len(other_cols)))
funcs.update({
    'INICIO_ATIVIDADE': 'min',
    'REFERENCIA': ['max', 'min'],
    'DATA_EXPIRACAO': 'max',
    #'DATA_EMISSAO': 'min'
})

# Perform the groupby with aggregation
df = df.groupby(key_columns).agg(funcs, split_out=16)

# Flatten MultiIndex columns
df.columns = ['_'.join(col).strip() for col in df.columns.values]

# Rename columns for clarity
df = df.rename(columns=dict(zip([f + '_last' for f in other_cols], other_cols)))
df = df.rename(columns={
    'INICIO_ATIVIDADE_min': 'INICIO_ATIVIDADE',
    'DATA_EXPIRACAO_max': 'DATA_EXPIRACAO',
    #'DATA_EMISSAO_min': 'DATA_EMISSAO'
})

m = df.REFERENCIA_max.max()

df['ATIVO'] = (df.REFERENCIA_max == m).astype(bool)
#%%

# Reset index and convert to int64
df = df.reset_index()
try:
    df.index = df.index.astype('int64')
except Exception as e:
    print(f"Index conversion failed: {e}")

df = df.dropna(subset=['INICIO_ATIVIDADE','DATA_EMISSAO'],how='all')

df = df.loc[lambda x: ~ (
        (x['INICIO_ATIVIDADE'] == '1900-01-01') &
        (x['DATA_EMISSAO'] == '1900-01-01')
    )
    ]

df['INICIO_ATIVIDADE'] = df.apply(lambda x: x['INICIO_ATIVIDADE'] if (x['INICIO_ATIVIDADE'] > pd.to_datetime('1900-01-01')) else x['DATA_EMISSAO'], meta=(None, 'datetime64[ns]'), axis=1)

df['TEMPO_ATIVIDADE'] = df.apply( lambda x: month_diff(x.REFERENCIA_max , x.INICIO_ATIVIDADE) if (x.REFERENCIA_max > x.INICIO_ATIVIDADE) else 0, meta=(None, 'int64') ,axis=1 )

# Persist the DataFrame
#df = client.persist(df)

# Save to Parquet
df.to_parquet(local + 'base_alvaras_stage02.parquet')


#%%
cluster.close()
client.close()