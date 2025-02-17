# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
# %%

import dash_bootstrap_components as dbc
from dash import dcc
from dash import  html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import page03
import page04
from dash_app import app, dash, logging

server = app.server

# %%
navbar = html.Div([
    dcc.Location(id="url", refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/alvaras", id="navindex")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("Sobre", href="/sobre",
                                         id='dropmenu-wellcome'),
                    dbc.DropdownMenuItem("Alvarás Dashboard",
                                         href="/alvaras", id='dropmenu-ativos')
                    #dbc.DropdownMenuItem("Histórico", href="/page02", id='dropmenu-historico'),
                ],
                nav=True,
                in_navbar=True,
                label="More",
                id='dropmenu'
            ),
            dbc.Col(width=2)
        ],
        brand="Base de Alvarás | Curitiba",
        color="primary",
        dark=True,
        # fluid=True
    )
])


main_layout = html.Div(
    [
        dbc.Container([
            navbar,
            html.Div([
                page04.grid
            ], id='content-grid')
        ])
    ]
)

app.layout = main_layout

# "complete" layout
app.validation_layout = html.Div([
    page04.grid,
    page03.grid,
    main_layout,
])

# warmup cache - traz os dados do bucket aws S3 para o serviço redis
'''alvaradata.get_dados_alvara_all()
# faz cache de alguns conjuntos de dados calculados a partir do dataset
alvaradata.get_dados_consolidado('all')
alvaradata.get_overview_data('all')
alvaradata.get_top_empresas('ativo')
alvaradata.get_top_empresas_alvaras('ativo')'''


@app.callback(
    Output("content-grid", "children"),
    [Input("dropmenu-ativos", "n_clicks"),
     Input("dropmenu-wellcome", "n_clicks"),
     Input('url', 'pathname'),
     Input('navindex', 'n_clicks')])
def menuitem_benef(ativos, wellcome, pathname, navindex):
    print("menu item : %s %s %s %s" % (ativos, wellcome, pathname, navindex))

    ctx = dash.callback_context
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    print("button id : %s" % button_id)

    if (button_id == 'dropmenu-ativos'):
        return [page04.page_layout()]
    elif (button_id == 'dropmenu-wellcome'):
        return [page03.grid]
    elif ((button_id == 'url') or (button_id == 'navindex')):
        if ((pathname == '/index') or (pathname == '/alvaras')):
            return [page04.page_layout()]
        elif (pathname == '/sobre'):
            return [page03.grid]
        else:
            return [page04.page_layout()]
    else:
        print("Error: %s" % button_id)
        return [page04.page_layout()]

# %%


if __name__ == '__main__':
    app.run_server(debug=True,  use_reloader=False,
                   host='0.0.0.0', port='8051')
# %%
