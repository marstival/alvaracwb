import dash
import dash_bootstrap_components as dbc

from dash import dcc
from dash import  html


grid = html.Div([
    dbc.Card([
    dbc.CardBody(
        [
            dcc.Markdown(
                ''' 
                ### Base de Alvarás ####
                
                Esta aplicação apresenta algumas informações da [Base de Alvarás de Curitiba](https://www.curitiba.pr.gov.br/dadosabertos/busca/). 
                
                Com o objetivo de facilitar o uso dos dados abertos publicados no Portal, foi gerado um novo dataset consolidado e enriquecido com algumas informações.
                
                [Neste repositório](https://bitbucket.org/sidegoals/alvaras/src/master/) você encontra os seguintes artefatos.

                * __Dataset__ transformado e enriquecido com algumas informações
                * __Dashboard__ para uma visualização rápida da base (esta aplicação)
                * __Wrangling__ fontes dos scripts Python usados para gerar o novo dataset a partir dos dados abertos 
                * ainda em construção, um pipeline automatizado para atualizar o dataset a cada novo arquivo disponibilizado 

                #### Dados ####

                A origem da informação é a base disponibilizada pela Prefeitura Municipal de Curitiba, 
                acessado por meio do [Portal de Dados Abertos de Curitiba](https://www.curitiba.pr.gov.br/dadosabertos/busca/). 

                Os dados são disponibilizados mensalmente no Portal, contendo apenas os alvarás ativos no momento da geração do arquivo. 
                                
                Para analisar o histórico de ativações e encerramentos de alvarás ao longo dos meses,
                foi necessário processar os arquivos referentes aos meses passados (com a "foto" da situação a cada mês). 
                No dataset transformado consolidamos os dados históricos de jan/2017 em diante.

                Além de correções diversas, o dataset conta também com novas informações, como a __geo localização__ do endereço de cada alvará.
                
                Esta aplicação, o dataset, e os scripts usados para transformar os dados originais estão disponíveis [neste repositório](https://bitbucket.org/sidegoals/alvaras/src/master/).              
                
                *O Portal de Dados Abertos de Curitiba e o órgão ou entidade de onde foram acessados os dados não garantem sua autenticidade, qualidade, integridade e atualidade após terem sido disponibilizados para uso secundário.*
    
                #### Autor 
                
                > [Marcelo L Stival](https://www.linkedin.com/in/marcelostival/)
                
                '''
            
            )
        ]
        ),       
    ]) 
])