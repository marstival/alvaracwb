# README #

Uma tentativa de libertar os dados abertos da base de alvarás de Curitiba...


## Dados ##

A origem da informação é a base disponibilizada pela Prefeitura Municipal de Curitiba, acessado por meio do Portal de [Dados Abertos de Curitiba](https://www.curitiba.pr.gov.br/dadosabertos/busca/). O Portal de Dados Abertos de Curitiba e o órgão ou entidade de onde foram acessados os dados não garantem sua autenticidade, qualidade, integridade e atualidade após terem sido disponibilizados para uso secundário.

[Dicionários de dados (original)](http://dadosabertos.c3sl.ufpr.br/curitiba/BaseAlvaras/Alvaras-Dicionario_de_Dados.csv)

## Produtos ##
Este repositório contém os seguintes artefatos.

|||
|------|:---|
|__ALVARAS DASH__ |uma aplicação com algumas visualizações dinâmicas do dataset de alvarás (Python, Dash, flask, Redis). |
|__Dataset__ | *dataset* criado a partir da Base de Alvarás publicada pela Prefeitura Municipal de Curitiba acessado através do Portal de Dados Abertos. |
|__Wrangling__ | conjunto de scripts que tratam os dados históricos da Base de Alvarás disponíveis no Portal de Dados Abertos e geram o *dataset* consolidado. |
|||

#### Licença
A licença do código é [LGPL3](https://www.gnu.org/licenses/lgpl-3.0.en.html) e dos dados convertidos [Creative Commons Attribution ShareAlike](https://creativecommons.org/licenses/by-sa/4.0/). Cite as fontes * -Fonte: Dados da [Base de Alvaras de Curitiba](https://www.curitiba.pr.gov.br/dadosabertos/busca/), transformados conforme descrito [neste projeto](https://bitbucket.org/sidegoals/alvaras/)*. Caso compartilhe os dados, utilize a mesma licença.

#### Dataset

A preparação dos dados passa por diversos estágios com o objetivo de criar um arquivo mais adequado para análises. Consulte [wrangling/Readme.md](wrangling/Readme.md) para mais informações sobre as transformações ralizadas a partir da base histórica original.

O arquivo final consolida e agrupa os arquivos da base histórica, e inclui algumas colunas adicionais conforme abaixo. Além das colunas originais descritas no [Dicionários de dados (original)](http://dadosabertos.c3sl.ufpr.br/curitiba/BaseAlvaras/Alvaras-Dicionario_de_Dados.csv).

|||
|---|---|
|Campo (novo) | Descrição dos campos adicionados ao dataset |
|*REFERENCIA_min*| Data da primeira ocorrência nas extrações (a partir de 2017-01-01); Todos com REFERENCIA_min == 2017-01-01 correspondem ao estoque de alvarás ativos em 2017-01-01; A partir desta data a REFERENCIA_min indica a data (mês) no qual o alvará passa a estar ativo (e portanto incluído nas extrações). Pode-se combinar esta informação com a DATA_EMISSAO |
|*REFERENCIA_max*| última ocorrência nas extrações mensais. Se REFERENCIA_max == "data da última extração", significa que está ainda ativo; Caso contrário, representa a data em que esteve ativo pela última vez (considero como data, ou mês, em que deixou de ter uma alvará ativo) |
|ATIVO| bool - apenas simplifica as consultas; True se REFERENCIA_max == "data da última extração", caso contrário False |
|*CNAE*| código CNAE - inferido pela descrição da atividade, portanto não está preenchido para 100% dos casos.  |
|*point*| Localização geográfica do endereço (tupla). Obs: campo string com o Dict, é preciso usar eval() ou astype(object) para obter a tupla que representa a posição lat/long.  Os campos *address* e *location* são intermediários usado no *basealvaras_geocode.py* |
|*TEMPO_ATIVIDADE*| Tempo de atividade em meses, considera a diferença da data de início da atividade (*INICIO_ATIVIDADE*) e a data em que o alavará deixou de estar ativo (*REFERENCIA_max*)  |

Cenários para exemplificar o significado dos campos após a consolidação:

* REFERENCIA_min == 2020-08-01  alvarás que passaram a figurar na base em agosto de 2020 
* REFERENCIA_min == 2017-01-01 -> como 2017-01-01 é o primeiro arquivo historico, corresponde a todos os alvarás que passaram a figurar na base em qualquer data anterior e que continuavam ativos em 2017)
* REFERENCIA_max == 2020-08-01 -> alvarás que estavam ativos até este mês (E a partir deste mês inativados).
* REFERENCIA_max >= 2020-08-01 AND REFERENCIA_min <= 2020-08-01 -> Quantidade de alvarás ativos no mês de referência 2020-08-01 

### Alvarás Dashboard 

A aplicação pode ser encontrada na pasta alvaras/alvarasdash. 
O arquivo docker-compose.yml pode ser usado para construir o container e rodar a aplicação alvarasdash e o serviço REDIS (imagem oficial dockerhub) usado pela aplicação para cache dos dados.

A aplicação lê os dados disponíveis no dataset, e mantem uma visão dos dados em um serviço *Redis*. 
A variável de ambiente *HOME_BUCKET* pode ser usada para carregar o arquivo de outro local (ver docker-compose.yml)
Obs: pode mudar o local do dataset, mas o nome do arquivo `base_alvaras_curitiba.parquet` na pasta indicada não pode ser alterado.

É necessário prover um [token do Mapbox](https://account.mapbox.com/access-tokens/). Crie um arquivo .mapbox.token na pasta alvaradash/src com o token (apenas o token). 