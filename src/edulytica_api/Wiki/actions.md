# `/actions`

---

---

## `/new_ticket` (POST)
* **access_token**: str *(HEADER)*


* **file**: UploadFile
* **event_id**: uuid

Return:
1. 200 Ok

    {detail: "Ticket has been created", ticket_id: uuid}
2. 400 BadRequest

    {detail: "Invalid file uploaded"}

    {detail: "Incorrect event id"}

---

## `/get_event_id` (GET)
* **access_token**: str *(HEADER)*


* **event_name**: str

Return:
1. 200 Ok

    {detail: "Event was found", event_id: uuid}
2. 400 BadRequest

    {detail: "Event doesn't exist"}

---

## `/get_ticket` (GET)
* **access_token**: str *(HEADER)*


* **ticket_id**: uuid

Return:
1. 200 Ok

    {detail: "Ticket was found", ticket: TicketModel}
2. 400 BadRequest

    {detail: "Ticket doesn't exist"}

---

## `/get_ticket_file` (GET)
* **access_token**: str *(HEADER)*


* **ticket_id**: uuid

Return:
1. 200 Ok

    {detail: "File was found", file: UploadFile}
2. 400 BadRequest

    {detail: "Ticket doesn't exist"}

---

## `/get_ticket_summary` (GET)
* **access_token**: str *(HEADER)*


* **ticket_id**: uuid

Return:
1. 200 Ok

    {detail: "Ticket summary found", summary: UploadFile}
2. 400 BadRequest

    {detail: "Ticket doesn't exist"}

    {detail: "Ticket summary not found"}

---

## `/get_ticket_result` (GET)
* **access_token**: str *(HEADER)*


* **ticket_id**: uuid

Return:
1. 200 Ok

    {detail: "Ticket result was found", result_file: UploadFile}
2. 400 BadRequest

    {detail: "Ticket doesn't exist"}

    {detail: "Ticket result not found"}

---

## `/ticket_share` (POST)
* **access_token**: str *(HEADER)*


* **ticket_id**: uuid

Return:
1. 200 Ok

    {detail: "Status has been changed"}
2. 400 BadRequest

    {detail: "You aren't ticket owner"}

    {detail: "Ticket doesn't exist"}
