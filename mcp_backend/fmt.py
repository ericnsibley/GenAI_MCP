import json 

TABLE_CONFIG_FILE = '../mcp_backend/table_config.json'
TABLE_CONFIG: dict | None = None
with open(TABLE_CONFIG_FILE, 'r') as infile: 
    TABLE_CONFIG = json.load(infile)


def format_table_name(table_name: str) -> str:
    table_description: str = TABLE_CONFIG.get(table_name, '')
    return f"<strong>Table:</strong> `{table_name}`<br>{table_description}"


def format_columns_as_markdown(columns: list[dict]) -> str:
    lines = [
        "| Column | Type |",
        "|--------|------|"
    ]
    for col in columns:
        lines.append(
            f"| {col['name']} | {col['type']} |"
        )
    return "<br>".join(lines)


def format_table_rows_as_markdown(table_name: str, rows: list[dict], max_cols: int = 10) -> str:
    if not rows:
        return f"<strong>Table:</strong> `{table_name}` is empty."

    header = list(rows[0].keys())[:max_cols]
    lines = [f"<strong>First {len(rows)} rows from `{table_name}`</strong>", "| " + " | ".join(header) + " |"]
    lines.append("|" + "|".join("---" for _ in header) + "|")

    for row in rows:
        line = [format_cell(row.get(col)) for col in header]
        lines.append("| " + " | ".join(line) + " |")

    return "<br>".join(lines)


def format_cell(value) -> str:
    if value is None:
        return "NULL"
    elif isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
