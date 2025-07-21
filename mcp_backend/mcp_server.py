from mcp.server.fastmcp import FastMCP
from sqlite_driver import SqliteDriver
import fmt

SERVER_NAME = "real_estate_mcp_server"
SQLITE_DB = "Zillow_data"
PORT = 5000
HOST = "127.0.0.1"

mcp = FastMCP(
    name=SERVER_NAME,
    host=HOST,
    port=PORT,
    timeout=30 
)


def get_sql_driver(db_file: str = SQLITE_DB) -> SqliteDriver:
    return SqliteDriver(f"../{db_file}")


@mcp.tool()
async def describe_tables(db_name: str = "main") -> str:
    """List all tables in the database with their descriptions and columns"""
    try: 
        sql_driver = get_sql_driver()
        tables = sql_driver.execute_query( f"SELECT name FROM {db_name}.sqlite_master WHERE type='table'" )
        
        s = []
        for table in tables or []:
            table_name = table.cells.get('name')
            s.append( fmt.format_table_name(table_name) ) 

        return '<br><br>'.join(s)
    except Exception as e: 
        print(f"Exception: {e}")
        return ''


@mcp.tool()
async def inspect_table(table_name: str, limit: int = 10, db_name: str = "main") -> str:
    """Dump schema and sample rows from a table"""
    try:
        sql_driver = get_sql_driver()
        # Try to sort by ForecastDate if the column exists
        cols = sql_driver.execute_query(f"PRAGMA {db_name}.table_info({table_name})")
        col_names = [c.cells.get('name') for c in cols]
        if 'ForecastDate' in col_names:
            rows = sql_driver.execute_query(f"SELECT * FROM {db_name}.{table_name} ORDER BY ForecastDate DESC LIMIT ?", [limit])
        else:
            rows = sql_driver.execute_query(f"SELECT * FROM {db_name}.{table_name} LIMIT ?", [limit])

        table_str = fmt.format_table_name(table_name)
        col_str = fmt.format_columns_as_markdown([c.cells for c in cols])
        row_str = fmt.format_table_rows_as_markdown(table_name, [r.cells for r in rows])

        return f"{table_str}<br><br>{col_str}<br><br>{row_str}"
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    try:
        print(f"Starting MCP server {SERVER_NAME} on {HOST}:{PORT}")
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
