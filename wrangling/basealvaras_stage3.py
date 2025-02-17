# %%
import pandas as pd
import numpy
#import pycep_correios
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
from tqdm import tqdm
import re
from datetime import datetime
import config
import os
# %%
data_home = config.get_data_home()
#dataset_dir = config.get_existing_data_home()
local = data_home + 'geo/'
stagedir = data_home + 'stages/'
# %%
do = pd.read_parquet(local + 'enderecos_geocoded.parquet')

do = do.loc[lambda x: (pd.isna(x['ENDERECO']) == False)
            & (x['ENDERECO'] != 'NÃO CONSTA')]
# %%

df = pd.read_parquet(
    stagedir + 'base_alvaras_stage02.parquet')
print("stage2 total  %s" % df.index.size)


df = df[['ENDERECO', 'NUMERO', 'BAIRRO']]

#%%

df = df.reset_index(drop=True)

df = df.loc[lambda x: (pd.isna(x['ENDERECO']) == False)
            & (x['ENDERECO'] != 'NÃO CONSTA')]

df = df[['ENDERECO', 'NUMERO', 'BAIRRO']].drop_duplicates()

df = df.set_index(['ENDERECO', 'NUMERO', 'BAIRRO'])
do = do.set_index(['ENDERECO', 'NUMERO', 'BAIRRO'])

print("geocode removing duplicates %s" % df.index.size)

# %%

df = pd.merge(df, do, left_index=True, right_index=True, how='outer',
              indicator=True)  # .loc[lambda x : x['_merge']!='right_only']
df = df.reset_index()

# se nenhum endereco novo no stage02 .. termina
if (df[df._merge == 'left_only'].index.size < 1):
    print("Nenhum endereco novo no arquivo stage02, que nao tivesse ja sido geo localizado... terminando script!")
    raise Exception(
        "Nenhum novo endereco encontrado, que nao tenha sido geo localizado anteriormente.")


# se left_only, significa que é um endereco que nao passou pela geo localizacao
# se nao eh left_only, ja foi tentado localizar
mask_geocoded = (df._merge != 'left_only')
dslice = df[mask_geocoded]

print("Registros com enderecos ja incluidos no arquivo de geo localizacao  %s" %
      dslice.index.size)

dslice['location'] = dslice.location.apply(lambda x: pd.NA if pd.isna(x) else str(x))
dslice['point'] = dslice.point.apply(lambda x: pd.NA if pd.isna(x) else str(x))

# %%
dslice[
    ['ENDERECO', 'NUMERO', 'BAIRRO', 'address', 'location', 'point']
].to_parquet(local+'enderecos_part0.parquet')

# %%
# todos que nao tiveram geolocalizacao encontrada
df = df[~ mask_geocoded]

print("Registros com geo localizacao ainda sem tentativa de geo localizar  %s" % df.index.size)

# %%


def to_address(x):
    r = x[0]
    # elimina sufixo na designacao do endereco no caso desta avenida (LD, LE, EC)
    # a api de localizacao nao encontra a coordenada quando termina em LD
    if (r.startswith('AV. JUSCELINO KUBITSCHEK DE OLIVEIRA')):
        r = 'AV. JUSCELINO KUBITSCHEK DE OLIVEIRA'
    # para a API de localizacao geo funciona melhor com os nomes por extenso..
    r = re.sub(r'^[Rr]\. ', 'Rua ', r)
    r = re.sub(r'^[Aa][Ll]\. ', 'Alameda ', r)
    r = re.sub(r'^[Tt][Vv]\. ', 'Travessa ', r)
    r = re.sub(r'^[Aa][Vv]\. ', 'Avenida ', r)
    r = re.sub(r'^[Pp][Cc]\. ', 'Praca ', r)
    r = re.sub(r'^[Rr][Oo][Dd]\. ', 'Rodovia ', r)
    r = re.sub(r'^[Ee][Ss][Tt]\. ', 'Estrada ', r)
    r = re.sub(r'BR CENTO E DEZESSEIS', 'BR 116', r)

    # alguns bairros nao batem com a base de enderecos do geopy... e não retorna a localização
    # pode rodar uma vez para refinar sem passar o bairro, mas na rodada inicial mantendo o bairro.
    c = '' if (pd.isna(x[2])) else x[2]
    #c = ''

    try:
        r = {'street': r + ", " + str(int(x[1])),
             'county': c,
             'city': 'Curitiba',
             'state': 'PR'
             }
    except:
        r = {'street': r,
             'county': c,
             'city': 'Curitiba',
             'state': 'PR'
             }

    return r


