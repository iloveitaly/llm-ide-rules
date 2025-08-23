"""Database prompt command: Generate database schema prompts using llm-sql-prompt."""

import sys
from typing import Optional, List
import structlog
import typer
from typing_extensions import Annotated

logger = structlog.get_logger()

def db_prompt_main(
    database_url: Annotated[str, typer.Argument(help="Database URL connection string")],
    table_names: Annotated[Optional[List[str]], typer.Option("--table", "-t", help="Specific table names to include")] = None,
    all_tables: Annotated[bool, typer.Option("--all", help="Include all tables")] = False,
    include_data: Annotated[bool, typer.Option("--include-data", help="Include sample data")] = False,
    exclude_stats: Annotated[bool, typer.Option("--exclude-stats/--include-stats", help="Exclude PostgreSQL statistics tables")] = True,
) -> None:
    """Generate database schema prompts using llm-sql-prompt, excluding problematic PostgreSQL stats tables."""
    
    try:
        # Import llm_sql_prompt here to avoid import errors if not installed
        from llm_sql_prompt import postgres
    except ImportError:
        logger.error("llm-sql-prompt package not found. Install it with: uv add llm-sql-prompt")
        raise typer.Exit(1)
    
    # When exclude_stats is enabled and all_tables is True, we need to get table list first
    # and filter out stats tables to prevent pg_stat_statements errors
    if exclude_stats:
        if all_tables and not table_names:
            # We need to get the table list ourselves and filter it
            try:
                import psycopg
                
                with psycopg.connect(database_url) as conn:
                    with conn.cursor() as cursor:
                        # Get all user tables (not system tables)
                        cursor.execute("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                            ORDER BY table_name
                        """)
                        user_tables = [row[0] for row in cursor.fetchall()]
                        
                        if user_tables:
                            table_names = user_tables
                            all_tables = False  # We now have explicit table list
                            logger.info(f"Discovered {len(table_names)} user tables, excluding system stats tables")
                        else:
                            logger.warning("No user tables found in public schema")
                            
            except Exception as e:
                logger.warning(f"Could not pre-filter tables: {e}. Proceeding with original parameters.")
        
        elif table_names:
            # Filter explicit table names to remove any stats tables
            stats_tables = [
                "pg_stat_statements",
                "pg_stat_activity", 
                "pg_stat_database",
                "pg_stat_user_tables",
                "pg_stat_user_indexes",
                "pg_stat_user_functions",
                "pg_stat_io",
                "pg_stat_bgwriter",
                "pg_stat_wal_receiver",
                "pg_stat_subscription",
                "pg_stat_ssl",
                "pg_stat_gssapi",
                "pg_stat_archiver",
                "pg_stat_replication",
                "pg_stat_slru",
                "pg_stat_wal",
            ]
            
            original_count = len(table_names)
            table_names = [t for t in table_names if not any(t.startswith(stat) for stat in stats_tables)]
            
            if len(table_names) < original_count:
                filtered_count = original_count - len(table_names)
                logger.info(f"Filtered out {filtered_count} PostgreSQL statistics tables")
    
    try:
        # Call the postgres module function with filtered tables
        postgres.describe_database_and_table(database_url, table_names, all_tables, include_data)
    except Exception as e:
        if "pg_stat_statements" in str(e):
            logger.error(
                "PostgreSQL statistics tables require special configuration. "
                "Use --exclude-stats (default) to avoid this error, or configure your "
                "PostgreSQL instance to load pg_stat_statements via shared_preload_libraries."
            )
            raise typer.Exit(1)
        else:
            logger.error(f"Database operation failed: {e}")
            raise typer.Exit(1)