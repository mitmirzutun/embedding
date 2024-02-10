import llm
import sqlite_utils
from promptflow import tool
from os.path import dirname, abspath, join
parentdir = dirname(dirname(abspath(__file__)))
EMBEDDING_DB = join(parentdir, "embedding.db")

@tool
def get_data(question: str) -> list:
    quembedding = llm.get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    quevector = quembedding.embed(question)
    EMBEDDING_COLLECTION=llm.Collection("cities",sqlite_utils.Database(EMBEDDING_DB),model_id="sentence-transformers/all-MiniLM-L6-v2")
    nearest_entries = EMBEDDING_COLLECTION.similar_by_vector(quevector)
    nearest_ids = [ e.id for e in nearest_entries]
    return nearest_ids

if __name__ == "__main__":
    print(get_data("Tondorf"))