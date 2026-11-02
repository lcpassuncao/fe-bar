
## Introdution

* **Company** :  EUROFARMA
* **Sector**  :  Pharmaceutical Industry
* **Author**  :  Luis Assunção (Solution Architect Databricks)
* **Use Case**:  Sales and demand-forecasting for generic medicines

</br></br>

## About EUROFARMA

Eurofarma is a multinational company with 100% Brazilian capital. Since 1972, it has been recognized by the medical community and society at large for promoting access to healthcare and a better quality of life through affordable, high-quality, and innovative treatments.

For over 50 years, the Eurofarma Group has operated in the healthcare sector, producing and marketing products and services designed to improve people's quality of life. With a diversified portfolio, the company is active across all key segments—including prescription drugs, over-the-counter (OTC) products, generics, hospital products, and oncology—as well as in the export and contract manufacturing of medicines. In Brazil alone, it offers more than 4,000 SKUs, serves 42 medical specialties, and covers over 140 therapeutic classes. Furthermore, it is the most-prescribed pharmaceutical company in Brazil.

The Eurofarma Group has a presence in 24 countries, with 10 manufacturing plants, covering all of Latin America, as well as select countries in Africa and the United States. In 2025, the company generated net sales of R$ 12.5 billion and currently employs more than 13,000 people. It concluded 2023 with two significant acquisitions: Genfar—Sanofi’s generics operation based in Colombia, with affiliates in Ecuador and Peru—and seven assets from Sanofi for the Brazilian, Colombian, Mexican, Argentine, and Uruguayan markets.

Revenue in Brazil: **US$ 4 billion (2025)**.

</br></br>

## About DATABRICKS

Databricks is a global enterprise software company that provides a cloud-based Data + AI Platform built on an open lakehouse architecture.

* Founded: 2013 by the creators of Apache Spark, Delta Lake, MLflow, and Unity Catalog.
* Valuation & Funding: Reached a $190 billion valuation following a $5 billion funding round in August 2026.
* Revenue: Crossed a $7 billion revenue run-rate with 80% year-over-year growth.
* Customer Base: Serves over 20,000 organizations globally, including more than 60% to 70% of the Fortune 500.

</br></br>



## Commercial Challenges: Sales and demand-forecasting 

The Commercial Director at Eurofarma faces the challenge, linked to his annual targets, of increasing the market share for generic drug sales by 1%, with a particular focus on the Northeast region; representing an increase of USD 35 million in annual revenue.
He needs visibility into which products are best suited for each specific region. 
Another of his goals is to reduce the stock-out rate for generic medications.
Currently, he lacks detailed visibility into sales by region.
He is dependent on data teams whenever he requires a more specialized report.
He would like greater independence in manipulating data.
Some reports contain inconsistencies, take too long to become available, and sales figures do not always align across regions.
He needs insight into which product types are most appropriate for each region and aims to improve demand forecasting.
Furthermore, he wants to democratize data access for Regional Managers, who are non-technical users, so they can monitor sales and take action to help meet sales targets. 
Ideally, each Regional Manager should have exclusive access to their own specific data.
Sales reports are sometimes delayed and only reflect the previous day’s data (D-1); 
He would prefer to have access to sales results on an hourly basis.

</br></br>


## Data & AI area Challenges:  Platform modernization

The Head of Data & AI, who reports to the IT Director, faces the challenge of modernizing the current data platform—hosted on GCP, with a Data Lake in BigQuery. 
Meanwhile, most business units rely on Excel as their primary tool for decision-making. The data team is currently centralized and faces a significant backlog of unaddressed data projects; 
There is an urgent need to increase team productivity and reduce the time required to deploy new data pipelines. To improve operational efficiency, the organization is exploring the decentralization of certain activities, potentially adopting a "Data Mesh" framework to grant greater autonomy to business units. 
Furthermore, the current BigQuery setup presents gaps in data governance, challenges in access management, and a lack of visibility into costs by individual business area.
The objective is to migrate the platform to boost the data team's productivity—for instance, by leveraging coding assistants ("Vibe Coding"). 
There are currently 11 pending data projects that must be delivered by the end of the year. 
Regarding the governance of predictive models, the lifecycle process requires greater robustness; 
The existing demand forecasting model lacks accuracy when broken down by region, and the training of new models is overly time-consuming, lacking a formal lifecycle management process. 
With an average project duration of 4 months, the team needs to achieve at least a 50% gain in productivity to clear the existing backlog. 
Additionally, there is a goal to reduce cloud infrastructure costs.

</br></br>

## Big Numbers of Challenge:

* Brazil has more than 100,000 pharmacies and drugstores;
* Out-of-Stock Rate: Industry data (such as surveys by Abrappe) indicate that the average out-of-stock rate in pharmaceutical retail is around 11.17%, split between commercial out-of-stocks (7.27%) and operational out-of-stocks (3.90%).
* Immediate Impact: When a customer seeks a medication for chronic use or an immediate need and fails to find it at the point of sale (POS), the pharmacy not only loses the revenue from that specific sale but also risks losing the patient’s loyalty, as they are likely to turn to a competitor.


