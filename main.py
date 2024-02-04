import llm, sqlite3

def setup():
    con=sqlite3.connect("embedding.db")
    cur=con.cursor()
    cur.execute("create table embedding(file, score)")
    print(cur.execute("select * from embedding").fetchall())
    cur.close()
    con.close()

def embed(file_name: str) -> None:
    embedding_model = llm.get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    file = open(file_name)
    vector = embedding_model.embed(file.read())
    file.close()
    con = sqlite3.connect("embedding.db")
    cur = con.cursor()
    insert="insert into embedding values {}".format(",".join(map(lambda x: "('"+file_name+"',"+str(x)+")",vector)))
    cur.execute(insert)
    print(cur.execute("select * from embedding").fetchall())
    cur.close()
    con.close()

def main():
    import subprocess
    if subprocess.run(["ls", "embedding.db"],capture_output=True).returncode!=0:
        setup()
    embed("data/equalstreetnames.md")
    subprocess.run(["rm","embedding.db"])

if __name__ == "__main__":
    main()