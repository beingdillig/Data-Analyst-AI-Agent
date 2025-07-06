# Data-Analyst-AI-Agent

## 🧠 Autonomous Data Analyst AI Agent with LangGraph + OpenAI + SQLite

This project is an **AI-powered Data Analyst Agent** that autonomously analyzes datasets using SQL queries, interprets the results, summarizes business insights, and provides a final strategic report — with **zero manual query writing**.

> 🔗 Powered by **LangGraph**, **LangChain**, **OpenAI**, **SQLite**, and **Chroma Vectorstore**.

---

## 🚀 What It Does

1. 📂 Accepts **CSV or Excel files** and uploads them into a SQLite database.
2. 📑 Extracts schema + sample data from the database.
3. 🔍 Uses **LangChain RAG** with a pre-embedded PDF of domain-specific queries to **detect the data domain**.
4. 🧠 Plans high-value SQL queries one by one using an LLM.
5. 🧪 Executes each query and captures results.
6. 📝 Summarizes the result in natural language as business insight.
7. 🔁 Repeats for up to 15 queries or until value is saturated.
8. 📈 Finally, **writes an executive-level report** with all synthesized insights.

---

## 🧱 Project Structure

```text
.
├── data.xlsx                        # Your Excel/CSV file to be analyzed
├── All_Domain_Data_Analysis_Queries.pdf  # Embedded PDF to guide domain classification
├── main.py                         # Main pipeline with LangGraph logic
├── sample.db                       # SQLite DB generated after upload
├── requirements.txt                # All required dependencies
└── README.md                       # This file

```

---
## Components & Tools

| Component        | Description                                                 |
| ---------------- | ----------------------------------------------------------- |
| **LangGraph**    | Orchestrates nodes like planner, runner, summarizer         |
| **OpenAI GPT-4** | Powers the query planner, summarizer, and insight generator |
| **Chroma**       | Used for RAG-based retrieval of relevant domain pages       |
| **LangChain**    | Used for embedding, document loading, and text splitting    |
| **SQLite**       | Simple database backend to store uploaded data              |
| **Pandas**       | Reads Excel/CSV, interacts with SQLAlchemy                  |

