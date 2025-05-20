import pandas as pd 
import sqlite3 
import os 
import re 

SQLITE_DB = "Zillow_data"

def load_and_unpivot_data(conn: sqlite3.Connection) -> None:
    prefix = "./zillow_data"
    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

    for filename in os.listdir(prefix):
        file_path = f"{prefix}/{filename}" 
        table_name = ''.join(filename.split('.')[:-1])
        df = pd.read_csv(file_path)
        print(f"Loaded {table_name} with shape {df.shape}")

        id_columns = []
        date_columns = []
        # If the column name matches yyyy-mm-dd then unpivot it 
        for col in df.columns:
            if date_pattern.fullmatch(col):
                date_columns.append( col )
            else: 
                id_columns.append( col )

        if len(date_columns) == 0:
            print(f"Skipping unpivoting {filename}: no time series date columns found")
            df_unpivoted = df 
        else:
            # Melt to unpivot time series
            df_unpivoted = df.melt(
                id_vars=id_columns,
                value_vars=date_columns,
                var_name="ForecastDate",
                value_name="Value"
            )
            print(f"df: {df.head()}")
            print(f"df_unpivoted: {df_unpivoted.head()}")

        rows = df_unpivoted.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Wrote unpivoted table {table_name} with {rows} rows")


def load_data(conn: sqlite3.Connection) -> None:
    prefix = "./zillow_data"

    for filename in os.listdir(prefix):
        file_path = f"{prefix}/{filename}" 
        filename_without_extension = ''.join(filename.split('.')[:-1])
        df = pd.read_csv(file_path)
        print(f"Loaded {filename_without_extension} with shape {df.shape}")
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
    conn = sqlite3.connect(SQLITE_DB)
    load_and_unpivot_data(conn)
    list_tables(conn)
    conn.close()