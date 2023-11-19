import functions_framework
import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

DB_INSTANCE = os.environ(INSTANCE)
DB_USER = os.environ(USER)
DB_PASS = os.environ(PASS)
DB_NAME = os.environ(NAME)
CLAUDE_KEY = os.environ(CLAUDE_KEY)
K_NEAREST = 10


def getconn():
    connector = Connector()
    conn = connector.connect(
        DB_INSTANCE, "pg8000", user=DB_USER, password=DB_PASS, db=DB_NAME
    )
    return conn


def getpool():
    return sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )


def embed_query(query):
    return model.encode(query)


def fetch_k_nearest(embedded_query, k):
    select = sqlalchemy.text(
        """
        SELECT context FROM legislation_vector_db_003
        ORDER BY embedding <-> (:embedding)
        LIMIT (:limit)
        """
    )

    pool = getpool()
    with pool.connect() as db_conn:
        return db_conn.execute(
            select, parameters={"embedding": embedded_query, "limit": k}
        ).fetchall()

def prompt(query, context):
    

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    QUERY_PARAM = "query"

    if request_json and QUERY_PARAM in request_json:
        query = request_json[QUERY_PARAM]
    else:
        return "Status 400"

    embedded_query = embed_query(query)
    context = fetch_k_nearest(embedded_query, K_NEAREST)

    return prompt(query, context)