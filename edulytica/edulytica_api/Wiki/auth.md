# `/auth`

---

---

## `/registration` (POST)
* **login**: str
* **email**: str
* **password1**: str
* **password2**: str

Return:
1. 200 Ok

    {detail: "Code has been sent"}
2. 400 BadRequest

    {detail: "Passwords are not equal"}
    
    {detail: "User with such email already exists"}

    {detail: "User with such login already exists"}

---

## `/check_code` (POST)
* **code**: str

Return:
1. 200 Ok

    {detail: "Code is correct", access_token: str}

    \+ `HTTPOnly Cookie (Refresh Token)`
2. 400 BadRequest

    {detail: "Wrong code"}

---

## `/login` (POST)
* **login**: str
* **password**: str

Return:
1. 200 Ok

    {detail: "Credentials are correct", access_token: str}

    \+ `HTTPOnly Cookie (Refresh Token)`
2. 401 Unauthorized

    {detail: "Credentials are incorrect"}

---

## `/get_access` (GET)
* **refresh_token**: str *(HEADER)*

Return:
1. 200 Ok

    {detail: "Token is correct", access_token: str} 

    \+ `HTTPOnly Cookie (Refresh Token)`
2. 400 BadRequest

    {detail: "Token is incorrect"}

    \+ `HTTPOnly Cookie (Refresh Token)`
---

## `/logout` (GET)
* **refresh_token**: str *(HEADER)*

Return:
1. 200 Ok 

    {detail: "Logout successful"} 

    \+ `HTTPOnly Cookie (Refresh Token)`