</br></br>


## EUROFARMA Metrics:

The company EUROFARMA:

* Has over 4,000 active SKUs;
* Includes 236 SKUs in its generic drug portfolio;
* Manufactures more than 570 million units of medication per year;
* Serves 42 medical specialties;
* Covers over 140 therapeutic classes;
* Its Generic Drugs division holds a 14.7% market share;
* Annual revenue in the generic drugs category reaches US$ 604 million;
* Sells 200 million units of generic drugs annually;
* Its generic products are distributed across approximately 90,000 pharmacies throughout Brazil.

</br>

**Reference:**  https://eurofarma.com.br/generic-drugs


</br></br>

## How does your Databricks solution address Data&AI area challenge? 

To meet the Head of Data’s modernization goals, the Databricks platform addresses the client’s needs from end to end.
Regarding governance, Databricks offers native, centralized data governance through Unity Catalog. It provides a clear, simple way to grant role-based access and establish permissions for catalogs, schemas, and tables. The value lies in making governance more observable, costs more attributable, and access more consistent and granular—reducing the effort required to manage disparate rules as the environment scales. Combined with a proposed migration from the existing Data Lake to Delta Lake, this will result in a much more integrated governance framework than what is currently available in GCP BigQuery.
To minimize initial disruption during the migration, it is recommended to use Lakeflow Connect and direct federation with BigQuery; this allows for immediate short-term gains while the Data Engineering team refactors ingestion pipelines.
Beyond modernization, this migration from BigQuery is expected to reduce infrastructure costs by approximately 30%, in line with market benchmarks.
In terms of productivity, Databricks enhances team output through integrated coding assistants (such as Genie Code), a collaborative environment, and simplified administration via DataOps frameworks. This will enable the data team to meet goals for accelerating the deployment of new projects, shortening timelines to a matter of weeks.
For the predictive model lifecycle, Databricks provides an MLOps framework called MLflow, which addresses both productivity and model robustness. The Feature Store functionality allows data scientists to boost productivity by reusing model parameters, while AutoML reduces the time required to create new models from months to weeks. Furthermore, Databricks includes integrated Model Serving, as well as Data Quality and Data Monitoring features, which help identify when models begin to lose accuracy.

</br></br>

## How does your Databricks solution address Business challenge? 

Databricks platform provides simple tools for querying and manipulating data—even for non-technical users, thereby fulfilling the goal of data democratization and reducing reliance on IT teams.
This ease of access is supported by a wide range of platform features, including conversational agents like "Genie Agents", which allow users to ask questions in natural language that are then automatically translated into queries against Data Lake tables.
The proposal involves creating a Genie Agent that enables Sales Managers and representatives in each territory to monitor daily sales, investigate discrepancies between actual and projected figures, access demand forecasts, identify top-selling products by region, and gain actionable sales insights to help meet targets. This granular level of oversight will improve management, support the achievement of sales goals, and, consequently, help increase market share.
Access to information is segmented by region; each Regional Manager can only analyze data for their own specific territory; a process managed automatically by Databricks through its governance solution, Unity Catalog.
In addition to the Genie conversational agent, Databricks offers a sales analysis solution via AI/BI Dashboards, allowing managers to track sales trends and utilize map-based visualizations for georeferenced analysis.
For users involved in sales planning who still rely on Excel for calculations, Databricks provides an Excel Add-in. This allows them to connect to the Data Lake directly from their spreadsheets and access the Genie conversational agent without leaving the Excel environment, significantly streamlining workflows and ensuring analytical consistency through a "single source of truth."
To address the objective of reducing stock-outs for generic medications, we propose a continuous improvement process for demand forecasting models, which are currently reviewed only on a semi-annual basis. With MLflow and AutoML capabilities, the creation, monitoring, and training of models will significantly accelerate the MLOps cycle. This, in turn, will improve prediction accuracy, with an expected reduction in the stock-out rate by at least 2 percentage points.
Model precision and decision-making agility will also be supported by higher-quality data—ensured by Databricks governance features—and by increasing the frequency of sales data loads from daily to hourly. This will be achieved through enhancements to data engineering processes using Databricks Lakeflow and the Spark Declarative Pipelines (SDP) framework—an open, native Apache Spark framework designed to simplify batch and streaming data engineering via a declarative approach. This will reduce reporting inconsistencies and substantially shorten the time required to make new data and analyses available.

</br></br>

## Expected Business Outcomes

* At least a 50% gain in productivity (Data and AI team);
* Reduce Infraestructure cost (by 25%, saving USD 200K per year);
* Increase the market share of generic medications by 1%;
* Reduce medication stockout by 2%;

</br></br>

## Next Steps

* Present a formal commercial proposal for the Databricks platform.
* Engage an accredited Databricks partner to implement the migration project.

</br></br>
