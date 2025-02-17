#### Mapbox token
Adicione na pasta 'src' um arquivo com o token mapbox
Arquivo: ".mapbox.token"

#### Deploying 

Originalmente usei um Droplet na [DigitalOcean](www.digitalocean.com), com Docker pré configurado.

Veja definições do arquivo docker-compose.yml. 

#### Acesso entre containers
Conforme definido o docker-compose.yml, os 2 containers rodam em uma mesma "rede", logo podem ser referenciadas pelo nome do serviço.
Para usar um serviço externo Redis, usar a variavel de ambiente CACHE_DIR para indicar para a aplicação como acessar o seriço redis.

#### Memoria

A aplicação dash usa Redis para fazer cache dos dados. Carrega o dataset completo a partir de um bucket na Amazon (AWS S3) no serviço Redis (portanto em memória). E passa a usar o Redis enquanto o dado estiver em cache - e está confiugrado para não expirar.

Portanto considerando o deploy dos dois containers (aplicação dash e Redis) no mesmo node, exige relativamente bastante memória (mas roda com folga em um droplet com 2vCPU e 4GB de RAM desde que SWAP esteja habilitado no host  - ver abaixo) 

Para evitar que o container seja derrubado pelo host, verifique a memória disponível para o container docker.
* Parametros de inicialização e configuração de limite de memória [link](https://docs.docker.com/config/containers/resource_constraints/)
* Ativação de swap no host como descrito [neste post](https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-16-04). 

```bash
#ssh into your droplet
sudo swapon --show
sudo fallocate -l 1G /swapfile
ls -lh /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon --show
free -h
sudo cp /etc/fstab /etc/fstab.bak
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```
#### snippets

##### Running containers
Recomendado o uso do docker-compose como definido no arquivo docker-compose.yml.

```bash
#export HOST=$(ifconfig eth1 | awk '/inet / { print $2 }' | sed -e s/addr://)

export HOME_BUCKET='s3://cwbalvaras/' 
export CACHE_DIR='redis://redis:6379'

docker network create -d bridge my_bridge

docker run --net=my_bridge --name redis -p '6379:6379'  -v '/var/lib/redis/:/var/lib/redis:rw'  redis &
#--oom-kill-disable --memory-reservation 4g --memory 12g --memory-swap 16g

docker run --name alvarasdash --net=my_bridge -p 8051:8051 \
--link redis \
-e HOME_BUCKET=$HOME_BUCKET -e CACHE_DIR=$CACHE_DIR -v $HOME'/.aws/credentials:/root/.aws/credentials:ro' stival/dashboarding:alvarasdash &
#--oom-kill-disable --memory-reservation 4g --memory 12g --memory-swap 16g 
```
#####
Para passar parametros de memoria via docker-compose, precisa usar a opção docker-compose `--compatibility` para que reconheça os parametros como estes abaixo. Ou usar via `docker run` 
```yml
deploy:
      resources:
          limits:
              #cpus: '0.50'
              memory: '2g'
              memswap_limit: '8g'
          reservations:
              memory: 1G
              memswap_limit: '6g'
```