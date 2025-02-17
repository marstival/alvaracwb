
# %%
import pandas as pd
#import awswrangler as wr
import ast
from dash_app import app, cache, dash, data_home, logging, dlm
import time
import re
from redlock import MultipleRedlockException
# %%


def month_diff(a, b):
    return 12 * (a.year - b.year) + (a.month - b.month)


def split(x):
    return x.left


def get_tempo_atividade_agg(filtro, value=None):
    key = 'tempo_ativ'+str(filtro)+str(value)
    g = cache.get(key)

    if (g is None):
        df = get_dados_alvara(filtro, value)
        df['tempo_intervals'] = pd.cut(df.TEMPO_ATIVIDADE, bins=60)

        g = df.groupby('tempo_intervals')[['tempo_intervals']].count()
        g = g.reset_index()
        g['ind'] = g.index.apply(split, axis=1)
        g = g.rename(columns={'tempo_intervals': 'COUNT'})
        cache.set(key, g, timeout=0 if (value is None) else 200)
    return g


def get_overview_data(filtro, value=None):
    start = time.time()
    logging.info("func get_overview_data")

    key = 'summary_'+str(filtro)+str(value)
    dparam = cache.get(key)
    if (dparam is None):
        logging.info('get_overview_data cache MISS')
        df = get_dados_alvara(
            filtro=filtro, value=value)[['REFERENCIA_max', 'REFERENCIA_min', 'TEMPO_ATIVIDADE', 'ATIVO']]
        df_ativos = df[df.ATIVO]
        total_ativos = df_ativos.index.size

        idade_media = round(
            df_ativos.TEMPO_ATIVIDADE.mean(), 2)  # meses para ano

        quantiles = df_ativos.TEMPO_ATIVIDADE.quantile(
            [0.25, 0.5, 0.75]).to_list()

        total_recentes = df_ativos[df_ativos.TEMPO_ATIVIDADE <=
                                   42].TEMPO_ATIVIDADE.size
        pct_recentes = total_recentes / total_ativos

        dt_atual = df.REFERENCIA_max.max()

        encerrados12 = df[~df.ATIVO & (df.REFERENCIA_max >= (
            dt_atual - pd.DateOffset(months=12)))].REFERENCIA_max.size

        abertos12 = df[
            (df.REFERENCIA_min >= (dt_atual - pd.DateOffset(months=12)))
        ].REFERENCIA_max.size

        dparam = pd.DataFrame([[total_ativos, idade_media, quantiles, total_recentes, pct_recentes, dt_atual, encerrados12, abertos12]],
                              columns=['total_ativos', 'idade_media', 'quantiles', 'total_recentes', 'pct_recentes', 'dt_atual', 'encerrados12', 'abertos12'])

        cache.set(key, dparam, timeout=0 if (value is None) else 200)

    logging.info("func get_overview_data %d" % (time.time()-start))
    return dparam.iloc[0]


def get_top_empresas(filtro, value=None):
    key = 'top_emp'+str(filtro)+str(value)
    g = cache.get(key)

    if (g is None):
        df = get_dados_alvara(filtro, value)
        g = df.groupby(['CD_NOME_EMPRESARIAL', 'CNAE_ATIVIDADE_PRINCIPAL']
                       ).agg({'ENDERECO': 'count', 'NOME_EMPRESARIAL': 'first', 'CNAE_ATIVIDADE_PRINCIPAL': 'first', 'ATIVIDADE_PRINCIPAL': 'first'})[['NOME_EMPRESARIAL', 'CNAE_ATIVIDADE_PRINCIPAL', 'ATIVIDADE_PRINCIPAL', 'ENDERECO']].rename(
            columns={'ENDERECO': 'COUNT'}).sort_values(by='COUNT', ascending=False)[0:30]

        g.index = [i[0] for i in g.index]
        cache.set(key, g, timeout=0 if (value is None) else 200)
    return g


def get_top_empresas_alvaras(filtro, value=None):
    key = 'top_emp_alvaras'+str(filtro)+str(value)
    dfe = cache.get(key)
    if (dfe is None):
        g = get_top_empresas(filtro, value)
        dfe = get_dados_alvara(filtro, value)
        dfe = dfe[dfe.CD_NOME_EMPRESARIAL.isin(g.index)]
        cache.set(key, dfe, timeout=0 if (value is None) else 200)
    return dfe


