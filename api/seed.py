import os
import sys
import csv
import sqlite3
from datetime import datetime

DATABASE = os.getenv('DATABASE_PATH', '/app/data/db.sqlite')
DEFAULT_CSV_PATH = os.getenv('CSV_SEED_FILE', '/app/data/seed.csv')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    conn.execute('''
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
    conn.commit()

def parse_date(date_str):
    """Parse date string to ISO format (YYYY-MM-DD)."""
    formats = [
        '%Y-%m-%d',      # 2024-01-15
        '%d/%m/%Y',      # 15/01/2024
        '%m/%d/%Y',      # 01/15/2024
        '%d-%m-%Y',      # 15-01-2024
        '%Y/%m/%d',      # 2024/01/15
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str. strip(), fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")

def check_existing_data(conn):
    cursor = conn.execute('SELECT COUNT(*) FROM coffee_sales')
    return cursor.fetchone()[0]

def seed_from_csv(conn, csv_path):
    if not os.path. exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    records_inserted = 0
    errors = 0

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            # Auto-detect delimiter
            sample = file.read(2048)
            file.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.DictReader(file, dialect=dialect)
            except csv.Error:
                reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 = header)
                try:
                    # Parse and validate data
                    date_value = parse_date(row. get('date', ''))
                    datetime_value = row.get('datetime', '').strip()

                    if not datetime_value:
                        print(f"  Row {row_num}:  Missing datetime, skipping...")
                        errors += 1
                        continue

                    # Validate cash_type
                    cash_type = row.get('cash_type', '').strip().lower()
                    if cash_type not in ('card', 'cash'):
                        print(f"  Row {row_num}:  Invalid cash_type '{cash_type}', skipping...")
                        errors += 1
                        continue

                    # Card can be null for cash payments
                    card = row.get('card', '').strip() or None

                    # Parse money as float
                    money_str = row.get('money', '0').strip()
                    money = float(money_str. replace(',', '.'))

                    # Coffee name
                    coffee_name = row.get('coffee_name', '').strip()

                    if not coffee_name:
                        print(f"  Row {row_num}: Missing coffee_name, skipping...")
                        errors += 1
                        continue

                    # Insert record
                    conn. execute('''
                        INSERT INTO coffee_sales (date, datetime, cash_type, card, money, coffee_name)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (date_value, datetime_value, cash_type, card, money, coffee_name))

                    records_inserted += 1

                except (ValueError, KeyError) as e:
                    print(f"  Row {row_num}: Error - {e}, skipping...")
                    errors += 1
                    continue

            conn.commit()

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        conn.rollback()
        sys.exit(1)

    return records_inserted, errors

def main():
    conn = get_db()
    init_db(conn)

    existing_count = check_existing_data(conn)

    if existing_count > 0:
        print(f"Database already contains {existing_count} records.")
        conn.close()
        sys.exit(0)

    print(f"Seeding from: {DEFAULT_CSV_PATH}")
    inserted, errors = seed_from_csv(conn, DEFAULT_CSV_PATH)

    print()
    print("=" * 50)
    print("Seeding Complete!")
    print("=" * 50)
    print(f"Records inserted: {inserted}")
    print(f"Errors/skipped:    {errors}")
    print(f"Total records:    {check_existing_data(conn)}")

    conn.close()

if __name__ == '__main__':
    main()
