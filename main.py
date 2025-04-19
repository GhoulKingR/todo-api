from fastapi import FastAPI, Header, status, Response
from typing import Annotated
from pydantic import BaseModel
import psycopg
import hashlib
from jwt_utility import generate_token, validate_token


class Item(BaseModel):
    title: str
    description: str


class ItemOpt(BaseModel):
    title: str | None = None
    description: str | None = None


class User(BaseModel):
    username: str
    password: str


description = """
A Todo API with user authentication

## Features
With this API you can:
- Log users in
- Create an account
- Get all todo items (Requires authentication)
- Get a single todo item (Requires authentication)
- Add a todo item (Requires authentication)
- Change a todo item (Requires authentication)
- delete an item (Requires authentication)
"""

app = FastAPI(
    title="Todo API",
    description=description,
    license_info={"name": "MIT License", "identifier": "MIT"},
)


def create_connection():
    return psycopg.AsyncConnection.connect(
        "postgres://postgres:password@127.0.0.1:5432/todoapp"
    )


@app.post("/api/auth/login")
async def login(user: User, response: Response):
    try:
        conn = await create_connection()
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}

    password = hashlib.sha256(user.password.encode()).hexdigest()
    curr = await conn.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (user.username, password),
    )
    result = await curr.fetchone()
    if result:
        return {
            "message": "successful",
            "token": generate_token(
                {
                    "name": user.username,
                    "_id": result[0],
                }
            ),
        }

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "incorrect username/password"}


@app.post("/api/auth/signup")
async def create_account(user: User, response: Response):
    try:
        conn = await create_connection()
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}

    try:
        password = hashlib.sha256(user.password.encode()).hexdigest()
        await conn.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s);",
            (user.username, password),
        )
        await conn.commit()
        curr = await conn.execute("Select lastval();")
        return {
            "message": "successful",
            "token": generate_token(
                {
                    "name": user.username,
                    "_id": (await curr.fetchone())[0],
                }
            ),
        }
    except:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "username already exists"}


@app.get("/api/todos")
async def root(authorization: Annotated[str | None, Header()], response: Response):
    try:
        token_obj = validate_token(authorization)
    except:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "unauthorized"}

    try:
        conn = await create_connection()
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}

    cur = await conn.execute(
        "SELECT * from todoItems WHERE userId = %s;", (token_obj["_id"],)
    )
    result = [
        {
            "id": item[0],
            "title": item[1],
            "description": item[2],
        }
        for item in await cur.fetchall()
    ]
    await conn.close()
    return result


@app.get("/api/todos/{id}")
async def get_item(
    id, authorization: Annotated[str | None, Header()], response: Response
):
    try:
        token_obj = validate_token(authorization)
    except:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "unauthorized"}

    try:
        conn = await create_connection()
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}

    cur = await conn.execute(
        "SELECT * FROM todoItems WHERE itemId = %s AND userId = %s;",
        (id, token_obj["_id"]),
    )
    item = await cur.fetchone()
    if item:
        result = {
            "id": item[0],
            "title": item[1],
            "description": item[2],
        }
        await conn.close()
        return result

    await conn.close()
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"message": f"todo item does not exist"}


@app.post("/api/todos")
async def add_item(
    item: Item, authorization: Annotated[str | None, Header()], response: Response
):
    try:
        token_obj = validate_token(authorization)
    except:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "unauthorized"}

    try:
        conn = await create_connection()
        await conn.execute(
            "INSERT INTO todoItems (title, description, userid) VALUES (%s, %s, %s)",
            (item.title, item.description, token_obj["_id"]),
        )
        await conn.commit()
        curr = await conn.execute("SELECT lastval();")

        new_item = {
            "id": (await curr.fetchone())[0],
            "title": item.title,
            "description": item.description,
        }

        await conn.close()
        return new_item
    except:
        await conn.close()
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}


@app.put("/api/todos/{id}")
async def change_item(
    id,
    item: ItemOpt,
    authorization: Annotated[str | None, Header()],
    response: Response,
):
    try:
        token_obj = validate_token(authorization)
    except:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "unauthorized"}

    try:
        conn = await create_connection()
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}

    cur = await conn.execute(
        "SELECT * FROM todoItems WHERE itemId = %s AND userId = %s;",
        (id, token_obj["_id"]),
    )
    itemdb = await cur.fetchone()

    try:
        if itemdb:
            to_change = {
                "id": itemdb[0],
                "title": itemdb[1],
                "description": itemdb[2],
            }

            if item.title:
                to_change["title"] = item.title

            if item.description:
                to_change["description"] = item.description

            await conn.execute(
                "UPDATE todoItems SET title = %s, description = %s WHERE itemId = %s",
                (to_change["title"], to_change["description"], to_change["id"]),
            )
            await conn.commit()

            await conn.close()
            return to_change

        await conn.close()
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"todo item does not exist"}

    except:
        await conn.close()
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}


@app.delete("/api/todo/{id}")
async def delete_item(
    id, authorization: Annotated[str | None, Header()], response: Response
):
    try:
        token_obj = validate_token(authorization)
    except:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "unauthorized"}

    try:
        conn = await create_connection()
        await conn.execute(
            "DELETE FROM todoItems WHERE itemid = %s AND userid = %s",
            (id, token_obj["_id"]),
        )
        await conn.commit()
        await conn.close()

        return {"message": "successful"}
    except:
        await conn.close()
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Internal server error"}
