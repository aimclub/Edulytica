# `/account`

---

---

## `/edit_profile` (POST)
* **access_token**: str *(HEADER)*


* **name**: Optional[str]
* **surname**: Optional[str]
* **organization**: Optional[str]

Return:
1. 200 Ok

    {detail: "Profile has been edited"}
2. 400 BadRequest

    {detail: "None of the arguments were specified"}

---

## `/change_password` (POST)
* **access_token**: str *(HEADER)*


* **old_password**: str
* **new_password1**: str
* **new_password2**: str

Return:
1. 200 Ok

    {detail: "Password has been changed"}
2. 400 BadRequest

    {detail: "Old password incorrect"}

    {detail: "New passwords not equal"}

---

## `/ticket_history` (GET)
* **access_token**: str *(HEADER)*

Return:
1. 200 Ok

    {detail: "Ticket history found", tickets: List[TicketModel]}
