import dash_bootstrap_components as dbc
dbc
from dash import dcc
from dash import  html

import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_app import app, cache, dash, logging
import plotly.graph_objects as go
import json
import alvarachart
import alvaradata
import time

#import locale
#locale.setlocale(locale.LC_ALL, 'pt_BR.ISO-8859-1')

overview = dbc.CardDeck(children=[
        dbc.Card(children=[
            dcc.Loading(
                html.Div(id="card-total")
            ),
        ],  body=True, outline=True, className="mb-2", color="info"
        ),
        dbc.Card([
            dcc.Loading(
                html.Div(id='pct-recentes')
            ),
        ],  body=True, outline=True, className="mb-3", color="info"
        ),
        dbc.Card([
            dcc.Loading(
                html.Div(id = 'abertos-fechados')
            ),
        ],  body=True, outline=True, className="mb-3", color="info"
        ),

    ], style={'wdith': '100%', 'align-content': 'center'}, className="mt-3")


radioitems = dbc.FormGroup([dbc.RadioItems(
            options=[
                {"label": "Trimestral", "value": 'QS'},
                {"label": "Mensal", "value": "MS"},
                {"label": "Anual", "value": "AS", "disabled": True},
            ],
            value='QS',
            inline=True,
            id="radioitems-input",),])

grid = html.Div([
    
    html.Div(id='signal-load-atividades', style={'display': 'none'}), 
    overview,
    dbc.Card(children=['Alvarás novos e encerrados ao longo do tempo.',
                       radioitems,
                       dcc.Loading(children=[
                           dcc.Graph(id='g_historico',
                                 config={'displayModeBar': False},
                                 animate=False,
                                 #figure=go.Figure()
                                 )
                       ]),
                       ], body=True, className="mX-3"),
    dbc.Row([
        dbc.Card(children=[
            dcc.Loading(children=[
                dcc.Graph(id='g_ativos_age',
                    config={'displayModeBar': False},
                    animate=False,
                    #figure=go.Figure(),
                    style={'width': '100%'}
                    )  
                ]
            )
        ], body=True,  className="w-70"#, color="info"
        ),

        dbc.Card([
            dcc.Loading(
                html.Div(id='card-tempo-medio')
            )
        ], body=True,  className="w-30"#, color="info"
        ),

    ], className='mX-3'),
    html.Div(
        dbc.Card(children=[html.Div(
            dcc.Loading(
                dcc.Graph(id='g_top_emp',
                      config={'displayModeBar': False},
                      animate=True,
                      figure=go.Figure())
            )
        )],body=True, className="mt-1"
        ), style={'overflowY': 'scroll', 'height': 500}
    ),
    dbc.Card(children=[
        dbc.FormGroup(
        [dbc.Label("Selecione uma ou mais empresas para visualizar no mapa.", width=10),
         dcc.Dropdown(
            id='drop-empresas',
            options=[],
            multi=True
        ),
            dbc.Button("Atualizar mapa", id='btn_map_empresa')
        ]),

        dbc.Spinner(html.Div(id="loading-map")),
        dcc.Graph(id='g_ativos_map',
                  config={'displayModeBar': False},
                  animate=False,
                  figure=go.Figure(),
                  style={'height': '75vh'})
    ], body=True, className="mt-3")
])


def page_layout():
    return grid

app.layout = grid

@app.callback([Output("card-total","children"), 
    Output("pct-recentes","children"), 
    Output("abertos-fechados","children"),
    Output("card-tempo-medio","children")],
    [Input('signal-load-atividades', 'children')])
def overview_update(atividades):
    
    logging.debug(f'func overview_update param {type(atividades)} conteudo {atividades}')
    print(f'func overview_update param {type(atividades)} conteudo {atividades}')

    dparam = alvaradata.get_overview_data('all', atividades)
    
    total_ativos = dparam['total_ativos']
    pct_recentes = dparam['pct_recentes']
    encerrados12 = dparam['encerrados12']
    abertos12 = dparam['abertos12']

    card_total = html.P(
                ["Curitiba tem ",
                 html.H3(f"{total_ativos:n} "),
                 html.H4("alvarás ativos")
                 ], className="card-text",
            )

    pct_recentes = html.P([
                 html.H3(f"{pct_recentes:.2%} "),
                 "estão em ",
                 html.H4("estágio inicial,"),
                 " com ",
                 html.H5(f"até 42 meses"),
                 ], className="card-text",
            )
    abertos_fechados = html.P(
                ["Nos últimos ", html.H4("12 meses:"),
                html.H5(
                    [dbc.Badge(f"{abertos12:n}", color='dark', className="ml-1"), " novos alvarás  "]),
                html.H5(
                    [dbc.Badge(f"{encerrados12:n}", color='dark', className="ml-1"), " encerrados"]),
                ], className="card-text",
            )
    
    idade_media = round(dparam['idade_media']/12, 2)
    quantiles = dparam['quantiles']

    tempo_medio = html.P([html.H4("Tempo médio "),
                    "em atividade é de ",html.H4(f"{idade_media:n} anos."),
                    html.Br(), html.Br(),
                    html.H4(f"{0.50:.0%} "), " dos alvarás tem ",
                    html.H4(f"entre {int(quantiles[0]/12):n} e {int(quantiles[2]/12):n} anos.")
                ], className="card-text",)

    print(f'return func overview_update param {type(atividades)} conteudo {atividades}')

    return card_total, pct_recentes, abertos_fechados, tempo_medio
  
