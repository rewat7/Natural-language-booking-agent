from langchain_core.tools import tool
import requests, os
import datetime as dt
from dateutil import parser
from typing import Optional
from langchain.pydantic_v1 import BaseModel, Field
from pinecone import Pinecone
pc = Pinecone(api_key=pinecone_api_key)
db=pc.Index("food-db")
from openai import OpenAI
client = OpenAI()

def time_parser(time):
    formats_to_try = ["%H:%M", "%I%M %p", "%I:%M %p","%H%M"]
    parsed_time=None
    for format in formats_to_try:
        try:
            parsed_time=dt.datetime.strptime(time, format).time()
            if parsed_time: break
        except Exception as e:
            pass

    time=parsed_time.strftime("%H:%M")
    return time

def date_parser(date):
    parsed_date = parser.parse(date)
    date=parsed_date.strftime('%d-%m-%y')
    return date


class BookingInput(BaseModel):
    name:str = Field(description="name of the food item to order")
    outlet_name:str = Field(description="name of the outlet from where to order")
    # date: str = Field(description="appointment date")
    # time: str = Field(description="appointment time")

@tool(args_schema=BookingInput)
def place_order(name, outlet_name):
    '''use this tool for placing orders from an outlet'''

    try:
        api_url = "http://127.0.0.1:8000/book-appointment"
        appointment_data = {
            "name": name,
            "outlet_name":outlet_name
        }
        response=requests.post(url=api_url, json=appointment_data)
        return "Order successfull"
    
    except Exception as e:
        print(e)
        return "Some error occured please try again"

class FoodSearchInput(BaseModel):
    query:str = Field(description="description of the dish")
    criteria:Optional[str] = Field(description='''to decide whether the price should be 
                          greater or lesser than a number''')
    price:Optional[int] = Field(description="price of the dish")
    # outlet_name: str = Field(description="name of the outlet serving the dish")

@tool(args_schema=FoodSearchInput)
def search_dishes(query, criteria=None ,price=None):
    '''use the tool for getting information about dishes'''

    embeds=client.embeddings.create(input=query,
                                    model="text-embedding-ada-002").data[0].embedding
    
    if price==None:
        response=db.query(
        vector=embeds,
        top_k=1,
        include_metadata=True
        )
    
    else:
        if "lesser" in criteria:
            response=db.query(
            vector=embeds,
            top_k=2,
            filter={"price":{"$lte":price}},
            include_metadata=True
            )
        else:
            response=db.query(
            vector=embeds,
            top_k=2,
            filter={"price":{"$gte":price}},
            include_metadata=True
            )

    res_array=[]
    for res in response["matches"]:
        res_array.append(res["metadata"])

    return res_array