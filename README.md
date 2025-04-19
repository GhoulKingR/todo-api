# Todo API

A Todo API with user authentication.

## Prerequisites

- Python 3
- Virtual environment manager (Virtualenv, Pipenv, e.t.c.)

## Getting started

To set up the project on your local machine, follow these steps:

- Clone the repo to your computer
- Cd into the project folder
- Activate a virtual environment for the project (Optional, but recommended)
- Install its dependencies

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
myHeaders.append("Authorization", "TOKEN_TEXT");

const requestOptions = {
  method: "GET",
  headers: myHeaders,
  redirect: "follow"
};

fetch("http://127.0.0.1:8000/api/todos", requestOptions)
  .then((response) => response.text())
  .then((result) => console.log(result))
  .catch((error) => console.error(error));
```

With this example, you can log all the todos created by the user identified by `TOKEN_TEXT`.

To get the token, you can use an example like this:
```js
const myHeaders = new Headers();
myHeaders.append("Content-Type", "application/json");

const raw = JSON.stringify({
  "username": "GhoulKingR",
  "password": "1234"
});

const requestOptions = {
  method: "POST",
  headers: myHeaders,
  body: raw,
  redirect: "follow"
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


<!-- ## Docs
To point to the actual API Docs -->

<!--
TODO:
- Write DB Creation script
- Write DB seed script
- An env file (and an entry in the readme for it)
 -->
