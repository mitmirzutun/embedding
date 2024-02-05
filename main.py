import llm, sqlite3, subprocess, json

def cosine_similarity(a,b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(x * x for x in b) ** 0.5
    return dot_product / (magnitude_a * magnitude_b)

def setup():
    con=sqlite3.connect("embedding.db")
    cur=con.cursor()
    cur.execute("create table embedding(file, score)")
    cur.close()
    con.close()

def embed(file_name: str) -> None:
    if "'"  in file_name:
        raise ValueError("file name is a SQL Injection attempt")
    if subprocess.run(["ls", "embedding.db"],capture_output=True).returncode!=0:
        setup()
    embedding_model = llm.get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    file = open(file_name)
    vector = embedding_model.embed(file.read())
    file.close()
    con = sqlite3.connect("embedding.db")
    cur = con.cursor()
    if cur.execute(f"select 1 from embedding where file='{file_name}'").fetchone()!=None:
        cur.close()
        con.close()
        return
    insert="insert into embedding values ('"+file_name+"','"+json.dumps(vector)+"')"
    cur.execute(insert)
    con.commit()
    cur.close()
    con.close()

def main():
    ls_result=subprocess.run(["ls","data"],capture_output=True).stdout.decode("utf8")
    for file in ls_result.strip().split("\n"):
        embed(f"data/{file}")
    con=sqlite3.connect("embedding.db")
    cur=con.cursor()
    res=cur.execute("select e1.file, e1.score, e2.file, e2.score from embedding e1 cross join embedding e2")
    for (file1,array1,file2,array2) in res:
        vector1=json.loads(array1)
        vector2=json.loads(array2)
        print(file1,file2,cosine_similarity(vector1,vector2))
    cur.close()
    con.close()
    # subprocess.run(["rm","embedding.db"])

if __name__ == "__main__":
    main()