from functools import wraps
import psycopg2
from config import (
    PG_HOST, PG_NAME, PG_PASSWORD, PG_PORT, PG_USER
)

# Operaciones de lectura
def with_cursor(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_NAME,
                user=PG_USER,
                password=PG_PASSWORD,
                port=PG_PORT,
            )
            conn.autocommit = True
            
            cursor = conn.cursor()
            result = f(args[0], cursor, *args[1:], **kwargs)
            return(result)
        except (Exception, psycopg2.DatabaseError) as e:
            print("Error:", e)
            if conn: conn.rollback()
        finally:
            if conn is not None: conn.close()
    return wrapper

def with_transactions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_NAME,
                user=PG_USER,
                password=PG_PASSWORD,
                port=PG_PORT,
            )
            cursor = conn.cursor()
            result = f(args[0], cursor, *args[1:], **kwargs)
            conn.commit()
            return result
        except (Exception, psycopg2.DatabaseError) as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn is not None:
                cursor.close()
                conn.close()
    return wrapper