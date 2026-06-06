#FAST API endpoint for retrieving context from the Lancedb vector store. Create src/compass/api/main.py and write a simple FastAPI app with one endpoint: GET /context?query=some_query. The endpoint should take the query parameter, use it to search the Lancedb vector store, and return the results as JSON.
from fastapi import FastAPI, Query
from compass.config import Config
from compass.retrieval.retriever import retrieve    
app = FastAPI()
config = Config()
@app.get("/query")
async def get_query(query: str = Query(..., description="The query to search for relevant context.")):
    results = await retrieve(query, config)
    return {"results": results}
