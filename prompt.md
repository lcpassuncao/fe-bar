
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

## 3 - Unity Catalog setup

Utilize o ambiente Databricks no endereço:
https://e2-demo-field-eng.cloud.databricks.com

### 3.1 - Crie notebook para Governança

crie um notebook com o nome de "01-unity_catalog".

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

crie um notebook com o nome de "02-lakeflow".

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

Crie um Agente na GENIE a partir da tabela: eurofarma.gold.obt_sales;


### 3.6 - Crie um Modelo de Machine Learning


Machine Learning	make it intelligent with AI Model to clustering sales and forecasting
Lakebase	Operational serving of AI Models
Databricks app	Simple way to expose and interact with data

