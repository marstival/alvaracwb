#%%
import config
import pandas as pd

dataset_home = config.get_existing_data_home()

stagedir = config.get_data_home()
local = stagedir + 'cnae/'


#%%
df = pd.read_excel(stagedir + 'cnae/CNAE_Subclasses_2_3_Estrutura_Detalhada.xlsx',engine = 'openpyxl',
                    dtype={'GROUP':'str','DIVISION':'str','CLASS':'str', 'SUBCLASS':'str'})
df = df.drop('Unnamed: 6',axis=1)
df = df.rename(columns={'DESCRIPTION':'SUBCLASS_DESC'})
#%%

df.SUBCLASS_DESC = df.SUBCLASS_DESC.str.replace(';',',')

dfsub = df[df.SUBCLASS.isna() == False].copy()

# %%
classe = dfsub['SUBCLASS'].astype(object).str[0:-3]
dfsub['CLASS'] = classe.str[0:2]+'.'+classe.str[2:6]
dfsub['CLASS_DESC'] = dfsub.CLASS.apply(lambda x: df[df.CLASS == x]['SUBCLASS_DESC'].values[0] )

#%%
dfsub['GROUP'] = dfsub['CLASS'].astype(object).str[0:4]
dfsub['GROUP_DESC'] = dfsub.GROUP.apply(lambda x: df[df.GROUP == x]['SUBCLASS_DESC'].values[0] )

#%%
dfsub['DIVISION'] = dfsub['GROUP'].astype(object).str[0:2].astype(object)
#%%
dfsub['DIVISION_DESC'] = dfsub.DIVISION.apply(lambda x: df[df.DIVISION == x]['SUBCLASS_DESC'].values[0] )

dsec = df[df['SECTION'].isna() == False]
# %%
n = dsec.index.size
for i in range(0,n):
    inicio = dsec.index[i]
    fim = dsec.index[i+1] if i < (n-1) else None
    dfsub.loc[inicio:fim,'SECTION'] = df.loc[inicio]['SECTION']
# %%

dfsub.to_csv(stagedir + 'cnae/CNAE_Subclasses_2_3_tabular.csv', sep=';',encoding='latin1')
dfsub.to_parquet(stagedir + 'cnae/CNAE_Subclasses_2_3_tabular.parquet')