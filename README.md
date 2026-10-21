# AI-SQL-Agent

Ask questions about a shop database in plain English. The application uses an OpenAI model to generate SQL, runs the query against SQLite, and explains the results. You can inspect the generated SQL and returned rows in the Streamlit interface.

## Requirements

- Python 3.10 or newer
- An OpenAI API key

## Setup

From the project folder, run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` and copy the configuration with `cp .env.example .env`.

Set `OPENAI_API_KEY` in `.env`. Keep that file private; it is excluded from Git. Each question makes two OpenAI API calls and may incur a charge.

## Run the application

```powershell
streamlit run app.py
```

The application creates `shop.db` with sample customer and order data on the first run. The database file is excluded from Git. Delete it to recreate the original data.

The [notebook](sql_agent_walkthrough.ipynb) contains the same database and question-answering flow. Launch it from the project folder with `jupyter notebook` so it uses the same `shop.db` file.

## Example questions

- How many orders are there?
- Who bought a monitor?
- What is the total sales amount by city?
- Which customer spent the most?

The application accepts a single `SELECT` statement from the model and shows the SQL and rows for review. Model-generated SQL and answers can be inaccurate, so check the results before relying on them.

## Subscribe

Subscribe to [NextGenQA Labs on YouTube](https://www.youtube.com/@NextGenQALabs) for more projects and updates.
