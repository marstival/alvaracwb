#%%
import pandas as pd
import numpy as np
#import pycep_correios

import config

#%%
data_home = config.get_data_home()
local = data_home + 'stages/'

#%%
df = pd.read_parquet(local+'base_alvaras_stage04.parquet')
#%%

# %%
key_columns = [ 'NOME_EMPRESARIAL',  'ENDERECO' , 'NUMERO','CNAE_ATIVIDADE_PRINCIPAL' ]

other_cols  = ['NOME_FANTASIA', 
       'UNIDADE', 'ANDAR', 'COMPLEMENTO', 'BAIRRO',
       'CEP', 'address', 'location','point'  ,'ATIVIDADE_PRINCIPAL','NUMERO_DO_ALVARA' ]



#alvara_cols = ['NUMERO_DO_ALVARA', 'DATA_EXPIRACAO', 'DATA_EMISSAO']

funcs = dict(zip(other_cols, ['last']*len(other_cols)))
funcs.update( {'INICIO_ATIVIDADE':'min','DATA_EXPIRACAO':'max','DATA_EMISSAO':'min', 'REFERENCIA_min':'min', 'REFERENCIA_max':'max'} )

g3 = df.groupby(key_columns).agg(funcs)
#g3.columns = ['_'.join(col).strip() for col in g3.columns.values]
g3 = g3.rename(columns=dict(zip(g3.columns, g3.columns.str.replace('_last',''))))

m = g3.REFERENCIA_max.max()

g3['ATIVO'] = (g3.REFERENCIA_max == m).astype(object)
#%%
g3 = g3.reset_index()
g3.index = g3.index.astype('int64')
#%%

#### V9
def month_diff(a, b):
    return 12 * (a.year - b.year) + (a.month - b.month)
    

g3 = g3.dropna(subset=['INICIO_ATIVIDADE','DATA_EMISSAO'],how='all')
g3 = g3.loc[lambda x: ~ (
        (x['INICIO_ATIVIDADE'] == '1900-01-01') &
        (x['DATA_EMISSAO'] == '1900-01-01')
    )
    ]

g3['INICIO_ATIVIDADE'] = g3.apply(lambda x: x['INICIO_ATIVIDADE'] if (x['INICIO_ATIVIDADE'] > pd.to_datetime('1900-01-01')) else x['DATA_EMISSAO'], axis=1)

g3['TEMPO_ATIVIDADE'] = g3.apply( lambda x: month_diff(x.REFERENCIA_max , x.INICIO_ATIVIDADE) if (x.REFERENCIA_max > x.INICIO_ATIVIDADE) else 0 ,axis=1 )

#%%

g3.to_parquet(local+'base_alvaras_stage05.parquet')

g3.to_csv(local+'base_alvaras_stage05.csv', sep=';', encoding='utf-8', index=False)