import llm
import json
import sqlite_utils
import sqlite3
import subprocess
import collections.abc
import os.path
EMBEDDING_DB="embedding.db"
EMBEDDING_COLLECTION=llm.Collection("cities",sqlite_utils.Database("embedding.db"),model_id="sentence-transformers/all-MiniLM-L6-v2")


def embed(file_name: str) -> None:
    file=open(file_name).read()
    os.path.basename(file_name)
    EMBEDDING_COLLECTION.embed(os.path.basename(file_name).split(".")[0],file,store=True)
    EMBEDDING_COLLECTION.embed(os.path.relpath(file_name),file,store=True)
    pass


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


def main():
    for file in grep_all_files("scraping/textfiles"):
        embed(file)
    con = sqlite3.Connection(EMBEDDING_DB)
    cur = con.cursor()
    cities = list(map(lambda x: x[0],cur.execute("select id from embeddings").fetchall()))
    print(cities)
    for city in cities:
        break
        print(city)
        data=EMBEDDING_COLLECTION.similar_by_id(city)
        for (place,city2) in enumerate(data):
            print(place+1,city2.id,city2.score)
    cities = cur.execute("select e1.id, e1.embedding, e2.id, e2.embedding from embeddings e1 inner join embeddings e2 on e1.id!=e2.id").fetchall()
    cities = map(lambda x: (x[0],x[2],llm.cosine_similarity(llm.decode(x[1]),llm.decode(x[3]))),cities)
    tmp=set()
    for city_pair in cities:
        tmp.add(frozenset(city_pair))
    cities=[]
    for city_pair in tmp:
        city_pair_tmp=list(city_pair)
        if type(city_pair_tmp[2])==float:
            cities.append(city_pair_tmp)
        elif type(city_pair_tmp[1])==float:
            city_pair_tmp[1], city_pair_tmp[2] = city_pair_tmp[2], city_pair_tmp[1]
            cities.append(city_pair_tmp)
        elif type(city_pair_tmp[0])==float:
            city_pair_tmp[0], city_pair_tmp[2] = city_pair_tmp[2], city_pair_tmp[0]
            cities.append(city_pair_tmp)
    cities = sorted(cities,key=lambda x: x[2],reverse=True)
    with open("ranking.csv","w") as csv_file:
        for city in cities:
            csv_file.write("{};{};{}\n".format(*city))
    cur.close()
    con.close()


if __name__ == "__main__":
    main()
