from typing import Any
import llm #type: ignore
import sqlite_utils
from promptflow import tool #type: ignore
from os.path import dirname, abspath, join
from json import JSONEncoder
parentdir = dirname(dirname(abspath(__file__)))
EMBEDDING_DB = join(parentdir, "embedding.db")

def trim(data: str):
    tmp=list(filter(lambda x: x!="",data.splitlines()))
    return "\n".join(tmp)

def generate(e: llm.embeddings.Entry):
    return (e.id)

@tool
def get_data(question: str) -> list:
    quembedding = llm.get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    quevector = quembedding.embed(question)
    EMBEDDING_COLLECTION=llm.Collection("cities",sqlite_utils.Database(EMBEDDING_DB),model_id="sentence-transformers/all-MiniLM-L6-v2")
    nearest_entries = EMBEDDING_COLLECTION.similar_by_vector(quevector,1,1)
    nearest_ids = [ generate(e) for e in nearest_entries]
    return nearest_ids

if __name__ == "__main__":
    model=llm.get_model("orca-mini-3b-gguf2-q4_0")
    print(model.prompt("Wo ist Tondorf?"))
    print(get_data("Tondorf"))