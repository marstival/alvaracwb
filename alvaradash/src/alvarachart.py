
# %%
import pandas as pd
import pandas as pd
import plotly as ply
from plotly import express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from turfpy.transformation import convex
from geojson import FeatureCollection, Feature, Point

from dash_app import cache
import time
import logging

import alvaradata
# %%


def get_top_filiais(g):
        
    fig = px.bar(g.sort_values(by='COUNT'),  
                x='COUNT',y='NOME_EMPRESARIAL', 
                hover_data = ['ATIVIDADE_PRINCIPAL'],
                orientation='h',
                 title='Empresas com maior número de alvarás',
                 color='ATIVIDADE_PRINCIPAL',
                 text='COUNT',
                 )
    
    fig.update_layout(barmode='stack', xaxis={
                      'title': '# alvarás ativos'},
                    yaxis_title=None,
                    font_color='midnightblue',
                    height=700,
                    hoverlabel=dict(
                        bgcolor="white",
                    ),
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False
                )

    return fig


@cache.memoize(timeout=120)
def get_consolidado(filtro, value=None, freq=None, inicio=None):
    dfc = alvaradata.get_dados_consolidado(filtro, value=value)
    # freq = AS, QS,
    # inicio = data a partir da qual plotar o grafico (usar inicio do quarter)

    if (inicio != None):
        inicio_filtro = pd.to_datetime(inicio)  
        dfc = dfc[dfc.index >= inicio_filtro]

    if (freq != None):
        dfc = dfc.resample(freq, convention='start').agg(
            {'NOVOS': 'sum', 'ENCERRADOS': 'sum', 'ACUMULADO': 'max'})

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=dfc.index, y=dfc.ACUMULADO,
                             marker_color='firebrick',
                             name='Alvarás Ativos',
                             text=dfc.ACUMULADO,
                             textposition='top center'
                             ),
                  secondary_y=True)

    fig.add_trace(go.Bar(x=dfc.index, y=dfc.ENCERRADOS,
                         base=-1*dfc.ENCERRADOS,
                         marker_color='lightcoral',
                         name='Encerrados',
                         text=dfc.ENCERRADOS,
                         textposition='inside'
                         ), secondary_y=False)
    fig.add_trace(go.Bar(x=dfc.index, y=dfc.NOVOS,
                         base=0,
                         marker_color='slateblue',
                         name='Novos',
                         text=dfc.NOVOS,
                         textposition='auto'
                         ), secondary_y=False)
    

    fig.update_layout(
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        showlegend=True, barmode='stack',
        font_color="midnightblue"
    )
    fig.update_yaxes(title_text="Encerrados / Novos", title_font_size=14,
                 secondary_y=False)
    fig.update_yaxes(title_text="# Total de Alavarás",
                     title_font_size=14, secondary_y=True)
    #fig.update_xaxes(title_text="mês", title_font_size=14, secondary_y=True)
    return fig


def get_hist_tempo_atividade(filtro, value=None):
    logging.info("get_hist_tempo_atividade")
    start = time.time()
    
    key = 'hist_tempo'+str(filtro)+str(value)
    fig = cache.get(key)
    if (fig is not None):
        return fig
   
    df = alvaradata.get_dados_alvara(filtro, value)
    
    logging.info(f"get_hist_tempo_atividade dados obtidos {time.time()-start}")
    start = time.time()

    fig = px.histogram(df, x='TEMPO_ATIVIDADE',
                       marginal="box",  # can be rug `box`, `violin`
                       )
    
    fig.update_layout(
            title="Distribuição do tempo em atividade",
            xaxis_title="Tempo em atividade (meses)",
            yaxis_title="# alvarás",
            font_color="midnightblue"
        )
    
    cache.set(key, fig, timeout=0 if value is None else 200 )
    logging.info(f"return get_hist_tempo_atividade {time.time()-start}")
    
    return fig