@app.callback(
    Output("g_historico", "figure"),
    [Input("radioitems-input", "value"),
     Input("signal-load-atividades", "children")])
def update_g_historico(radio_items_value, atividades):
    logging.debug(f'func update_g_historico param {type(atividades)} conteudo {atividades}')

    if (radio_items_value in list(['QS', 'AS', 'MS']) == False):
        radio_items_value = 'QS'
    fig_historico = alvarachart.get_consolidado(
        'all', value=atividades, freq=radio_items_value, inicio=None
    )
    return fig_historico

  
@app.callback(
    Output("g_top_emp", "figure"),
    [Input("signal-load-atividades", "children")])
def update_top_empresas(atividades):
    logging.debug(f'func update_top_empresas param {type(atividades)} conteudo {atividades}')

    g = alvaradata.get_top_empresas('ativo', atividades)
    fig_top_emp = alvarachart.get_top_filiais(g)

    return fig_top_emp

@app.callback(Output("g_ativos_age", "figure"),
             [Input("signal-load-atividades", "children")])
def update_g_ativos_age(atividades):
    logging.debug(f'func update_g_ativos_age param {atividades}')
    start = time.time()

    fig_age = alvarachart.get_hist_tempo_atividade('ativo', atividades)
    logging.debug(f'return func update_g_ativos_age param {atividades}')
    logging.debug(f'return func time {time.time()-start}')
    return fig_age

@app.callback(
    Output("drop-empresas", "options"),
    [Input("drop-empresas", "search_value"),
    Input("signal-load-atividades", "children")],
    [State("drop-empresas", "value")],
)
def update_multi_options(search_value, atividades, value):
    logging.debug(f'func update_g_ativos_age param {type(atividades)} conteudo {atividades}')

    top_empresas = alvaradata.get_top_empresas('ativo', atividades)
    # pode haver nome de empresa repetido, pois foi agrupado por atividade_principal
    options_empresas = [{'label': top_empresas[top_empresas.index == i]['NOME_EMPRESARIAL'].iloc[0],
                        'value': str(i)} for i in top_empresas.index.unique()]
    
    if not search_value:
        return options_empresas

    ops = [
        o for o in options_empresas if search_value in o["label"] or o["value"] in (value or [])
    ]
    # logging.debug(ops)
    return ops
    
#Output('loading-map', 'children')
@app.callback(
    Output('g_ativos_map', 'figure'),
    [Input('btn_map_empresa', 'n_clicks'),
     Input('g_ativos_map', 'clickData'),
     Input('drop-empresas', 'value'),
     Input('loading-map', 'n_clicks')])
def generate_map_empresas(n_clicks, clickdata, selected, spinner_input):
    start = time.time()
    logging.info("func generate_map_empresas")
    logging.info("BEGIN generate_map %s" % selected)

    ctx = dash.callback_context
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    logging.info("generate_map event id : %s" % button_id)

    if ((button_id != 'btn_map_empresa') and (button_id != 'g_ativos_map')):
        return go.Figure()

    if ((selected == None) or (len(selected) < 1)):
        selected = alvaradata.get_top_empresas('ativo', None).index.values

    df_filtered = alvaradata.get_top_empresas_alvaras('ativo', None)
    df_filtered = df_filtered.loc[lambda x: x.CD_NOME_EMPRESARIAL.isin(
        [int(s) for s in selected])]

    trace = pd.DataFrame([])
    if (button_id == 'g_ativos_map'):
        logging.info(json.dumps(clickdata, indent=2))
        trace = df_filtered[df_filtered.CD_NOME_EMPRESARIAL ==
                            clickdata['points'][0]['customdata']]

    fig = alvarachart.get_mapbox(df=df_filtered, df2=trace)

    logging.info("func generate_map_empresas %d" % (time.time() - start))
    return fig


