#%%
import pandas as pd

columns = ['NOME_EMPRESARIAL','INICIO_ATIVIDADE','NUMERO_DO_ALVARA','NOME_FANTASIA','DATA_EMISSAO','DATA_EXPIRACAO','ENDERECO','NUMERO','UNIDADE','ANDAR','COMPLEMENTO','BAIRRO','CEP','CNAE_ATIVIDADE_PRINCIPAL','ATIVIDADE_PRINCIPAL']


#%%
# Load the parquet file into a pandas DataFrame
file_path = '/home/stival/projetos/alvaracwb/dataset/base_alvaras_curitiba.parquet'
dfgeral = pd.read_parquet(file_path)
#/home/stival/projetos/alvaracwb/staging/stages/2024-12-01_Alvaras-Base_de_Dados.parquet

#%%
# Print the first 5 lines of the DataFrame

#dfgeral.columns
# %%
file_path = '~/projetos/alvaras/data_staging/download/2024-12-01_Alvaras-Base_de_Dados.csv'
dfatual = pd.read_csv(file_path, sep=';', na_values=['***','**', '*'], 
                     keep_default_na=True,
                     usecols=columns, encoding='latin1', index_col=False, dayfirst=True, infer_datetime_format=True, parse_dates=['INICIO_ATIVIDADE','DATA_EMISSAO','DATA_EXPIRACAO'])
dfatual.columns
# %%
dfatual[dfatual.NOME_EMPRESARIAL.str.contains('Bradesco', case=False)].count()
#%%
dfgeral[dfgeral.NOME_EMPRESARIAL.str.contains('Bradesco', case=False) & dfgeral.ATIVO].count()

# %%
dfatual[dfatual.NOME_EMPRESARIAL.str.contains('Bradesco', case=False) & ~ dfatual.NUMERO_DO_ALVARA.isin(dfgeral.NUMERO_DO_ALVARA)].head()
# %%
dfgeral[dfgeral.NUMERO_DO_ALVARA=='1355921']
# %%


# Load the parquet file into a pandas DataFrame
file_path = '/home/stival/projetos/alvaracwb/staging/stages/2024-12-01_Alvaras-Base_de_Dados.parquet'
df = pd.read_parquet(file_path)

# %%
df[df.NUMERO_DO_ALVARA=='1355921']
#df[df.NOME_EMPRESARIAL.str.contains('Bradesco', case=False)].count()

# %%
dfatual[dfatual.NUMERO_DO_ALVARA==1355921]

# %%
dfatual[dfatual.NOME_EMPRESARIAL.str.contains('Bradesco', case=False) & ~(dfatual.NOME_EMPRESARIAL == 'BANCO BRADESCO S.A.')].count()

# %%

def convert_to_int(value) -> str:
    try:
        # Check if the value is a float and convert to int
        if (value == 'S/N' or value == 'SN' or value == 'NA' or value == 'N/A' or pd.isna(value)):
            return ""
        return str(int(float(value)))
    except ValueError:
        # If conversion fails, return the original value
        return value
#%%
# Apply the custom function to the NUMERO column
dfgeral['NUMERO'] = dfgeral['NUMERO'].apply(convert_to_int)

# Check the result
print(dfgeral.NUMERO)
# %%
dfgeral[(dfgeral.NUMERO != 'S/N') & (dfgeral.NUMERO != 'SN')].NUMERO.astype(int)
# %%
# %%
dfgeral[dfgeral.NOME_EMPRESARIAL.str.contains('Bradesco', case=False) & ~(dfgeral.NOME_EMPRESARIAL == 'BANCO BRADESCO S.A.')]
# %%
df = dfgeral.groupby(['NUMERO_DO_ALVARA']).size().sort_values()
# %%
df
# %%
dfgeral[dfgeral.NUMERO_DO_ALVARA == '105'][['NUMERO_DO_ALVARA','ENDERECO','NUMERO','BAIRRO','CEP','NOME_EMPRESARIAL','DATA_EMISSAO','DATA_EXPIRACAO','INICIO_ATIVIDADE','ATIVO']]
# %%
dfgeral[dfgeral.DATA_EMISSAO.isnull()].count()
# %%
file_path = '/home/stival/projetos/alvaracwb/staging/stages/base_alvaras_stage02.parquet'
df2 = pd.read_parquet(file_path)
#%%
df2.index.size
# %%
dfgeral.index.size
# %%
df2[(df2.INICIO_ATIVIDADE == '1900-01-01') & (df2.DATA_EMISSAO == '1900-01-01')].count()


# %%
# %%
dfatual['CEP'] = dfatual.CEP.apply(convert_to_int).astype(str)

# %%
dfatual.dtypes
# %%
dfatual.CEP.astype(int)
# %%
