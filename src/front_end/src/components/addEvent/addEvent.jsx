import { useState } from "react"
import { Input } from "../../utils/input/input"
import "./addEvent.scss"
export const AddEvent = ({ setAddEventModal, event, setEvent }) => {
  const [eventName, setEventName] = useState("")
  const [eventInfo, setEventInfo] = useState("")

  const handleBtnAddEvent = () => {
    if (!eventName.trim()) return
    addEventFunction({
      name: eventName,
      info: eventInfo,
    })

    setAddEventModal(false)
  }

  const addEventFunction = (ev) => {
    setEvent((pr) => [...pr, ev])
  }
  return (
    <div className="addEvent">
      <div className="titleAddEvent">Новое мероприятие</div>
      <div className="containerAddEvent">
        <div className="inputContainerAddEvent">
          <div className="blockInputAddEvent">
            <div className="titleInputAddEvent">Название</div>
            <Input
              type="text"
              placeholder="Введите название мероприятия..."
              value={eventName}
              onChange={(e) => setEventName(e.target.value)}
            />
          </div>
          <div className="blockInputAddEvent">
            <div className="titleInputAddEvent">Критерии</div>
            <Input
              multiline
              placeholder="Напишите критерии мероприятия..."
              style={{ height: "90px" }}
              value={eventInfo}
              onChange={(e) => setEventInfo(e.target.value)}
            />
          </div>
        </div>

        <button className="btnAddEvent" onClick={handleBtnAddEvent}>
          Добавить
        </button>
      </div>
      <svg
        onClick={() => setAddEventModal(false)}
        style={{
          position: "absolute",
          top: "40px",
          right: "40px",
          cursor: "pointer",
        }}
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M8.53464 25.3327L6.66797 23.466L14.1346 15.9993L6.66797 8.53268L8.53464 6.66602L16.0013 14.1327L23.468 6.66602L25.3346 8.53268L17.868 15.9993L25.3346 23.466L23.468 25.3327L16.0013 17.866L8.53464 25.3327Z"
          fill="white"
        />
      </svg>
    </div>
  )
}
