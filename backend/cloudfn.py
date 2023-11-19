import functions_framework
import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from sentence_transformers import SentenceTransformer
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

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
        SELECT file_name, context FROM legislation_vector_db_003
        ORDER BY embedding <-> (:embedding)
        LIMIT (:limit)
        """
    )

    pool = getpool()
    with pool.connect() as db_conn:
        result = db_conn.execute(
            select, parameters={"embedding": embedded_query, "limit": k}
        ).fetchall()

    return [str({str(row[0]): str(row[1])}) for row in result]


def prompt(query, context):
    input = f"""
        \n\nHuman: Here is my question: {query};
        Here is some context and data for you to
        answer my question with- when answering,
        please be sure to reference this data exactly.
        Always include the file name (txt) key. Context: 
        {context}\n\nAssistant:
        """

    anthropic = Anthropic(api_key=CLAUDE_KEY)
    return anthropic.completions.create(
        model="claude-2", max_tokens_to_sample=5000, prompt=input
    )


@functions_framework.http
def answer_query(request):
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
