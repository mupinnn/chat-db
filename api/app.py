import os
import sqlite3
from flask import Flask, g, jsonify, request
from dotenv import load_dotenv

load_dotenv()
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DATABASE = os.getenv('DATABASE_PATH', '/app/data/db.sqlite')

app = Flask(__name__)

PROMPT_QUERY = '''
    You are an expert SQL assistant. Your task is to generate a valid SQL query based on the user's question and the database schema provided.
    Use only the information in the schema context below. Ensure your query is syntactically correct, semantically accurate, and limited to SELECT queries only.

    Schema:
    {context}

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
    Show all orders made by a customer named Alice Sharma.

    SQL Query:
    SELECT
        o.order_id,
        o.amount,
        o.date,
        c.name,
        c.city
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    WHERE c.name = 'Alice Sharma';

    ---

    Example 2:
    Question:
    What is the total number of orders and total sales for April 1, 2025?

    SQL Query:
    SELECT
        COUNT(order_id) AS total_orders,
        SUM(amount) AS total_sales
    FROM orders
    WHERE date = '2025-04-01';

    ---

    Example 3:
    Question:
    List the top 5 customers by total spending.

    SQL Query:
    SELECT
        c.name,
        c.city,
        SUM(o.amount) AS total_spent
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    GROUP BY c.id
    ORDER BY total_spent DESC
    LIMIT 5;

    ---

    Example 4:
    Question:
    Find all orders made by customers from Mumbai.

    SQL Query:
    SELECT
        o.order_id,
        o.amount,
        o.date,
        c.name,
        c.city
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    WHERE c.city = 'Mumbai';

    ---

    Now use the same format to answer the user question below.

    Question:
    {question}

    SQL Query:
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

@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/api/sales', methods=['GET'])
def get_sales():
    db = get_db()

    limit = request.args.get('limit', 25, type=int)
    offset = request.args.get('offset', 0, type=int)

    query = 'SELECT * FROM coffee_sales WHERE 1=1 ORDER BY datetime DESC LIMIT ? OFFSET ?'
    cursor = db.execute(query, [limit, offset])
    sales = [dict(row) for row in cursor.fetchall()]

    return jsonify({
        'data': sales,
        'count': len(sales),
        'limit': limit,
        'offset': offset
    })

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.getenv('PORT', 5000))

    if FLASK_ENV == 'development':
        app.run(host=host, port=port, debug=True)
    else:
        app.run(host=host, port=port)
