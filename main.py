from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict


app = FastAPI()


class Post(BaseModel):
    id: int
    title: str
    body: str
    author: User


class User(BaseModel):
    id: int
    username: str
    age: int


class Post_Create(BaseModel):
    id: int
    title: str
    body: str
    author_id: int


users= [
    {"id": 1, "username": "username1", "age": 30},
    {"id": 2, "username": "username2", "age": 40},
    {"id": 3, "username": "username3", "age": 50},
]


posts = [
    {"id": 1, "title": "title 1", "body": "text 1", "author": users[0] },
    {"id": 2, "title": "title 2", "body": "text 2", "author": users[1] },
    {"id": 3, "title": "title 3", "body": "text 3", "author": users[2] },
    {"id": 4, "title": "title 4", "body": "text 4", "author": users[2] },
]


@app.get("/items")
async def items() -> list[Post]:
    return [Post(**post) for post in posts]


@app.post("/items/add")
async def add_item(post: Post_Create) -> Post:
    author =  next((user for user in users if user["id"] == post.author_id), None)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_post_id = len(posts) + 1

    new_post = {"id": new_post_id, "title": post.title, "body": post.body, "author": author}
    posts.append(new_post)
    return Post(**new_post)


@app.get("/items/{item_id}")
async def item(item_id: int) -> Post:
    for post in posts:
        if post["id"] == item_id:
            return Post(**post)
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/search")
async def search(post_id: Optional[int] = None) -> Dict[str, Optional[Post]]:
    if post_id:
        for post in posts:
            if post["id"] == post_id:
                return {"data": Post(**post)}
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        return {"data": None}