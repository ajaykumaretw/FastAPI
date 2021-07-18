try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    from bson.objectid import ObjectId
    from datetime import datetime
    #MOTOR
    import motor.motor_asyncio
except Exception as e:
    print("Error! Some Modules are Missing  : {} ".format(e))


app = FastAPI()

MONGO_DETAILS = "mongodb+srv://FasterAPI:FasterAPI123@cluster0.wffch.mongodb.net/test"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.FASTAPI
FASTAPI_collection = database.get_collection("FasterAPI")

def schema_helper(data) -> dict:
    '''
    helper to make the mongo query into dict form
    '''
    return {
        "id": str(data["_id"]),
        "SKU": data["sku"],
        "Brand Name": data["brand_name"],
        "Title": data["title"],
        "Thumbnail":  data["thumbnail"],
        "Available Price":  data["available_price"],
        "MRP":  data["mrp"]
    }


class Items(BaseModel):
    sku: str
    brand_name: str
    title: str
    thumbnail: str
    available_price: str
    mrp: str

# Retrieve all datas present in the database
@app.get("/")
async def get_all_data():
    datas = []
    async for data in FASTAPI_collection.find():
        datas.append(schema_helper(data))
    return datas

# Retrieve a data with a matching ID present in the database
@app.get("/{data_id}")
async def get_data(data_id:str):
    data_data = await FASTAPI_collection.find_one({"_id": ObjectId(data_id)})
    return schema_helper(data_data)

# Add a new data into to the database
@app.post('/new/')
async def post_data(item: dict) -> dict:
    data_data = await FASTAPI_collection.insert_one(item)
    new_data = await FASTAPI_collection.find_one({"_id": data_data.inserted_id})
    return schema_helper(new_data)


# Delete a data from the database
@app.delete('/delete_data/{data_id}')
async def delete_data(data_id: str):
    '''
    Return: 
            true, once the data got deleted.
    '''
    data = await FASTAPI_collection.find_one({"_id": ObjectId(data_id)})
    if data:
        await FASTAPI_collection.delete_one({"_id": ObjectId(data_id)})
        return True
    return False

# Update data with a matching ID
@app.put('/update_data/{data_id}')
async def update_data(id: str, updated_data: dict):
    '''
    Return: 
            true, once the data element got updated.
            false, if an empty request body is sent.
    '''
    if len(updated_data) < 1:
        return False
    data = await FASTAPI_collection.find_one({"_id": ObjectId(id)})

    #add update and update time field to get tracked
    data.update({"update":True, "updated_time":datetime.now()})
    if data:
        updated = await FASTAPI_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": updated_data}
        )
        if updated:
            return True
        return False

