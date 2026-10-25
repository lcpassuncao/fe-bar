
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

Crie um pipeline de carga, replicando as 3 tabelas para as camadas silver e gold.

### 3.4 - 