---
## Graph Architecture
![data_analyst_ai_agent_LR](https://github.com/user-attachments/assets/431c4a0e-7253-436c-bf17-eaf72a3fc768)
---

## ⚙️ Installation
You can run this project on Colab, VSCode, or locally with Python 3.10+.
1. Create a virtual environment (optional but recommended)
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. Install dependencies
```
pip install -r requirements.txt
```
---
## 🛠️ Usage Instructions
Step 1: Place your data file
Drop your .csv or .xlsx file in the root directory. Rename to data.xlsx (or change name in main.py).

Step 2: Run the Upload Script
This reads your Excel/CSV file and uploads each sheet into a SQLite DB (sample.db).
```
python main.py  # First part of the file handles upload
```

### Step 3: Autonomous AI Agent Starts The Pipeline

- Detects the domain (Retail / FMCG / etc.)
- Plans SQL queries
- Runs and analyzes them
- Generates business summaries
- Stops after 15 insights or if "DONE"
- Synthesizes a final report

---

## 📊 Example Output
```
✅ Uploaded sheet 'sales' to SQLite table 'sales'
Retreiving analysis plan... Retail / CPG (Consumer Packaged Goods) / FMCG Analytics
Thinking about the next query...
Next_query:  SELECT Year, Sector, Category, Brand, SUM("POS $ Sales") AS total_sales, SUM("POS Unit Sales") AS total_units, AVG("Shelf Price") AS avg_price, SUM("Inventory Units On Hand") AS total_inventory
FROM sales
GROUP BY Year, Sector, Category, Brand
ORDER BY Year, total_sales DESC;
Summarizing the query_result please hold on!!

 Summarized_insight:  This analysis provides a comprehensive view of sales, units sold, average shelf price, and inventory across three years (2019–2021), segmented by sector, category, and brand. Several key patterns and shifts emerge:

1. Dominance of Great V-Globex: Across all years, the Great V-Globex brand consistently leads in total sales and units sold, particularly in the Family Care sector (Bath Tissue) and Home Care sector (Air Care and Dish Care). In 2020, for example, Great V-Globex’s Bath Tissue sales reached nearly $1.7 million, far outpacing other brands.

2. Sector and Category Trends:
   - Family Care (Bath Tissue) and Home Care (Dish Care and Air Care) are the primary revenue drivers.
   - Bath Tissue, especially under Great V-Globex, shows the highest sales and inventory levels, indicating strong demand and significant shelf presence.
   - Air Care and Dish Care categories in Home Care also contribute substantially, with several brands (e.g., Air Wic-Umbrella Corp., Renuzit-Wonka Industries, Cascade-Virtucon) maintaining high sales and inventory.

3. Year-over-Year Shifts:
   - There is a marked increase in both sales and units sold from 2019 to 2020, with 2020 representing a peak year for most leading brands and categories. This is likely reflective of pandemic-driven demand for home and family care products.
   - In 2021, while sales remain strong, there is a slight contraction in top-line sales for some leading brands (e.g., Great V-Globex Bath Tissue drops from $1.7M in 2020 to $1.4M in 2021), suggesting a normalization after the 2020 surge.

4. Pricing and Inventory Insights:
   - Average shelf prices for Bath Tissue under leading brands (e.g., Great V-Globex, Southern-Warbucks Industries, Sharmin-123Corp) increased notably in 2021, with some brands exceeding $8–$11 per unit, compared to $3–$7 in prior years. This may indicate price increases or a shift to premium products.
   - Inventory levels for top brands remain high, especially for Bath Tissue, supporting their ability to meet sustained demand.

5. Brand and Category Outliers:
   - Some brands, such as B&W in Bath Tissue, maintain high unit sales at a much lower average price point (around $0.65), suggesting a value-oriented positioning.
   - In Air Care, brands like PomPom and Citrus -Bengals command higher average prices (over $6–$10), but with lower total sales, indicating a niche or premium market segment.
   - Several smaller brands in Dish Care and Air Care have much lower sales and inventory, highlighting a long tail of niche or less competitive offerings.

6. Correlations and Strategic Implications:
   - The combination of high sales, high inventory, and rising average prices for leading brands suggests strong brand loyalty and pricing power, especially in Bath Tissue.
   - The 2020 spike across most categories and brands underscores the importance of supply chain resilience and inventory management during demand surges.
   - The presence of both premium and value brands within the same categories points to a segmented market, with opportunities for both high-margin and high-volume strategies.

In summary, the data reveals a market dominated by a few key brands, especially Great V-Globex, with significant year-over-year fluctuations driven by external factors. There is evidence of both premiumization (rising prices) and value competition, and inventory management remains critical for maintaining market leadership. 


Query Planner signaled completion. No query executed.
Skipping summarizer — DONE signal already received.
Routing to final_insights — planner returned DONE.

AI Final Insight: Executive Business Insights Report: SuperMax Stores (2019–2021)

Overview
The analysis of SuperMax Stores’ sales performance from 2019 to 2021 reveals a market shaped by a few dominant brands, significant pandemic-driven demand shifts, and evolving pricing and inventory strategies. The Family Care (Bath Tissue) and Home Care (Dish Care, Air Care) sectors are the primary revenue engines, with clear patterns of brand leadership, price sensitivity, and market segmentation.

---

1. Market Leadership and Brand Dominance
- Great V-Globex is the unequivocal market leader across both Family Care and Home Care, consistently generating the highest sales and unit volumes, particularly in Bath Tissue, Air Care, and Dish Care. In 2020, Great V-Globex Bath Tissue sales peaked at nearly $1.7 million, far surpassing competitors.
- A small group of brands—Great V-Globex, Endure-Fooddyne, Sharmin-123Corp, Air Wic-Umbrella Corp., and Renuzit-Wonka Industries—account for the majority of sales, indicating strong brand loyalty and effective market positioning.

2. Sector and Category Performance
- Home Care (Dish Care and Air Care) leads in total sales and units sold, with Dish Care slightly ahead each year. Family Care’s Bath Tissue, while third in sales, is the most price-volatile and shows the highest inventory levels.
- The top 20 product combinations are concentrated in these three categories, underscoring their centrality to SuperMax’s revenue.

3. Pandemic-Driven Demand and Market Normalization
- 2020 saw an unprecedented surge in sales and units sold across all major categories, with Dish Care and Air Care sales nearly tripling compared to 2019. This reflects pandemic-driven demand for cleaning and hygiene products.
- In 2021, sales moderated but remained well above pre-pandemic levels, suggesting a new, higher baseline for these essential categories.

4. Pricing Dynamics and Consumer Sensitivity
- Average shelf prices increased steadily, especially for Bath Tissue (up 47% from 2020 to 2021). Some brands, such as Sharmin-123Corp and Southern-Warbucks Industries, pushed prices above $10 per unit, but did not achieve the highest sales volumes.
- Brands with competitive, mid-range pricing (notably Great V-Globex) consistently captured the largest share of sales and units sold, highlighting significant price sensitivity in high-volume categories.
- Value brands (e.g., B&W in Bath Tissue, Love Home-Glocal in Dish Care) maintained strong unit sales at very low price points, indicating a robust segment of price-conscious consumers.

5. Inventory Management and Supply Chain Resilience
- Inventory levels rose sharply in 2020 in response to demand spikes and remained elevated in 2021, reflecting proactive supply chain management.
- Leading brands maintained high inventory to support sustained demand, but some lower-performing brands also held substantial stock, suggesting potential overstocking or slower turnover that warrants attention.

6. Market Segmentation and Strategic Opportunities
- The coexistence of premium and value brands within each category points to a segmented market, with opportunities for both high-margin (premium) and high-volume (value) strategies.
- Premiumization is evident in rising average prices, but the data shows that volume leadership is achieved through competitive pricing rather than premium positioning.
- The 2020 demand spike underscores the importance of agile inventory and supply chain strategies to capitalize on market disruptions and prevent stockouts.

---

Strategic Recommendations

1. Optimize Pricing Strategies: Maintain competitive price points in high-volume categories to maximize sales and market share, while selectively leveraging premium offerings for margin growth.
2. Enhance Inventory Efficiency: Continuously monitor inventory turnover, especially for lower-performing brands, to minimize overstocking and free up working capital.
3. Strengthen Supply Chain Agility: Build on the robust inventory management practices developed during the pandemic to ensure rapid response to future demand surges or market disruptions.
4. Leverage Brand Leadership: Invest in marketing and loyalty programs for leading brands, particularly Great V-Globex, to reinforce market dominance and defend against competitive encroachment.
5. Expand Segmented Offerings: Continue to serve both value-oriented and premium customer segments, tailoring promotions and product assortments to evolving consumer preferences.
6. Monitor Price Sensitivity: Regularly assess consumer response to price changes, especially in core categories like Bath Tissue, to avoid volume declines from over-aggressive price increases.

---

Conclusion
SuperMax Stores’ performance from 2019 to 2021 demonstrates the power of brand leadership, the impact of external demand shocks, and the critical role of pricing and inventory management. By balancing competitive pricing, supply chain agility, and targeted brand strategies, SuperMax is well-positioned to sustain growth and profitability in a dynamic market environment. Ongoing vigilance in inventory and pricing, coupled with a segmented approach to customer needs, will be key to maintaining and expanding market leadership. 
```

## 📦 Requirements
Here are key libraries:
```
pandas
sqlalchemy
openai
langchain
langchain-openai
langchain-community
langgraph
langchain-chroma
pypdf
```

### 🧠 Inspiration
This project draws from LangChain's Autonomous Agents, LangGraph's stateful flows, and real-world business data analysis workflows.

### 🙋 Support or Questions?
Feel free to raise an issue or open a discussion!