def get_dados_alvara_all():
    home = data_home
    key = 'alvara_all'
       
    df = cache.get(key)

    if (df is not None):
        return df
    try:
        ex = 300 # tempo para expirar o lock segundos
        t = 5 #tempo de espera até nova tentativa
        lock_resource = 'get_alvaras_lock'
        data_lock = dlm.lock(lock_resource, ex * 1000) #milisec
        trials = 0
        while (data_lock == False):
            trials = trials+1
            time.sleep(t)
            df = cache.get(key)
            if (df is not None):
                return df
            else:
                if (trials > (ex/t) ):
                    #se passou do limite de tolerancia, tenta pegar o lock
                    # se conseguir, segue para carga dos dados
                    # se nao conseguir, pode ser que outro processo na fila conseguiu
                    #    e neste segundo caso volta para o loop, tenta cache.get ... mas sem reiniciar trails.
                    data_lock = dlm.lock(lock_resource, ex * 1000)
        
        start_time = time.time()
        logging.info(f"get_dados_alvara_all cache MISS trials {trials}")
        df = pd.read_parquet(home+'base_alvaras_curitiba.parquet')

        df['CD_NOME_EMPRESARIAL'] = df['NOME_EMPRESARIAL'].apply(hash)

        df['point'] = df[['point']].apply(lambda x: ast.literal_eval(
            x.point) if (x.point != None) else None, axis=1)  # meta='tuple',

        df = df.reset_index(drop=True)

        logging.info("get_dados_alvara_all %s" % (time.time() - start_time))

        cache.set(key, df)

    except MultipleRedlockException as re:
        logging.error(f"get_dados_alvara_all Exception MultipleRedlockException {re}")
        raise MultipleRedlockException(re)
    except Exception as e:
        logging.error(f"get_dados_alvara_all Exception MultipleRedlockException {e}")
        raise Exception(e)
    finally:
        if (data_lock):
            dlm.unlock(data_lock)    

    logging.error(f"return get_dados_alvara_all")    
    
    return df


def get_dados_alvara(filtro, value=None):
    '''
    Args: 
    - filtro: 'all' ou 'ativo'
    - value: [] com os codigos de atividade_principal para filtrar do dataset
    '''
    start = time.time()

    key = 'alvaras_filtro'+str(filtro)+str(value)
    if (value is not None):
        # faz cache do resultado quando aplicado o filtro por atividade
        df = cache.get(key)
        if (df is not None):
            return df

    df = get_dados_alvara_all()
    logging.info(f"get_dados_alvara get all ok {time.time()-start}")
    start = time.time()

    if (filtro == 'ativo'):
        df = df[df.ATIVO]

    logging.info(f"get_dados_alvara ativo filtered {time.time()-start}")
    start = time.time()

    # faz cache do resultado quando aplicado o filtro por atividade
    if ((value is not None) and (len(value) > 0)):
        logging.info(f"get_dados_alvara value not none")
        df = df[df.CNAE_ATIVIDADE_PRINCIPAL.isin(value)]
        cache.set(key, df, timeout=300) 

    logging.info(f"return get_dados_alvara  {time.time()-start}")

    return df


def get_dados_consolidado(filtro, value=None):

    key = 'consolidado_'+str(filtro)+str(value)
    dfc = cache.get(key)
    if (dfc is not None):
        return dfc

    df = get_dados_alvara(filtro, value)

    end = df.REFERENCIA_max.max()
    start = df.REFERENCIA_min.min()
    meses = pd.date_range(start=start, end=end, freq='MS')

    ativos_d0 = df[(df.REFERENCIA_max >= start) & (
        df.REFERENCIA_min <= start)].index.size

    dn = df.groupby(['REFERENCIA_min'])[['REFERENCIA_min']].count()
    dn = dn.reindex(meses).fillna(0).astype(
        int).rename(columns={'REFERENCIA_min': 'NOVOS'})
    dn.loc[start] = 0

    de = df[(~ df.ATIVO)].groupby(df.REFERENCIA_max +
                                  pd.DateOffset(months=1))[['REFERENCIA_max']].count()
    de = de.reindex(meses).fillna(0).astype(int).rename(
        columns={'REFERENCIA_max': 'ENCERRADOS'})

    dfc = dn.merge(de, left_index=True, right_index=True)
    dfc['ACUMULADO'] = ((dn.NOVOS - de.ENCERRADOS)).cumsum() + ativos_d0

    cache.set(key, dfc, timeout=0 if value is None else 200)

    return dfc


def get_ramos_atividade(f='ramos_atividade'):
    dict_ramos = cache.get('ramos_atividade')
    if (dict_ramos is None):
        home = data_home
        ramos = pd.read_parquet(home+'alvaras_ramos_atividade.parquet')
        logging.info("Ramos distintos %d" % ramos.index.size)
        ramos = ramos.set_index('CNAE_ATIVIDADE_PRINCIPAL')

        dict_ramos = [{'label': ramos.loc[i]['ATIVIDADE_PRINCIPAL'],
                       'value': str(i)} for i in ramos.index]

        cache.set('ramos_atividade', dict_ramos)

    return dict_ramos


# %%

