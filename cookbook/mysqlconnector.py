import mysql.connector
import pandas as pd
import re

print("✅ Deane’s MySQL Connector V39 — has query_value function ")


# ============================================================
# GLOBAL STATE
# ============================================================
CURRENT_DB = None
GLOBAL_SQL_CONFIG = None


# ============================================================
# APPLY GLOBAL CONFIG
# ============================================================
def set_global_config(config):
    """Apply default connection settings (no default DB required)."""
    global GLOBAL_SQL_CONFIG, CURRENT_DB
    GLOBAL_SQL_CONFIG = config
    CURRENT_DB = config.get("database")  # may be None


# ============================================================
# MAIN CONNECTOR CLASS
# ============================================================
class mysqlconnector:
    def __init__(self, query, host, user, password, database=None, params=None):
        global CURRENT_DB

        self.df = pd.DataFrame()
        self.result = []
        self.columns = []

        # -----------------------------
        # CLEAN SQL INPUT
        # -----------------------------
        cleaned_query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        cleaned_query = "\n".join(
            line for line in cleaned_query.splitlines()
            if not line.strip().startswith("#")
        )

        if not isinstance(cleaned_query, str):
            cleaned_query = str(cleaned_query)

        cleaned_query = cleaned_query.strip()
        self.query = cleaned_query

        # Allow multi-statement SQL
        statements = [s.strip() for s in self.query.split(';') if s.strip()]

        # Start with last DB known
        current_db = CURRENT_DB or database

        # Params apply ONLY to last SQL statement
        params_list = [None] * len(statements)
        if params is not None:
            params_list[-1] = params

        # ============================================================
        # EXECUTE EACH STATEMENT
        # ============================================================
        for i, stmt in enumerate(statements):

            # -----------------------------
            # USE database;
            # -----------------------------
            use_match = re.match(r'(?i)^USE\s+`?([A-Za-z0-9_\-$]+)`?$', stmt)
            if use_match:
                current_db = use_match.group(1)
                CURRENT_DB = current_db
                print(f"📦 Switched default DB to: {CURRENT_DB}")
                continue

            is_last = (i == len(statements) - 1)

            # -----------------------------
            # CONNECT
            # -----------------------------
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=current_db or None
            )
            cursor = conn.cursor(buffered=True)

            try:
                # -----------------------------
                # EXECUTE (single or many)
                # -----------------------------
                if params_list[i] is not None:

                    # 🔥 MASS INSERT SUPPORT (NEW)
                    if isinstance(params_list[i], list):
                        cursor.executemany(stmt, params_list[i])
                    else:
                        cursor.execute(stmt, params_list[i])

                else:
                    cursor.execute(stmt)

                # -----------------------------
                # SELECT (last statement only)
                # -----------------------------
                if is_last and cursor.description:
                    self.columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()

                    self.result = [dict(zip(self.columns, row)) for row in rows]
                    df = pd.DataFrame(self.result)

                    # Convert int-like floats → Int64
                    for col in df.columns:
                        if pd.api.types.is_float_dtype(df[col]):
                            s = df[col]
                            if (s.dropna() % 1 == 0).all():
                                df[col] = s.astype("Int64")

                    self.df = df.convert_dtypes()
                    #print("✅ Final SELECT returned rows.")

                else:
                    conn.commit()

            except Exception as e:
                print(f"❌ SQL Error in statement {i+1}: {e}")
                self.df = pd.DataFrame()

            finally:
                try:
                    cursor.close()
                    conn.close()
                except:
                    pass

    # ============================================================
    # OUTPUT FORMATS
    # ============================================================
    def to_df(self):
        return self.df

    def to_dict(self):
        return self.df.to_dict(orient='records')

    def to_json(self):
        return self.df.to_json(orient='records')

    def to_jinja(self):
        """Convert DF to Jinja-friendly dict (safe for templates)."""
        df_clean = self.df.copy()

        for col in df_clean.columns:

            if pd.api.types.is_datetime64_any_dtype(df_clean[col]) or \
               pd.api.types.is_timedelta64_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype(str)

            elif pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].apply(
                    lambda x: float(x) if pd.notnull(x) else None
                )

            elif df_clean[col].dtype == object:
                df_clean[col] = df_clean[col].apply(
                    lambda x: x.decode() if isinstance(x, (bytes, bytearray)) else x
                )

        return df_clean.to_dict(orient='records')

    def head(self, n=5):
        return self.df.head(n)

    def __repr__(self):
        return repr(self.df)

    def __str__(self):
        return str(self.df)

    def __getattr__(self, name):
        return getattr(self.df, name)


# ============================================================
# WRAPPER: run_sql()
# ============================================================
def run_sql(query, params=None):
    global GLOBAL_SQL_CONFIG
    if GLOBAL_SQL_CONFIG is None:
        raise Exception("❌ SQL_CONFIG not set. Call set_global_config(SQL_CONFIG) first.")

    return mysqlconnector(
        query,
        host=GLOBAL_SQL_CONFIG["host"],
        user=GLOBAL_SQL_CONFIG["user"],
        password=GLOBAL_SQL_CONFIG["password"],
        database=GLOBAL_SQL_CONFIG.get("database"),
        params=params
    )


# ============================================================
# ENV SETUP
# ============================================================
import os
import sys

base_dir = os.getcwd() + '/'

sys.path.append('/home/comradmarx/python_cook_book/')
sys.path.append('/Users/deanemarks/Desktop/python_cook_book')

if 'deanemarks' in base_dir:
    SQL_CONFIG = {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", "")
    }

elif 'comradmarx' in base_dir:
    SQL_CONFIG = {
        "host": os.environ.get("MYSQL_HOST", "comradmarx.mysql.pythonanywhere-services.com"),
        "user": os.environ.get("MYSQL_USER", "comradmarx"),
        "password": os.environ.get("MYSQL_PASSWORD", "")
    }

else:
    SQL_CONFIG = {
        "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", "")
    }


set_global_config(SQL_CONFIG)













# ============================================================
# HELPER: query_value()
# ============================================================
def query_value(query, params=None):
    """
    Execute SQL and return the first column of the first row.
    Returns None if no rows.
    """
    result = run_sql(query, params).to_dict()
    if not result:
        return None
    return next(iter(result[0].values()))
