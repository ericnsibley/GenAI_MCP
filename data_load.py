import pandas as pd 
import sqlite3 
import os 


def load_data(conn: sqlite3.Connection) -> None:
    prefix = "./zillow_data"
    for filename in os.listdir(prefix):
        file_path = f"{prefix}/{filename}" 
        filename_without_extension = ''.join(filename.split('.')[:-1])
        df = pd.read_csv(file_path)
        print(f"{filename_without_extension}: {df.head()}")
        rows = df.to_sql(filename_without_extension, conn, if_exists="replace") 
        print(f"{rows} rows were written to table {filename_without_extension}")


def list_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for name in tables:
        print(f"- {name[0]}")


if __name__ == "__main__":
    conn = sqlite3.connect("Zillow_data")
    load_data(conn)
    list_tables(conn)
    conn.close()