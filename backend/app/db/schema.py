from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Columns added after the first release. create_all does not alter existing tables.
_ADDITIONS: dict[str, list[tuple[str, str, str]]] = {
    "projects": [
        ("owner_id", "VARCHAR(64) NOT NULL DEFAULT 'local'", "VARCHAR(64) NOT NULL DEFAULT 'local'"),
        ("selected_generation_id", "VARCHAR(36)", "VARCHAR(36)"),
        ("brand_kit_id", "VARCHAR(36)", "VARCHAR(36)"),
        ("creator_profile_id", "VARCHAR(36)", "VARCHAR(36)"),
        ("channel_id", "VARCHAR(36)", "VARCHAR(36)"),
        ("creative_style", "VARCHAR(32) NOT NULL DEFAULT 'cinematic'", "VARCHAR(32) NOT NULL DEFAULT 'cinematic'"),
        ("audience_brief", "JSON", "JSON"),
        ("research_brief", "JSON", "JSON"),
        ("shared", "BOOLEAN NOT NULL DEFAULT 0", "BOOLEAN NOT NULL DEFAULT false"),
    ],
    "concepts": [
        ("image_prompt", "TEXT", "TEXT"),
        ("archived", "BOOLEAN NOT NULL DEFAULT 0", "BOOLEAN NOT NULL DEFAULT false"),
    ],
    "generations": [
        ("variation_axis", "VARCHAR(32)", "VARCHAR(32)"),
        ("source_generation_id", "VARCHAR(36)", "VARCHAR(36)"),
        ("impressions", "INTEGER NOT NULL DEFAULT 0", "INTEGER NOT NULL DEFAULT 0"),
        ("clicks", "INTEGER NOT NULL DEFAULT 0", "INTEGER NOT NULL DEFAULT 0"),
    ],
    "agent_runs": [
        ("input_tokens", "INTEGER", "INTEGER"),
        ("output_tokens", "INTEGER", "INTEGER"),
    ],
}


def sync_schema(engine: Engine) -> None:
    inspector = inspect(engine)
    names = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table, columns in _ADDITIONS.items():
            if table not in names:
                continue
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, sqlite_type, postgres_type in columns:
                if name in existing:
                    continue
                column_type = postgres_type if engine.dialect.name == "postgresql" else sqlite_type
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {column_type}"))
        if "projects" in names and _has_column(inspector, "projects", "privacy_mode"):
            connection.execute(text("ALTER TABLE projects DROP COLUMN privacy_mode"))


def _has_column(inspector, table: str, column: str) -> bool:
    return any(item["name"] == column for item in inspector.get_columns(table))
