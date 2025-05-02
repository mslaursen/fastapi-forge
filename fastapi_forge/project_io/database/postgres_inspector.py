from typing import Any
from urllib.parse import urlparse

import psycopg2

from .protocols import DatabaseInspector


class PostgresInspector(DatabaseInspector):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.db_name = self.validate_connection_string(connection_string)
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()

    def validate_connection_string(self, connection_string: str) -> str:
        parsed = urlparse(connection_string)
        if parsed.scheme != "postgresql":
            msg = "Connection string must start with 'postgresql://'"
            raise ValueError(msg)

        db_name = parsed.path[1:]
        if not db_name:
            msg = "Database name not found in connection string"
            raise ValueError(msg)
        return db_name

    def fetch_enums(self, schema: str) -> dict[str, list[str]]:
        self.cursor.execute(
            """
            SELECT t.typname AS enum_name,
                   array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
            FROM pg_catalog.pg_type t
            JOIN pg_catalog.pg_enum e ON t.oid = e.enumtypid
            WHERE t.typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
            GROUP BY t.typname;
        """,
            (schema,),
        )
        return dict(self.cursor.fetchall())

    def fetch_enum_columns(self, schema: str) -> list[tuple[Any, ...]]:
        self.cursor.execute(
            """
            SELECT
                c.table_schema,
                c.table_name,
                c.column_name,
                format_type(a.atttypid, a.atttypmod) AS data_type,
                t.typname AS enum_type
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class cl ON a.attrelid = cl.oid
            JOIN pg_catalog.pg_namespace n ON cl.relnamespace = n.oid
            JOIN pg_catalog.pg_type t ON a.atttypid = t.oid
            JOIN information_schema.columns c ON
                c.table_schema = n.nspname AND
                c.table_name = cl.relname AND
                c.column_name = a.attname
            WHERE n.nspname = %s AND
                  t.typtype = 'e' AND
                  a.attnum > 0 AND
                  NOT a.attisdropped
            ORDER BY c.table_schema, c.table_name, c.column_name;
        """,
            (schema,),
        )
        return self.cursor.fetchall()

    def fetch_schema_tables(self, schema: str) -> list[tuple[Any, ...]]:
        self.cursor.execute(
            """
            SELECT
                c.table_schema,
                c.table_name,
                json_agg(
                    json_build_object(
                        'name', c.column_name,
                        'type', c.data_type,
                        'nullable', c.is_nullable = 'YES',
                        'primary_key', pk.column_name IS NOT NULL,
                        'unique', uq.column_name IS NOT NULL,
                        'default', null,
                        'foreign_key',
                            CASE WHEN fk_ref.foreign_table_name IS NOT NULL THEN
                                json_build_object(
                                    'field_name', c.column_name,
                                    'target_model', fk_ref.foreign_table_name,
                                    'referenced_field', fk_ref.foreign_column_name
                                )
                            ELSE NULL END
                    ) ORDER BY c.ordinal_position
                ) AS columns
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT kcu.table_schema, kcu.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    AND tc.table_name = kcu.table_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
            ) pk ON c.table_schema = pk.table_schema AND c.table_name = pk.table_name
                AND c.column_name = pk.column_name
            LEFT JOIN (
                SELECT kcu.table_schema, kcu.table_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    AND tc.table_name = kcu.table_name
                WHERE tc.constraint_type = 'UNIQUE'
                  AND tc.constraint_name NOT IN (
                      SELECT constraint_name
                      FROM information_schema.table_constraints
                      WHERE constraint_type = 'PRIMARY KEY'
                  )
            ) uq ON c.table_schema = uq.table_schema
                AND c.table_name = uq.table_name
                AND c.column_name = uq.column_name
            LEFT JOIN (
                SELECT kcu.table_schema, kcu.table_name, kcu.column_name,
                       ccu.table_schema AS foreign_table_schema,
                       ccu.table_name AS foreign_table_name,
                       ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    AND tc.table_name = kcu.table_name
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                    AND tc.table_schema = ccu.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
            ) fk_ref ON c.table_schema = fk_ref.table_schema
                AND c.table_name = fk_ref.table_name AND c.column_name = fk_ref.column_name
            WHERE c.table_schema = %s
            GROUP BY c.table_schema, c.table_name
            ORDER BY c.table_schema, c.table_name;
        """,
            (schema,),
        )
        return self.cursor.fetchall()

    def get_connection_string(self) -> str:
        return self.connection_string

    def get_db_name(self) -> str:
        return self.db_name

    def __del__(self) -> None:
        if hasattr(self, "cursor"):
            self.cursor.close()
        if hasattr(self, "conn"):
            self.conn.close()
