"""A natural-language-to-SQL application for SQLite."""

# %% 1. Imports and settings (same cell in the notebook)
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Read the API key from .env without putting it in the code.
load_dotenv()
DB_PATH = Path("shop.db")


# %% 2. Create a small sample database (same cell in the notebook)
def setup_database():
    # Connecting creates shop.db if it does not exist yet.
    with sqlite3.connect(DB_PATH) as connection:
        # Create two tables: each order belongs to one customer.
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
        """)
        # Add a few rows so we have something to ask questions about.
        # INSERT OR IGNORE avoids duplicates when this function runs again.
        connection.executemany(
            "INSERT OR IGNORE INTO customers VALUES (?, ?, ?)",
            [(1, "Asha", "Mumbai"), (2, "Ravi", "Delhi"),
             (3, "Meera", "Mumbai"), (4, "Kabir", "Pune")],
        )
        connection.executemany(
            "INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?)",
            [(1, 1, "Keyboard", 1200), (2, 1, "Mouse", 600),
             (3, 2, "Monitor", 9000), (4, 3, "Keyboard", 1200),
             (5, 3, "Monitor", 9000), (6, 4, "Mouse", 600)],
        )


# %% 3. Turn a question into SQL, then answer it (same cell in the notebook)
def make_sql(question, model):
    # The schema tells the model which tables and columns it may use.
    schema = """customers(id INTEGER, name TEXT, city TEXT)
orders(id INTEGER, customer_id INTEGER, product TEXT, amount REAL)
orders.customer_id refers to customers.id. amount is in rupees."""

    # Ask the model to write one SQLite query for the question.
    sql_prompt = ChatPromptTemplate.from_messages([
        ("system", """You write SQLite queries for the shop database.
Use only this schema:\n{schema}
Return exactly one read-only SELECT query, with no markdown or explanation.
Use a JOIN when needed. Limit lists to 10 rows."""),
        ("human", "{question}"),
    ])
    sql = (sql_prompt | model | StrOutputParser()).invoke(
        {"schema": schema, "question": question}
    )
    return sql.strip().rstrip(";")


def get_rows(sql):
    # Reject responses that are not a single SELECT query.
    if not sql.upper().startswith("SELECT") or ";" in sql:
        raise ValueError("The model did not return one SELECT query.")

    # Open the database and fetch up to 10 matching rows.
    with sqlite3.connect(DB_PATH) as connection:
        # sqlite3.Row lets us use column names such as "name" and "amount".
        connection.row_factory = sqlite3.Row
        rows = connection.execute(sql).fetchmany(10)

        # Turn each SQLite row into a plain dictionary for display and the model.
        results = []
        for row in rows:
            results.append(dict(row))
        return results


def explain_rows(question, rows, model):
    # Ask the model to turn the returned rows into a short answer.
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the question briefly using only these SQL rows: {rows}. "
                   "If there are no rows, say no matching data was found."),
        ("human", "{question}"),
    ])
    return (answer_prompt | model | StrOutputParser()).invoke(
        {"rows": str(rows), "question": question}
    )


def ask_database(question):
    # A single question follows the same three steps every time.
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Set OPENAI_API_KEY in a .env file before asking a question.")

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    sql = make_sql(question, model)
    rows = get_rows(sql)
    answer = explain_rows(question, rows, model)
    return sql, rows, answer


# %% 4. Streamlit UI (added after the notebook walkthrough)
def main():
    import streamlit as st

    # Streamlit runs this function whenever someone interacts with the page.
    st.set_page_config(page_title="Ask the Shop Database", page_icon="🛒")
    st.title("🛒 Ask the Shop Database")
    st.caption("Ask a question in plain English. The app shows the SQL and its answer.")
    setup_database()

    # Collect one question from the user.
    with st.form("question_form"):
        question = st.text_input("Your question", placeholder="Which customer spent the most?")
        submitted = st.form_submit_button("Ask")

    st.caption("Try: How many orders are there? · Total sales by city? · Who bought a monitor?")
    if submitted and question.strip():
        try:
            # Reuse the same function that we tried in the notebook.
            with st.spinner("Asking the database..."):
                sql, rows, answer = ask_database(question.strip())
            st.subheader("Answer")
            st.write(answer)
            with st.expander("See the SQL and rows"):
                st.code(sql, language="sql")
                st.dataframe(rows)
        except Exception as error:
            st.error(str(error))


if __name__ == "__main__":
    main()
