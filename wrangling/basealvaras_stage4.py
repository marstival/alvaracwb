#%%
# Aplica a geo localizacao nos enderecos da base de alvaras
import pandas as pd
import numpy
#import pycep_correios
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
from tqdm import tqdm
import re
import config

data_home = config.get_data_home()
local = data_home + 'stages/'
#dataset_dir = config.get_existing_data_home()
#arquivo com a geo localizacao para cada endereco do dataset
geo_codes = data_home + 'geo/enderecos_geocoded.parquet'
geo = pd.read_parquet(geo_codes)


geo = geo.set_index(['ENDERECO','NUMERO','BAIRRO'])
geo = pd.read_parquet(geo_codes)
geo = geo.set_index(['ENDERECO', 'NUMERO', 'BAIRRO'])

df = pd.read_parquet(local+'base_alvaras_stage02.parquet')

print ("stage2 total records  %s"%df.index.size)
def lookup(x):
    try:
        if (pd.isna(x.ENDERECO) | (x.ENDERECO == 'NÃO CONSTA')):
            return [pd.NA, pd.NA, pd.NA]
        if (pd.isna(x.BAIRRO)):
            r = geo.loc[(x.ENDERECO, x.NUMERO,)].iloc[0]
        else:    
            r = geo.loc[(x.ENDERECO, x.NUMERO, x.BAIRRO)]
        return [r.address, r.location, r.point]
    except KeyError:
        print("geo not found %s %s %s"%(x.ENDERECO, x.NUMERO, x.BAIRRO))
        return [pd.NA, pd.NA, pd.NA]

df[['address','location','point']] = df.apply(lookup, result_type='expand',axis=1)

num_missing = df['point'].isna().sum()

# Print the result
print(f"Numero de Enderecos com geo localizacao NAO encontrada: {num_missing}")

df = df.reset_index(drop=True)
df.index = df.index.astype('int64')

df.to_parquet(local+'base_alvaras_stage04.parquet')

df.to_csv(local+'base_alvaras_stage04.csv', sep=';', encoding='utf-8', index=False)