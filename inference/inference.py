from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.models.ollama import Ollama
from agno.tools.duckdb import DuckDbTools
from textwrap import dedent
import json 
from typing import Optional
from agno.tools import Toolkit
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os

os.environ['GROQ_API_KEY'] = ''
model = Groq(id="llama-3.3-70b-versatile")
# model = Ollama(id="llama3.2:1b")
embed_model = SentenceTransformer('all-mpnet-base-v2')

class RetrieveTools(Toolkit):
    def __init__(
        self,
    ):
        super().__init__(name = "retrieve_tools")
        self.es = Elasticsearch(
    "http://localhost:9200",
)
        self.register(self.retrieve_tool)
    def retrieve_tool(self, prompt:str) -> Optional[str]:
        if self.es.ping():
            print('Connected to ES!')
        else:
            print('Could not connect to ES!')
            exit(1)
        max_candi = self.es.count(index="rag")["count"]
        if max_candi > 0:
            query = {
            "field" : "SummaryVector",
            "query_vector" : embed_model.encode(prompt),
            "k" : 5,
            "num_candidates" : max_candi , 
        }
        res = self.es.knn_search(index="rag", knn=query , source=["Price","Area","Position","Type","Benefit"])
        results = []

        for hit in res['hits']['hits']:
            if hit['_score'] < 0.5:
                continue
            source_data = hit['_source']
            # print(source_data.get("Content"))
            results.append({
                "Giá": source_data.get("Price"),
                "Diện tích": source_data.get("Area"),
                "Vị trí": source_data.get("Position"),
                "Loại hình": source_data.get("Type"),
                "Tiện ích": source_data.get("Benefit"),
                # "Summary": source_data.get("Summary")
            })
        return json.dumps(results, indent=2)   

agent = Agent(model=model, 
              tools = [RetrieveTools()],
            #   markdown=True,
              instructions = dedent("""\
    Initiate the 'retrieve_tool' to gather relevant information.
    If the 'retrieve_tool' provides useful information, response to the user in Vietnamese based on that information.
    Please respond with a detailed overview, structured in a way that provides clarity and highlights the key aspects of the offer. Make sure to include:
    - Giá (Price): Provide the cost details and explain what the price includes, if applicable.
    - Vị trí (Location): Describe the location and its proximity to key landmarks, transportation, or any notable features.
    - Tiện ích (Amenities): List the amenities available, emphasizing the most attractive or unique features of the property or service.
    If the question about they need to buy and rent some place, suggest two places that are similar in terms of price, location, or amenities. For each suggestion, provide the same detailed structure (Price, Location, and Amenities) to help the user compare their options.
    
    If no useful information is retrieved, respond in Vietnamese based on your own knowledge.
    
    """),
              )
while True:
    input_text = input("User: ")
    agent.print_response(input_text)