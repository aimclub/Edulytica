# /account

## /edit_profile (POST)
* access_token: str (HEAD)


* name: Optional[str]
* surname: Optional[str]
* organization: Optional[str]

## /change_password (POST)
* access_token: str (HEAD)


* old_password: str
* new_password1: str
* new_password2: str

200 {detail: "Ok"}
400 {detail: "Old password incorrect / New passwords not equal"}

## /ticket_history (GET)
* access_token: str (HEAD)

200 {detail: "Ok": tickets: [TicketModel]}
