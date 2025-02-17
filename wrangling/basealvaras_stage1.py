import pandas as pd
import datetime as dt
import re
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import os
import logging
import numpy as np
import unicodedata
#%%

origem = config.get_data_home() + 'download/'
local = config.get_data_home() + 'stages/'

def convert_to_int(value) -> str:
    try:
        # Check if the value is a float and convert to int
        if (pd.isna(value) or (value == 'S/N') or (value == 'SN') or (value == 'NA') or (value == 'N/A')):
            return ""
        return str(int(float(value)))
    except ValueError:
        # If conversion fails, return the original value
        return value


def remove_suffix(text: str) -> str:
    if not isinstance(text, str):
        return text  # Return the value unchanged if it's not a string
    patterns = [
        r"s[\s\./]*a[\s\./]*$",  # Matches variations of "S/A", "S.A.", "S / A", etc.
        r'[ ]*[-]?[ ]*[Mm][Ee][\.]?$',  # Matches variations of "ME", "ME.", "ME -", etc.
        r'[ ]*[-]?[ ]*[Ee][Pp][Pp][\.]?$',  # Matches variations of "EPP", "EPP.", "EPP -", etc. 
        r"[\s\-]*L[\s]*T[\s]*D[\s]*A[\s\.]*$" # Matches variations of "LTDA", "LTDA.", "LTDA -", etc.
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "S.A.", text, flags=re.IGNORECASE).strip()
    
    return text

def remove_accents(text: str) -> str:
    if not isinstance(text, str):
        return text  # Return the value unchanged if it's not a string
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

files = config.arquivos_to_append

columns = ['NOME_EMPRESARIAL', 'INICIO_ATIVIDADE','NUMERO_DO_ALVARA','NOME_FANTASIA', 
       'DATA_EMISSAO', 'DATA_EXPIRACAO',
       'ENDERECO', 'NUMERO', 'UNIDADE', 'ANDAR', 'COMPLEMENTO', 'BAIRRO',
       'CEP',  'CNAE_ATIVIDADE_PRINCIPAL','ATIVIDADE_PRINCIPAL' ]


for f in files:
    logging.info(f)

    base, ext = os.path.splitext(f)
    target_file = local + base + '.parquet'
    if (os.path.exists(target_file) ):
        print("SKIPPING file already processed: ", target_file)
        logging.warning("SKIPPING file already processed: %s"%target_file)
        continue


    df = pd.read_csv(origem + f, sep=';', encoding='latin1', dayfirst=True, 
                     na_values=['***','**', '*'], 
                     keep_default_na=True,
                     parse_dates=['DATA_EXPIRACAO', 'DATA_EMISSAO', 'INICIO_ATIVIDADE'],
                     usecols=columns)
    
    df['NOME_EMPRESARIAL'] = df['NOME_EMPRESARIAL'].apply(remove_suffix)
    df['NOME_EMPRESARIAL'] = df['NOME_EMPRESARIAL'].apply(remove_accents)

    df['NOME_FANTASIA'] = df['NOME_FANTASIA'].apply(remove_suffix)
    df['NOME_FANTASIA'] = df['NOME_FANTASIA'].apply(remove_accents)

    df['NOME_FANTASIA'] = df['NOME_FANTASIA'].fillna(df['NOME_EMPRESARIAL'])

    df['DATA_EXPIRACAO'] = pd.to_datetime(df['DATA_EXPIRACAO'], dayfirst=True, errors='coerce')
    df['DATA_EMISSAO'] = pd.to_datetime(df['DATA_EMISSAO'],  dayfirst=True, errors='coerce')
    df['INICIO_ATIVIDADE'] = pd.to_datetime(df['INICIO_ATIVIDADE'], dayfirst=True, errors='coerce')

    date_match = re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', f)
    if date_match:
        df['REFERENCIA'] = dt.datetime.strptime(date_match[0], '%Y-%m-%d')
    else:
        df['REFERENCIA'] = pd.NaT  # or any other default value
    
    
    # Apply the custom function to the NUMERO column
    df['NUMERO'] = df['NUMERO'].apply(convert_to_int).astype(str)


    df['NUMERO_DO_ALVARA'] = df.NUMERO_DO_ALVARA.fillna("").astype(str)
    df['CEP'] = df.CEP.apply(convert_to_int).astype(str)

    df = df.reset_index(drop=True)
    df.index = df.index.astype('int64')

    
    
    df.to_parquet(target_file) 

    