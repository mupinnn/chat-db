import os
import sqlite3
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DATABASE = os.getenv('DATABASE_PATH', '/app/data/db.sqlite')

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
CORS(app, origins=[os.getenv("ALLOWED_CORS_ORIGIN")])

PROMPT_QUERY = '''
    You are an expert SQL assistant. Your task is to generate a valid SQL query based on the user's question and the database schema provided.
    Use only the information in the schema context below. Ensure your query is syntactically correct, semantically accurate, and limited to SELECT queries only.

    The SQL database has the table "coffee_sales" and the following columns schema:
    - date:  Date of purchasing
    - datetime: Datetime of purchasing
    - cash_type: Cash or card purchasing
    - card: Anonymous card number
    - money: Amount of money in Ukrainian hryvnias
    - coffee_name: Coffe type

    Guidelines:
    - Only use tables, columns, and relationships defined in the schema.
    - Do not invent column or table names. If something is unclear, write a SQL comment.
    - Use JOINs where necessary to combine data across tables.
    - Use GROUP BY and aggregate functions when the question implies summarization.
    - Always use LIMIT in queries requesting a preview or top-N results.
    - Format queries cleanly with appropriate indentation.
    - Never write DELETE, INSERT, UPDATE, DROP, or DDL statements.
    - Prefer using table aliases (`c` for customers, `o` for orders) when dealing with multiple tables.
    - All dates must follow 'YYYY-MM-DD' format.

    ---

    Here are some examples to guide your output:

    Example 1:
    Question:
    Get total sales and revenue per coffee type on March 2024

    SQL Query:
    SELECT
        coffee_name,
        COUNT(*) AS total_orders,
        SUM(money) AS total_revenue,
        AVG(money) AS avg_price,
        MIN(datetime) AS first_order,
        MAX(datetime) AS last_order
    FROM coffee_sales
    WHERE date BETWEEN '2024-03-01' AND '2024-03-31'
    GROUP BY coffee_name
    ORDER BY total_revenue DESC;

    ---

    Example 2:
    Question:
    What is the total number of payments that using card and the amount above 32?

    SQL Query:
    SELECT
        id,
        datetime,
        coffee_name,
        card,
        money
    FROM coffee_sales
    WHERE cash_type = 'card'
      AND money >= 32.00
      AND card IS NOT NULL
    ORDER BY datetime DESC;

    ---

    Example 3:
    Question:
    Get today sales summary with payment type breakdown.

    SQL Query:
    SELECT
        date,
        COUNT(*) AS total_transactions,
        SUM(money) AS daily_revenue,
        SUM(CASE WHEN cash_type = 'card' THEN 1 ELSE 0 END) AS card_payments,
        SUM(CASE WHEN cash_type = 'cash' THEN 1 ELSE 0 END) AS cash_payments,
        SUM(CASE WHEN cash_type = 'card' THEN money ELSE 0 END) AS card_revenue,
        SUM(CASE WHEN cash_type = 'cash' THEN money ELSE 0 END) AS cash_revenue
    FROM coffee_sales
    GROUP BY date
    ORDER BY date DESC;

    ---

    The output should not include ``` or the word "sql".

    Now use the same format to answer the user question below.

    Question:
    {question}
'''

PROMPT_HUMAN_FRIENDLY = '''
    You are a helpful assistant. Based on the user's question, the generated SQL query, and the SQL result, write a clear and natural language answer.

    Guidelines:
    - Do not repeat the SQL query.
    - Focus only on summarizing the result in plain language.
    - If the result is a list or table, summarize it or highlight the top results.
    - Avoid guessing or adding information not in the SQL result.

    Previously, you were asked: "{question}"
    The query result from the database is: "{result}".

    Please respond to the customer in a humane and friendly and detailed manner.
    For example, if the question is "What is the biggest sales of product A?",
    you should answer "The biggest sales of product A is 1000 USD".
'''

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS coffee_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            datetime DATETIME NOT NULL,
            cash_type TEXT NOT NULL CHECK(cash_type IN ('card', 'cash')),
            card TEXT,
            money REAL NOT NULL,
            coffee_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.commit()

def get_gemini_response(prompt):
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return None

def read_sql_query(query):
    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        return rows
    except Exception as e:
        return None
    finally:
        cursor.close()

    return None

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/sales', methods=['GET'])
def get_sales():
    db = get_db()

    limit = request.args.get('limit', 25, type=int)
    offset = request.args.get('offset', 0, type=int)

    sales_cursor = db.execute(
        'SELECT * FROM coffee_sales WHERE 1=1 ORDER BY datetime DESC LIMIT ? OFFSET ?',
        [limit, offset]
    )
    sales = [dict(row) for row in sales_cursor.fetchall()]

    count_cursor = db.execute('SELECT COUNT(*) AS count FROM coffee_sales')
    count = dict(count_cursor.fetchone())

    return jsonify({
        'data': sales,
        'count': count['count'],
        'limit': limit,
        'offset': offset
    })

@app.route('/api/ask', methods=['POST'])
def ask_sales():
    data = request.get_json()
    required_fields = ['q']

    for field in required_fields:
        if field not in data:
            return jsonify({ 'message': f'{field} is required' }), 400

    question = data['q']
    sql_query = get_gemini_response(PROMPT_QUERY.format(question=question))
    if (sql_query):
        result = read_sql_query(sql_query)
        if result:
            human_friendly_response = get_gemini_response(PROMPT_HUMAN_FRIENDLY.format(question=question, result=result))
            return jsonify({ 'data': human_friendly_response })

    return jsonify({ 'message': "Can't query the data at the moment." }), 500

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.getenv('PORT', 5000))

    if FLASK_ENV == 'development':
        app.run(host=host, port=port, debug=True)
    else:
        app.run(host=host, port=port)
