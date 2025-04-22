# Todo API

A Todo API with user authentication.

## Prerequisites

- Python 3
- Virtual environment manager (Virtualenv, Pipenv, e.t.c.)

## Getting started

### Downloading and setting up the project

To set up the project on your local machine, follow these steps:

- Clone the repo to your computer
- Cd into the project folder
- Activate a virtual environment for the project (Optional, but recommended)
- Install its dependencies

### Setting up the database integration

To integrate a PostgreSQL database into this project, you first need to set one up, either locally or on the cloud will do.

Next, create a connection string for the database. PostgreSQL connection strings usually follow this format:

```txt
postgres://username:password@host_ip:port/database
```

After generating your connection string, create a `.env` file in the project's root folder, and paste the following line into it:

```env
DB_URL=db_connection_string
```

Replacing `db_connection_string` with the connection string of your database (without adding quotes). For example:

```env
DB_URL=postgres://username:password@host_ip:port/database
```

### Running the project

With the project set up, run any of these commands, to start the API in your prefered mode:

- Development

```bash
fastapi dev main.py
```

- Production

```bash
fastapi run main.py
```

## How does it work

The API provides two endpoints for user authentication: `/api/auth/login` and `/api/auth/signup`. They take in username and password as requests and return a token as part of their output. The server uses this endpoint for user identification.

In a web application, you can store this token in cookies, local storage, or anywhere else you deem fit. And pass it through the `Authentication` header of any request your app makes to any of the todo endpoints.

For example:

```js
const myHeaders = new Headers();
myHeaders.append("Authorization", "Bearer [TOKEN_TEXT]");

const requestOptions = {
  method: "GET",
  headers: myHeaders,
  redirect: "follow",
};

fetch("http://127.0.0.1:8000/api/todos", requestOptions)
  .then((response) => response.text())
  .then((result) => console.log(result))
  .catch((error) => console.error(error));
```

Replacing `[TOKEN_TEXT]` with the token gotten from the authentication APIs like the login API below:

```js
const myHeaders = new Headers();
myHeaders.append("Content-Type", "application/json");

const raw = JSON.stringify({
  username: "GhoulKingR",
  password: "1234",
});

const requestOptions = {
  method: "POST",
  headers: myHeaders,
  body: raw,
  redirect: "follow",
};

fetch("http://127.0.0.1:8000/api/auth/login", requestOptions)
  .then((response) => response.text())
  .then((result) => console.log(result))
  .catch((error) => console.error(error));
```

This would return an response containing the token text, structured like the below:

```json
{
  "message": "successful",
  "token": "TOKEN_TEXT"
}
```

## Implemention detail

This section contains overview of different aspects of the implementation.

### Framework and tooling

The framework/development tools used for this project are:

- FastAPI - Backend framework
- PostgreSQL - Database

### Authentication

The type of authentication used in the project is a self-rolled JWT authentication system. This system provides two endpoints for authenticating users:

- `/api/auth/signup`: for creating an account
- `/api/auth/login`: for logging users into their account

Both accept `POST` requests and accept JSON strings with the syntax below:

```JSON
{
  "username": "string",
  "password": "string"
}
```

The only difference between them, is that the login endpoint generates a token for the user account. The signup endpoint creates a new account and return the token if it doesn't exist, and doesn't return a token if the account already exists.

The token is returned as a `token` field in the response object. For example:

```JSON
{
    "message": "successful",
    "token": "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJuYW1lIjogIkdob3VsS2luZ1IiLCAiX2lkIjogMiwgImV4cCI6IDE3NDUzMzcyNzN9.YWkHW5dX8mW2vg4Y14Z5ryOyk0GBlU0qGyJ8pppZD5s"
}
```
