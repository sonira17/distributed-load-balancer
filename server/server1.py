from fastapi import FastAPI




app=FastAPI()
@app.get("/")
def home():
    return{
        "server":"server1",
         "port":8001
    }

from pydantic import BaseModel
class User(BaseModel):
    user:str
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }




@app.post("/user")
def post_user(user:User):
    return{
        "result": f"user {user.user} added successfully",
        "server": "server1"
    }



@app.get("/users")
def get_users():
    return{
        "server":"server1",
         "port":8001,
         "users":"user1"
    }

import asyncio

@app.get("/slow")
async def slow():
    await asyncio.sleep(10)

    return {
        "server": "server-1",
        "message": "Finally responded"
    }