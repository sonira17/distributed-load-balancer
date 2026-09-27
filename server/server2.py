from fastapi import FastAPI

app=FastAPI()
import asyncio
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
        "server": "server2"
    }


@app.get("/")
def home():
    return{
        "server":"server2",
         "port":8002
    }

@app.get("/users")
def get_users():
    return{
        "server":"server2",
         "port":8002,
         "user":"user2"
    }




@app.get("/slow")
async def slow():
    await asyncio.sleep(10)
    return {
        "server": "server-2",
        "message": "Finally responded"
    }
