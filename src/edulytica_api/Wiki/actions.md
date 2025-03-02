# /actions

## /new_ticket (POST)
* access_token: str (HEAD)


* file: UploadFile
* event_id: uuid

return:
200 {detail: "Ok", ticket_id: uuid}

## /get_event_id (GET)
* access_token: str (HEAD)


* event_name: str

return:
200 {detail: "Ok", event_id: uuid}
400 {detail: "Event doesn't exist"}

## /get_ticket (GET)
* access_token: str (HEAD)


* ticket_id: uuid

return:
200 {detail: "Ok", ticket: TicketModel}
400 {detail: "Ticket doesn't exist"}

## /get_ticket_file (GET)
* access_token: str (HEAD)


* ticket_id: uuid

return:
200 {detail: "Ok", file: UploadFile}
400 {detail: "Ticket doesn't exist"}

## /get_ticket_summary (GET)
* access_token: str (HEAD)


* ticket_id: uuid
return:
200 {detail: "Ok", summary: UploadFile}
400 {detail: "Ticket doesn't exist"}

## /get_ticket_result (GET)
* access_token: str (HEAD)


* ticket_id: uuid
return:
200 {detail: "Ok", result_file: UploadFile}
400 {detail: "Ticket doesn't exist"}

## /ticket_share (POST)
* access_token: str (HEAD)


* ticket_id: uuid
return:
200 {detail: "Status has been changed"}
400 {detail: "You aren't ticket owner"}