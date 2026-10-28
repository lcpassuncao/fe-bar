
## 1 - Identificação

Informe qual o conversation ID desse chat?

## 2 - GitHub setup

### 2.1 - Criação do REPO

Crie um repositório chamado "eurofarma" no endereço:
https://github.com/luis-assuncao_data

### 2.2 - Cópia dos Arquivos RAW

Faça uma cópia dos arquivos sintéticos de dados do endereço:
https://github.com/lcpassuncao/fe-bar/rawdata
para o endereço:
https://github.com/luis-assuncao_data/eurofarma/rawdata

### 2.3 - Cópia do contexto e objetivo da aplicação (Presentation)

Copie o arquivo:
https://github.com/lcpassuncao/fe-bar/blob/main/presentation_deck.md
para o endereço:
https://github.com/luis-assuncao_data/eurofarma


Todos os notebooks que forem criado devem ser registrados no github:
https://github.com/luis-assuncao_data/eurofarma/notebook

## 3 - Unity Catalog setup

Utilize o ambiente Databricks no endereço:
https://e2-demo-field-eng.cloud.databricks.com

### 3.1 - Crie notebook para Governança

crie um notebook com o nome de "01-unity_catalog",
e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook

No notebook, em linguagem SQL, crie o catálogo: "eurofarma".

Dentro do catálogo "eurofarma",  crie os schemas:  bronze, silver, gold.

Crie também um volume chamado "rawdata".

Grave o notebook no github, na pasta chamada "notebook".

### 3.2 - Cópia dos arquivos RAW DATA

Faça upload dos 3 arquivos CSV para o volume eurofarma.rawdata.

Arquivos;
fact_sales.csv
drugs.csv
drugstore.csv

Que estão no https://github.com/luis-assuncao_data/eurofarma/rawdata

### 3.3 - Carga de dados utilizando Lakeflow

Crie um notebook com o nome de "02-lakeflow",
e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook

Crie 3 pipelines usando o Lakeflow para carga dos Arquivos:
fact_sales.csv
drugs.csv
drugstore.csv

Carga das tabelas no eurofarma.bronze

Crie um pipeline de carga replicando as 3 tabelas para a camadaa silver.

Crie um pileline para gerar uma tabela (one big table, desnomalized) chamada eurofarma.gold.obt_sales,
resultado do cruzamento pelas respectivas chaves, das três tabelas abaixo:
eurofarma.silver.fact_sales
eurofarma.silver.drugs
eurofarma.silver.drugstore


### 3.4 - Criação do Dashboard AI/BI

Crie um notebook com o nome de "03-aibi_dashboard",e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook

Crie um Dashboard utiizando como fonte a tabela: eurofarma.gold.obt_sales.

Com macro indicadores de Vendas (Qde Vendas, Valor Vendas, Ticket Médio).
Colocar filtros globais:
Fabricante do Medicamento;
Tipo do Medicamento;
Região da Venda (UF);
Cidade da Venda;
Filtro de período de data;

Crie uma segunda aba no mesmo dashboard, com um elemento gráfico em forma de MAPA, com pontos geográficos (latitude e longitue);

### 3.5 - Crie um Agente conversacional

Crie um notebook com o nome de "04-genie",  
e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook,
contendo os seguintes passos:

Crie um Agente na GENIE a partir da tabela: eurofarma.gold.obt_sales;

Nome do Agente: "genie_eurofarma".

Descrição dos agentes:  "Agente conversacional Comercial".

Coloque algumas perguntas sobre vendas:
Quais os TOP 5 medicamentos mais vendidos do fabricante Eurofarma.

### 3.6 - Crie uma base de dados no Lakebase

Crie um notebook com o nome de "05-lakebase", 
e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook,
contendo os seguintes passos:

Crie uma tabela chamada eurofarma forecast, para armazenar dados de projeção de vendas para os próximos dias.

Com as colunas:  código do SKU, nome do medicamento, data projetada, qde esperada de vendas


### 3.7 - Crie um Modelo de Machine Learning

Crie um notebook com o nome de "06-machine_learning",
e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook,
contendo os seguintes passos:

Crie um modelo de Machine Learning de Forecast de vendas, utilizando a tabela eurofarma.gold.obt_sales;

O Modelo deve ser registrado no Unity Catalog, catálogo eurofarma.

O modelo deve seguir as boas práticas utilizando o MLFlow.

O modelo deve ter como saída, popular o resultado final na tabela do Lakebase de eurofarma forecast.


### 3.8 - Crie uma aplicação no Databricks APPs

Crie um notebook com o nome de "07-apps"
e gravar no link https://github.com/luis-assuncao_data/eurofarma/notebook,
contendo os seguintes passos:

No Databricks APPs deve ter um:
* gráfico de linhas evolutivo das vendas.
* gráfico de linhas de vendas projetadas.
* chat com o genie criado

O aplicativo final, deve ser gravado no github:
e gravar no link https://github.com/luis-assuncao_data/eurofarma/app

Databricks app	Simple way to expose and interact with data

