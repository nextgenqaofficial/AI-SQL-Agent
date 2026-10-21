# AI-SQL-Agent

A 15-minute beginner demo.

Ask questions about a tiny shop database in plain English. LangChain and an OpenAI model write SQL, SQLite runs it, and the model explains the rows. The generated SQL is shown in the app so participants can see what happened.

## Setup

Use Python 3.10 or newer, then run these commands from this folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace `your_api_key_here` with your OpenAI API key. The two model calls per question use the OpenAI API and may incur a small charge. Never show the key on screen in the video.

On macOS or Linux, activate with `source .venv/bin/activate` and copy with `cp .env.example .env`.

## Suggested video flow

1. **Minutes 0–2:** Open `sql_agent_walkthrough.ipynb`; explain the two tables and sample rows.
2. **Minutes 2–6:** Run the setup and database cells. Ask `Which customer spent the most?` and inspect the generated SQL, rows, and answer.
3. **Minutes 6–10:** Walk through `ask_database`: question → SQL → SQLite rows → answer. Try `Total sales by city?`.
4. **Minutes 10–15:** Open `app.py`. Its first three marked sections are copied exactly from the notebook. Explain the final Streamlit UI section, then run:

   ```powershell
   streamlit run app.py
   ```

The SQLite file `shop.db` is created automatically on the first run. Delete it to start again with fresh sample data. The notebook should be launched from this project folder with `jupyter notebook` so both files use the same `shop.db`.

## Example questions

- How many orders are there?
- Who bought a monitor?
- What is the total sales amount by city?
- Which customer spent the most?

This is a teaching demo with a fixed sample database. The code checks that the generated SQL starts with `SELECT` and has no second statement, but model-generated SQL can still be inaccurate. Check the shown SQL and rows before trusting an answer.