# %%
# address é um dict, entao precisa estar como objeto para a funcao geocode funcionar logo abaixo...
df['address'] = df[['ENDERECO', 'NUMERO', 'BAIRRO']].apply(
    to_address, axis=1).astype(object)

# %%
geolocator = Nominatim(user_agent="Alvara3")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1/20)
# %%

s = int(df.index.size)

if (s > 1000):
    a = [0, int(s*0.35), int(s*0.75), int(s)]
    chunks = [0, 1, 2]
else:
    a = [0, s]
    chunks = [0]

# %%
for i in chunks:

    print("%d : %d" % (a[i], a[i+1]))
    tqdm.pandas()
    dslice = df[a[i]:a[i+1]]
    # Cria a coluna location com o local retornado a partir do endereço
    # confirme que 'address'seja um objeto dict (e nao uma string). use eval() se necessario converter
    dslice['location'] = dslice['address'].progress_apply(geocode)

    # Seleciona a latitude e longitude que está dentro do local
    dslice['point'] = dslice['location'].apply(
        lambda loc: tuple(loc.point) if loc else pd.NA)

    dslice['location'] = dslice.location.apply(
        lambda x: pd.NA if pd.isna(x) else str(x))
    dslice['point'] = dslice.point.apply(
        lambda x: pd.NA if pd.isna(x) else str(x))
    #dslice = dslice.set_index(['ENDERECO','NUMERO','BAIRRO'])

    dslice['address'] = dslice.address.astype(str)
    dslice[
        ['ENDERECO', 'NUMERO', 'BAIRRO', 'address', 'location', 'point']
    ].to_parquet(local+'enderecos_part%s.parquet' % (i+1))

    time.sleep(30)
    print("Finished %d" % (i+1))
print("Finished")

# %%


# %%
files = [local+'enderecos_part%d.parquet' % i for i in range(0, len(chunks)+1)]
# %%
'''df = pd.read_parquet(files[0])
for f in files[1:]:
    d = pd.read_parquet(f)
    df = df.append(d)'''

# Load all files and concatenate them into a single DataFrame
df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)


# %%
mask = (df.location.isna() == False) & (
    df.location.str.contains('Curitiba') == False)
print(
    f"total erroneamente fora de curitiba {sum(mask)} e portanto atribuido pd.NA")
df.loc[mask, 'location'] = pd.NA
df.loc[mask, 'point'] = pd.NA

# %%
# cria um backup do arquivo com a geo localizacao dos enderecos
now = datetime.strftime(datetime.today(), f'%Y-%m-%d-%H_%M_%S')
backup_parquet = local + f"enderecos_geocoded_{now}.parquet"
os.rename(local+'enderecos_geocoded.parquet', backup_parquet)

df['address'] = df.address.astype(str)
df[
    ['ENDERECO', 'NUMERO', 'BAIRRO', 'address', 'location', 'point']
].to_parquet(local+'enderecos_geocoded.parquet')

print("Finalizado geocode")

# %%
print(
    f"Geo localizacao adicionada ao arquivo. {df[df.point.isna()==False].index.size} registros geo localizados, e {df[df.point.isna()].index.size} enderecos com geo localizacao nao encontrada.")
# %%
# remove arquivos intermediarios
for f in files:
    os.remove(f)
# %%
