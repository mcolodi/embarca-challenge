# Desafio Embarca
Desafio de orquestração de microserviços usando AWS Step Functions, Lambdas e S3.

Funções Lambda:
- lambda1: faz o download dos arquivos de dados de acidentes de diferentes fontes, une os dados e salva no S3.
- lambda2: faz o processamento dos dados de acidentes, salva no banco de dados e retorna informação sobre os dados processados.

Pipeline:
- lambda1 -> lambda2

Pre-requisitos:
- iniciar o Docker e o PostgreSQL em contêiner (banco de dados local 'docker-compose up -d')
- criar um bucket S3 para armazenar os dados
- adicionar as credenciais de acesso ao bucket S3 no arquivo credentials.env
- adicionar as credenciais do banco de dados no arquivo credentials.env

Deploy via Serverless:
- Status: parte inicial de testes, não está funcionando corretamente
- prévia da estrutura em arquivo serverless.yml
