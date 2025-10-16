import { useState } from "react"
import { Input } from "../../utils/input/input"
import "./addEvent.scss"
import { ticketService } from "../../services/ticket.service"

export const AddEvent = ({ setAddEventModal }) => {
  const [eventName, setEventName] = useState("")
  const [eventInfo, setEventInfo] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [fieldErrors, setFieldErrors] = useState({})
  const [touched, setTouched] = useState({})

  const validate = () => {
    const errors = {}
    if (!eventName.trim()) {
      errors.eventName = "Введите название мероприятия"
    }
    if (!eventInfo.trim()) {
      errors.eventInfo = "Заполните описание мероприятия"
    }
    return errors
  }

  const handleBtnAddEvent = async () => {
    const errors = validate()
    setFieldErrors(errors)
    setTouched({ eventName: true, eventInfo: true })
    if (Object.keys(errors).length > 0) return
    setLoading(true)
    setError("")
    try {
      await ticketService.addCustomEvent(eventName, eventInfo)
      setAddEventModal(false)
    } catch (err) {
      if (err?.response?.data?.detail) {
        setFieldErrors({ eventName: err.response.data.detail })
        setTouched((prev) => ({ ...prev, eventName: true }))
      } else {
        let msg = "Ошибка при добавлении мероприятия."
        if (err?.message) {
          msg = err.message
        }
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
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
              onChange={(e) => {
                setEventName(e.target.value)
                setTouched((prev) => ({ ...prev, eventName: true }))
                if (fieldErrors.eventName) {
                  setFieldErrors((prev) => ({ ...prev, eventName: undefined }))
                }
              }}
              disabled={loading}
            />
            {touched.eventName && fieldErrors.eventName && (
              <div className="errorTextAddEvent">{fieldErrors.eventName}</div>
            )}
          </div>
          <div className="blockInputAddEvent">
            <div className="titleInputAddEvent">Критерии</div>
            <Input
              multiline
              placeholder="Напишите критерии мероприятия..."
              style={{ height: "90px" }}
              value={eventInfo}
              onChange={(e) => {
                setEventInfo(e.target.value)
                setTouched((prev) => ({ ...prev, eventInfo: true }))
                if (fieldErrors.eventInfo) {
                  setFieldErrors((prev) => ({ ...prev, eventInfo: undefined }))
                }
              }}
              disabled={loading}
            />
            {touched.eventInfo && fieldErrors.eventInfo && (
              <div className="errorTextAddEvent">{fieldErrors.eventInfo}</div>
            )}
          </div>
        </div>
        {error && <div className="errorAddEvent">{error}</div>}
        <button
          className="btnAddEvent"
          onClick={handleBtnAddEvent}
          disabled={loading}
        >
          {loading ? "Добавление..." : "Добавить"}
        </button>
      </div>
      <svg
        onClick={() => setAddEventModal(false)}
        style={{
          position: "absolute",
          top: "40px",
          right: "40px",
          cursor: loading ? "not-allowed" : "pointer",
          pointerEvents: loading ? "none" : "auto",
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
