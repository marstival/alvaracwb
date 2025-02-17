

# Keep this out of source code repository - save in a file or a database
import pandas as pd
#import dash_auth
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
#import dash_html_components as html
# dash_core_components as dcc

from flask_caching import Cache

import logging

import os
#%%
import redlock

#df = pd.read_csv('../../secret/dash_app_auth.csv',encoding='utf-8')
#print ("Login with %s"% df.USER[0])
#%%

cache_type = os.getenv('CACHE_TYPE','redis')
#redis://redis:6379
cache_dir = os.getenv('CACHE_DIR','redis://127.0.0.1:6379')
data_home = os.getenv('HOME_BUCKET', '../../dataset/')
if (data_home.endswith('/') == False):
        data_home = data_home+'/'

print ("ENVIRONMENT %s %s %s"%(cache_type,cache_dir,data_home))

if (data_home is None):
    print ('Please, set environment variables HOME_BUCKET, CACHE_TYPE, CACHE_DIR')
    SystemExit

#VALID_USERNAME_PASSWORD_PAIRS = dict(zip(df.USER,df.PASS))
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
    # Loading screen CSS
    #'https://codepen.io/chriddyp/pen/brPBPO.css'
    ])
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': cache_type,
    'CACHE_REDIS_URL': cache_dir,
    'CACHE_DEFAULT_TIMEOUT':200
}

dlm = redlock.Redlock([f"{cache_dir}/0"])


#app.enable_dev_tools(debug=True)
#logger = logging.getLogger()

logging.basicConfig(
    #filename='alvaras.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )

cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)
#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
#)
    
print ("APP SERVER: %s"%app.server)
logging.info("APP SERVER: %s"%app.server)