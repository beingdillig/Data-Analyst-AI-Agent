from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from sqlalchemy import create_engine, inspect
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Annotated, Sequence
import json
import time


pdf_path = "All_Domain_Data_Analysis_Queries.pdf"
pdf = PyPDFLoader(pdf_path)
documents = pdf.load()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
)
split_docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)

vectorstore = Chroma.from_documents(documents=split_docs, embedding=embeddings, collection_name="analysis")

retreiver = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

openai = ChatOpenAI(
    model_name="gpt-4.1",
    api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# State of the graph
class AgentState(TypedDict):
    db_uri : str
    query_result: List[dict]
    schema : List[str]
    analysis_plan : List[str]
    query_history : List[str]
    done : bool
    insights: List[str]
    message : Annotated[Sequence[BaseMessage], add_messages]



def connect_to_db(db_uri):
    engine = create_engine(db_uri)
    inspector = inspect(engine)
    return engine, inspector

def get_schema_summary(engine, inspector):
    schema_info = {}

    for table_name in inspector.get_table_names():
        columns_raw = inspector.get_columns(table_name)
        foreign_keys_raw = inspector.get_foreign_keys(table_name)
        df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", engine)

        # Convert SQLAlchemy types to strings
        columns = [
            {
                "name": col["name"],
                "type": str(col["type"])
            }
            for col in columns_raw
        ]

        foreign_keys = [
            {
                "constrained_columns": fk.get("constrained_columns"),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns")
            }
            for fk in foreign_keys_raw
        ]

        schema_info[table_name] = {
            "columns": columns,
            "foreign_keys": foreign_keys,
            "sample_data": df.to_dict(orient="records")
        }

    return schema_info



def fetch_schema(state: AgentState) -> AgentState:
    db_uri = state.get("db_uri")
    if not db_uri:
        raise ValueError("Missing 'db_uri' in state")

    engine, inspector = connect_to_db(db_uri)
    schema_dict = get_schema_summary(engine, inspector)

    # Optional: convert dict to pretty JSON string
    state["schema"] = json.dumps(schema_dict, indent=2)

    return state

def retreive_plan(state:AgentState) -> AgentState:
  system_prompt = SystemMessage(content="""You are data expert you just have to give the domain type of the data that has been given to you
  input:
  schema of the data.

  output:
  Retail / CPG (Consumer Packaged Goods) / FMCG Analytics
  """)

  schema = state['schema']
  response = openai.invoke([system_prompt,schema])
  print("Retreiving analysis plan...", response.content)
  docs = retreiver.invoke(response.content)
  page_contents = [doc.page_content for doc in docs]
  state["analysis_plan"] = page_contents
  return state

def queries_planner(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="""
You are the Query Planner node in a LangGraph-based autonomous Data Analyst AI Agent.

Your job is to intelligently generate **one highly informative SQL query at a time** based on:

- The analysis Plan given to you.
- A JSON-formatted schema (with table names, column names/types, foreign keys, and sample rows)
- A growing list of insight summaries from previously executed queries

---

🎯 Mindset: You're a **senior data analyst** optimizing for:
- High information gain per query
- Strategic dimension combinations
- Zero redundancy
- Strict query limit: **maximum 15 queries**

---

🧠 Your queries should:
- Use multiple dimensions (e.g., Year, Sector, Brand)
- Reveal trends, outliers, top contributors, pricing/inventory/sales patterns
- Build upon previous insights to deepen understanding

---

🚨 Very Important Output Rule:

🛑 **Do NOT include markdown, explanations, or formatting.**

✅ **ONLY return the raw SQL query** — exactly like this:
SELECT Year, Sector, Category, Brand, SUM("POS $ Sales") AS total_sales, SUM("POS Unit Sales") AS total_units
FROM sales
GROUP BY Year, Sector, Category, Brand
ORDER BY Year, total_sales DESC;

🛑 **NO**:
- Code blocks (e.g., ```sql)
- Commentary
- Descriptive text
- Explanations

Just the SQL query, nothing else.

---

If the previous query failed, correct the error and submit a fixed query.
Do not repeat the same logic.

You are allowed to generate **only 20 total queries**, so make each one count, Ask most informative queries.
""")
    print("Thinking about the next query...")
    time.sleep(14)
    schema_string = state["schema"]
    query_history = "\n".join(state["query_history"])
    analysis = "\n".join(state["analysis_plan"])

    if state["insights"]:
      if len(state['insights']) >=15:
        print("Stopping after 15 queries.")
        state["query_history"].append("DONE")
        return state
      else:
        summarized_insights_string = "".join(state["insights"][-1])
        user_message = HumanMessage(content=f"""Schema:\n{schema_string}\n
    Last successful or failed query:\n{summarized_insights_string}\n
    Past query attempts:\n{query_history}\n AnalysisPlan:\n{analysis}""")
    else:
        user_message = HumanMessage(content=f"""Schema:\n{schema_string}\n
    Past query attempts:\n{query_history} \n AnalysisPlan:\n{analysis}""")

    response = openai.invoke([system_prompt, user_message])

    # Save the queries in state
    state["query_history"].append(response.content)
    print("Next_query: ", state["query_history"][-1])
    return state


def query_runner(state: AgentState) -> AgentState:
    query_result = state.get("query_result")
    query = state["query_history"][-1].strip()
    db_uri = state["db_uri"]

    # 💡 STOP CONDITION
    if query.upper() == "DONE":
        print("Query Planner signaled completion. No query executed.")
        result = {
            "query": query,
            "success": True,
            "result": [],
            "note": "Planner returned DONE. No further queries to execute."
        }
        query_result.append(result)
        state["query_result"] = query_result
        state["done"] = True  # 👈 Optional flag you can use in conditional logic
        return state

    # Otherwise, proceed with SQL execution
    engine = create_engine(db_uri)
    try:
        df = pd.read_sql(query, engine)
        result = {
            "query": query,
            "success": True,
            "result": df.to_dict(orient="records")
        }
    except SQLAlchemyError as e:
        result = {
            "query": query,
            "success": False,
            "error": str(e)
        }

    query_result.append(result)
    state["query_result"] = query_result
    return state


def summarizer(state: AgentState) -> AgentState:
  result = state['query_result'][-1]
  system_prompt = SystemMessage(content="""
You are the Summarizer node in a LangGraph-based autonomous Data Analyst AI Agent.

You will receive the **result of a previously executed SQL query** in structured JSON format.
Each result includes:
- The original SQL query
- Whether it was successful
- A table-like output (`result`) as a list of records (rows), if successful

Your job:
----------
Write a clear, concise **business summary** of the query result.


🎯 Your mindset is that of a **senior data analyst** who is:

- Efficiently exploring a dataset to extract **deep business insights**
- Maximizing information gain per query
- Strategically combining dimensions (e.g., Category + Brand + Year) in each query
- Avoiding shallow or redundant exploration (e.g., not just swapping one column name)
- Making sure each new query **builds on prior insights**

---

🧠 Prioritize SQL queries that:

- Uncover patterns across **multiple dimensions at once**
- Identify key drivers of metrics like sales, revenue, units sold, shelf price, or inventory
- Compare and contrast trends across categories, brands, sectors, time, and retailers
- Highlight outliers, anomalies, or dominant contributors
- Can compress multiple smaller "one-dimensional" queries into a single richer one
  (e.g., instead of separate queries by category and by brand, combine them)

Instructions:
- Analyze the data deeply to extract meaningful business insights
- Identify key trends, outliers, anomalies, dominant contributors, or correlations
- Prioritize clarity and usefulness for non-technical stakeholders, but allow for depth
- Write as much as needed to capture all valuable observations — don't restrict to 3–4 sentences
- If the result spans multiple dimensions (e.g., Year + Category + Brand), highlight noteworthy patterns across those combinations
- Avoid SQL jargon or technical language — use plain business-friendly language


Input format example:
[
  {
    "query": "SELECT Year, SUM(\"POS $ Sales\") AS total_sales FROM sales GROUP BY Year ORDER BY Year;",
    "success": true,
    "result": [
      {"Year": 2019, "total_sales": 4424179.80},
      {"Year": 2020, "total_sales": 13445469.91},
      {"Year": 2021, "total_sales": 12260626.12}
    ]
  }
]

Expected output:
From this query "SELECT Year, SUM(\"POS $ Sales\") AS total_sales FROM sales GROUP BY Year ORDER BY Year;" wo got that,
Sales peaked in 2020 at over $13.4M, followed by a decline in 2021 to $12.3M. The year 2019 saw significantly lower sales at $4.4M, indicating a major growth trend followed by slight contraction.

⚠️ Do not include markdown, tables, or SQL.
⚠️ If `success` is false, return a helpful error summary.
""")
  if state.get("done"):  # <- Skip if DONE was already triggered
        print("Skipping summarizer — DONE signal already received.")
        return state
  print("Summarizing the query_result please hold on!!")
  time.sleep(14)
  user_message = HumanMessage(content=json.dumps(result))
  # print(json.dumps(result))
  response = openai.invoke([system_prompt, user_message])
  # state["message"].append(HumanMessage(content=response.content))
  # if "insights" not in state:
  #   state["insights"] = []
  state["insights"].append(response.content)
  print("\n Summarized_insight: ", response.content, "\n")
  return state

def should_continue(state: AgentState):
  if state['done'] == True:
    return "final_insights"
  else:
    return "query_planner"


def final_insights(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="""
You are the Final Insights Generator in a LangGraph-based autonomous Data Analyst AI Agent.

You will receive a list of natural-language summaries, each derived from previously executed SQL queries on a business database. These summaries capture key trends, anomalies, metrics, and insights uncovered during the analysis.

Your task:
-----------
Write a **concise, strategic-level business report** that synthesizes the most important findings across all summaries.

Guidelines:
- Focus on **high-level insights** that matter to business stakeholders
- Highlight major patterns, trends, correlations, and outliers
- Avoid repeating all summaries verbatim — instead, **aggregate and connect** them
- Keep it professional, non-technical, and actionable
- Give detailed Insights so that action can be taken, accordingly.

Tone:
-----
Clear, confident, executive-level language. The kind of insight a data analyst would present to C-level executives or strategic decision-makers.

Do NOT:
- Include raw SQL or technical jargon
- Speculate beyond the data provided
""")
    print("Routing to final_insights — planner returned DONE.")

    all_summaries = "\n".join(state["insights"])
    user_message = HumanMessage(content=all_summaries)

    response = openai.invoke([system_prompt, user_message])
    print(f"\nAI Final Insight: {response.content} \n")

    return state




graph = StateGraph(AgentState)

graph.add_node("schema_fetcher", fetch_schema)
graph.add_node("retreiver", retreive_plan)
graph.add_node("query_planner", queries_planner)
graph.add_node("query_runner", query_runner)
graph.add_node("summarizer", summarizer)
graph.add_node("final_insights", final_insights)

graph.add_edge(START, "schema_fetcher")
graph.add_edge("schema_fetcher", "retreiver")
graph.add_edge("retreiver", "query_planner")
graph.add_edge("query_planner", "query_runner")
graph.add_edge("query_runner", "summarizer")

graph.add_conditional_edges(
    "summarizer",
    should_continue,
    {
        "final_insights": "final_insights",
        "query_planner": "query_planner"
    }
)
graph.add_edge("final_insights", END)

app = graph.compile()


db_uri = "sqlite:///sample.db"
initial_state = {
    "db_uri": db_uri,
    "query_history": [],
    "query_result": [],
    "schema": [],
    "done": False,
    "insights": [],
    "analysis_plan": [],
    "message": []
}

result = app.invoke(initial_state, config={"recursion_limit": 150})