@cache.memoize(timeout=120)
def get_bar_tempo_atividade(filtro, value=None):
    
    g = alvaradata.get_tempo_atividade_agg(filtro, value)
    
    fig = px.bar(g, x='ind', y='COUNT', )
    
    fig.update_traces(marker_color='midnightblue')
    fig.update_layout(
            title="Distribuição do tempo em atividade",
            xaxis_title="Tempo em atividade (meses)",
            yaxis_title="# alvarás",
            font_color="midnightblue"
        )

    return fig

def get_mapbox(df, df2 = pd.DataFrame([])):
    
    #./alvaradash/src/.mapbox.token
    mapbox_access_token=open(".mapbox.token").read()


    df=df[df.point.isna() == False & (df.point != 'None')]

    if (df2.empty == False):
        df2=df2[df2.point.isna() == False & (df2.point != 'None')]
        logging.info("get_mapbox df2 size point not null %s"%df2.index.size)

    logging.info("get map not none %s" % df.point.size)

    if (df.point.size < 1):
        return go.Figure()

    #reset index para usar como argumento para definir a cor no grafico
    empresas = df.CD_NOME_EMPRESARIAL.drop_duplicates().reset_index(drop=True)
    colors = [ int(empresas[empresas == e].index[0]+1) for e in df.CD_NOME_EMPRESARIAL.values]
    
    

    lats=[p[0] for p in df.point]
    lons=[p[1] for p in df.point]

    fig=go.Figure(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color = colors,
            cauto=True,
            opacity=0.7,
        ),
        customdata=df.CD_NOME_EMPRESARIAL,
        text=df.NOME_EMPRESARIAL,
        hovertemplate="%{text}"  # <br>%{customdata}"
    ))
    if (df2.empty == False):
        logging.info("df2 not empty ")
        color = [ int(empresas[empresas == e].index[0]) for e in df2.CD_NOME_EMPRESARIAL.values]
        #logging.info("color df2: "+str(color))
        trace=create_polygon(df2,color)
        if (trace is not None):
            fig.add_trace(trace)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
        x=1),
        autosize=True,
        hovermode = 'closest',
        clickmode = 'event',
        mapbox = dict(
            accesstoken=mapbox_access_token,
            # bearing=0,
            center=go.layout.mapbox.Center(
                lat=-25.42679,  # lats[0],
                lon=-49.26681,  # lons[0]
            ),
            # pitch=0,
            zoom=10,
            style= 'streets'
        )
    )

    return fig


def create_polygon(df2, color):
    try:
        fc=[Feature(geometry = Point(p)) for p in df2.point]

        df2.NOME_DA_EMPRESA.values[0]

        c=convex(FeatureCollection(fc))
        geomtype=c['geometry']['type']
        coordinates=c['geometry']['coordinates'][0] if (geomtype == 'Polygon') else c['geometry']['coordinates'] if (
            geomtype == 'LineString') else [c['geometry']['coordinates']] if geomtype == 'Point' else []

        lats=[p[0] for p in coordinates]
        lons=[p[1] for p in coordinates]
        logging.info("LONS %s"%str(lons))
        trace=go.Scattermapbox(
            lat = lats,
            lon = lons,
            mode = 'lines+markers',
            marker = go.scattermapbox.Marker(
                size=18,
                color=color, #$'hotpink',#empresas.index(df2.NOME_DA_EMPRESA.values[0]),
                opacity=0.4,
            ),
            # line =go.scattermapbox.Line(
            # color='hotpink',
            # ),
            customdata = df2.CD_NOME_EMPRESARIAL,
            text = df2.NOME_EMPRESARIAL,
            hovertemplate = '%{text}',  # "%{customdata}",
            #fillcolor = 'lightpink',
            opacity=0.2,
            fill = 'toself',
            #fillcolor='blue'
        )
        return trace
    except Exception as e:
        logging.info("Could not add a plygon trace for points")
        logging.info(df2.point)
        logging.info(e)
        return None


# %%
