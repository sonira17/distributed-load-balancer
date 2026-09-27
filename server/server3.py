from fastapi import FastAPI
import asyncio
app=FastAPI()

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
        "server": "server3"
    }


@app.get("/")
def home():
    return{
        "server":"server3",
        "port":8003
    }

@app.get("/users")
def get_users():
    return{
        "server":"server3",
         "port":8003,
         "user":"user3"
    }


@app.get("/slow")
async def slow():
    asyncio.slow(10)
    return {
        "server": "server-3",
        "message": "Finally responded"
    }