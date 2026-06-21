import lancedb

db = lancedb.connect("data/lancedb")
table = db.open_table("documents")
print(len(table.to_pandas()))
