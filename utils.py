import os
import logging
import contextlib
from functools import wraps
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor


ERROR_LOG_FILE = os.path.dirname(os.path.abspath(__file__)) + "/error.log"


logger = logging.getLogger("application")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(ERROR_LOG_FILE)
formatter = logging.Formatter("\n\n%(asctime)s - %(message)s \n\n")
fh.setFormatter(formatter)
logger.addHandler(fh)


class InternalServerError(Exception):
    pass


class BadRequest(Exception):
    pass


class ValidationException(Exception):
    """
    exception for Cerberus
    """


DB_SERVER_URL = os.getenv("DATABASE_HOST", "127.0.0.1")
DB_SERVER_PORT = int(os.getenv("DATABASE_PORT", "5432"))

DB_SERVER_USER = os.getenv("DATABASE_SERVER_USER")
DB_SERVER_PASS = os.getenv("DATABASE_SERVER_PASSWORD")

DB_NAME = os.getenv("DB_NAME", "ticket_system")
DB_TEST_NAME = os.getenv("DB_TEST_NAME", "ticket_system_test")

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "user")
ENVIROMENT = os.getenv("ENVIROMENT", "test")
MEMCACHE_URL = os.getenv("MEMCACHE_URL", "127.0.0.1")
MEMCACHE_PORT = os.getenv("MEMCACHE_PORT", "11211")


postgres_pool = ThreadedConnectionPool(
    1,
    100,
    "postgresql://{0}:{1}@{2}:{3}/{4}".format(
        DB_USER,
        DB_PASSWORD,
        DB_SERVER_URL,
        DB_SERVER_PORT,
        (DB_TEST_NAME if ENVIROMENT == "test" else DB_NAME),
    ),
)


@contextlib.contextmanager
def get_db_connection():
    try:
        connection = postgres_pool.getconn()
        yield connection
    finally:
        postgres_pool.putconn(connection)


@contextlib.contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()


def error_handler(default_message=None, default_code=None):
    def decorator(func):
        @wraps(func)
        def wrapped(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                return result
            except IndexError:
                return "Object not found", 404
            except BadRequest as e:
                logger.exception(str(e))
                return str(e), 400
            except ValidationException as e:
                logger.exception(str(e))
                return "Request Validation error: {0}".format(str(e)), 400
            except Exception as e:
                logger.exception(str(e))
                return "Internal Server Error", 500

        return wrapped

    return decorator
