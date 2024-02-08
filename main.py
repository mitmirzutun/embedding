import collections.abc
import json
import llm
import os.path
import sqlite3
import subprocess
EMBEDDING_DB="embedding.db"

def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(x * x for x in b) ** 0.5
    return dot_product / (magnitude_a * magnitude_b)


def setup():
    con = sqlite3.connect(EMBEDDING_DB)
    cur = con.cursor()
    cur.execute("create table embedding(file, score)")
    cur.close()
    con.close()


def embed(file_name: str) -> None:
    if "'" in file_name:
        raise ValueError("file name is a SQL Injection attempt")
    if subprocess.run(["ls", EMBEDDING_DB], capture_output=True).returncode != 0:
        setup()
    file_name = os.path.relpath(file_name)
    con = sqlite3.connect(EMBEDDING_DB)
    cur = con.cursor()
    if cur.execute(f"select 1 from embedding where file='{file_name}'").fetchone() is not None:
        cur.close()
        con.close()
        return
    embedding_model = llm.get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    file = open(file_name)
    vector = embedding_model.embed(file.read())
    file.close()
    insert = "insert into embedding values ('"+file_name+"','"+json.dumps(vector)+"')"
    cur.execute(insert)
    con.commit()
    cur.close()
    con.close()


def grep_all_files(*paths: str) -> collections.abc.Iterator[str]:
    if len(paths) == 0:
        return
    if len(paths) != 1:
        for path in paths:
            yield from grep_all_files(path)
    path = os.path.abspath(paths[0])
    if os.path.isdir(path):
        ls_result = subprocess.run(["ls", path], capture_output=True).stdout.decode("utf8").strip().split("\n")
        for rel_path in ls_result:
            yield from grep_all_files(os.path.join(path, rel_path))
    if os.path.isfile(path):
        yield path


def plot() -> None:
    import matplotlib.pyplot
    data = []
    con = sqlite3.connect(EMBEDDING_DB)
    cur = con.cursor()
    magnitude_x = []
    magnitude_y = []
    result = cur.execute("select e1.file, e1.score, e2.file, e2.score from embedding e1" +
                         " cross join embedding e2 where e1.file!=e2.file")
    for (file1, score1, file2, score2) in result:
        array1 = json.loads(score1)
        array2 = json.loads(score2)
        data.append(cosine_similarity(array1, array2))
        magnitude_x.append(sum(x*x for x in array1))
        magnitude_y.append(sum(x*x for x in array2))
    cur.close()
    con.close()
    _figure, axes = matplotlib.pyplot.subplots(2, 2)
    axes[0, 0].scatter(range(len(data)), data)
    axes[0, 1].scatter(magnitude_x, magnitude_y)
    matplotlib.pyplot.savefig("embedding_visualized.png")
    matplotlib.pyplot.show()


def main():
    for path in grep_all_files("data", "scraping/textfiles"):
        embed(path)
    plot()
    # subprocess.run(["rm","embedding.db"])


if __name__ == "__main__":
    main()
