
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

The Commercial Director at Eurofarma faces the challenge, linked to his annual targets, of increasing the market share for generic drug sales by 2%, with a particular focus on the Northeast region. 
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

## How does your Databricks solution address this challenge? 

Databricks is a comprehensive Data and AI platform that provides end-to-end solutions—covering everything from data ingestion and governance to machine learning models, GenAI assistants, and data applications—with the goal of simplifying and accelerating operations.

| Solution | Objective |
| -- | -- |
| Unity Catalog | Unified and native Data Governance |
| Lakeflow | Data ingestion in a simple way |
| Genie Agent | Democratize information by making it accessible via natural language |
| Machine Learning | make it intelligent with AI Model to clustering sales and forecasting |
| Lakebase | Operational serving of AI Models |
| Databricks app | Simple way to expose and interact with data |
| AI/BI Dashboard | Commercial Analytics Dashboard with Sales KPIs |

</br></br>

## Expected Business Outcomes

* Reduce medication stockout by 20%;
* Increase the market share of generic medications by 1%;

</br></br>

## Technological improvements

* Unification of data, analytics, and AI on a single platform.
* Greater agility: accelerates the creation of pipelines, dashboards, predictive models, and AI applications.
* Centralized governance: provides access control, auditing, lineage, and security policies.
* Adoption of generative AI: facilitates the development of models, agents, and applications based on corporate data.
* Real-time processing: supports both batch and streaming workloads within the same architecture.
* Increased productivity: collaborative environments enable the reuse of code, data, models, and processes.

</br></br>
