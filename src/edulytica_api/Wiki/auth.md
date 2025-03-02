# /auth

---

## /registration (POST)
* login: str
* email: str
* password1: str
* password2: str

## /check_code (POST)
* code: str

return:
200 {detail: "Code is correct", access_token: str} + HTTPOnly Cookie (Refresh Token)
400 {detail: "Wrong code"}

## /login (POST)
* login: str
* password: str

return:
200 {detail: "Ok", access_token: str} + HTTPOnly Cookie (Refresh Token)
401 {detail: "Unauthorized"}

## /get_access (GET)
* refresh_token: str (HEAD)

return:
200 {detail: "Ok", access_token: str} + HTTPOnly Cookie (Refresh Token)
400 {detail: ""}

## /logout (GET)
* access_token: str (HEAD)

return:
200 {detail: "Ok"} + HTTPOnly Cookie (Refresh Token)


