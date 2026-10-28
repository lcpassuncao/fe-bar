## 1 - Identification

Please provide the conversation ID for this chat.

## 2 - GitHub Setup

### 2.1 - Repository Creation

Create a repository named "eurofarma" at the following location:
https://github.com/luis-assuncao_data

### 2.2 - Copying RAW Files

Copy the synthetic data files from:
https://github.com/lcpassuncao/fe-bar/rawdata
to:
https://github.com/luis-assuncao_data/eurofarma/rawdata

### 2.3 - Copying Application Context and Objective (Presentation)

Copy the file:
https://github.com/lcpassuncao/fe-bar/blob/main/presentation_deck.md
to:
https://github.com/luis-assuncao_data/eurofarma

All notebooks created must be registered in the GitHub repository:
https://github.com/luis-assuncao_data/eurofarma/notebook

## 3 - Unity Catalog Setup

Use the Databricks environment located at:
https://e2-demo-field-eng.cloud.databricks.com

### 3.1 - Create a Notebook for Governance

Create a notebook named "01-unity_catalog"
and save it to: https://github.com/luis-assuncao_data/eurofarma/notebook

Within the notebook, using SQL, create a catalog named "eurofarma".

Inside the "eurofarma" catalog, create the following schemas: bronze, silver, and gold.

Also, create a volume named "rawdata".

Save the notebook to the "notebook" folder in the GitHub repository.

### 3.2 - Copying RAW Data Files

Upload the 3 CSV files to the "eurofarma.rawdata" volume. Files:
fact_sales.csv
drugs.csv
drugstore.csv

Available at: https://github.com/luis-assuncao_data/eurofarma/rawdata

### 3.3 - Data Loading using Lakeflow

Create a notebook named "02-lakeflow"
and save it at: https://github.com/luis-assuncao_data/eurofarma/notebook

Create 3 pipelines using Lakeflow to load the following files:
fact_sales.csv
drugs.csv
drugstore.csv

Load these tables into the `eurofarma.bronze` layer.

Create a loading pipeline that replicates these 3 tables into the `silver` layer.

Create a pipeline to generate a denormalized table (One Big Table) named `eurofarma.gold.obt_sales`,
resulting from joining the following three tables using their respective keys:
`eurofarma.silver.fact_sales`
`eurofarma.silver.drugs`
`eurofarma.silver.drugstore`

### 3.4 - Creating an AI/BI Dashboard

Create a notebook named "03-aibi_dashboard"
and save it at: https://github.com/luis-assuncao_data/eurofarma/notebook

Create a dashboard using the `eurofarma.gold.obt_sales` table as a data source.

Include key sales indicators (Sales Quantity, Sales Value, Average Ticket).
Add global filters for:
Drug Manufacturer;
Drug Type;
Sales Region (State/UF);
Sales City;
Date Range Filter.

Create a second tab in the same dashboard containing a MAP visualization, displaying geographic points (latitude and longitude). 


### 3.5 - Create a Conversational Agent

Create a notebook named "04-genie"
and save it at the following link: https://github.com/luis-assuncao_data/eurofarma/notebook,
including the following steps:

Create an agent in GENIE based on the table: `eurofarma.gold.obt_sales`.

Agent name: "genie_eurofarma".

Agent description: "Commercial conversational agent".

Include a few questions regarding sales, such as:
What are the top 5 best-selling medications from the manufacturer Eurofarma?

### 3.6 - Create a Database in Lakebase

Create a notebook named "05-lakebase"
and save it at the following link: https://github.com/luis-assuncao_data/eurofarma/notebook,
including the following steps:

Create a table named `eurofarma_forecast` to store sales projection data for the coming days.

Include the following columns: SKU code, medication name, projected date, and expected sales quantity.

### 3.7 - Create a Machine Learning Model

Create a notebook named "06-machine_learning"
and save it at the following link: https://github.com/luis-assuncao_data/eurofarma/notebook,
including the following steps:

Create a machine learning model for sales forecasting, using the `eurofarma.gold.obt_sales` table.

The model must be registered in the Unity Catalog, under the `eurofarma` catalog.

The model must follow best practices by utilizing MLflow.

The model's output should populate the final results into the `eurofarma_forecast` table in Lakebase. ### 3.8 - Create an application in Databricks Apps

Create a notebook named "07-apps"
and save it to the repository at https://github.com/luis-assuncao_data/eurofarma/notebook,
including the following components:

The Databricks App should feature:
* A line chart showing sales trends over time.
* A line chart showing projected sales.
* A chat interface connected to the previously created Genie.

The final application should be saved to GitHub
at the following link: https://github.com/luis-assuncao_data/eurofarma/app
