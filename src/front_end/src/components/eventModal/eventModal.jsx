import { useEffect, useState } from "react"
import "./eventModal.scss"
import { ticketService } from "../../services/ticket.service"

/**
 * Компонент модального окна для выбора мероприятия.
 *
 * @param {Function} props.setSelectedEvent - Функция для установки выбранного мероприятия.
 * @param {Function} props.closeModal - Функция для закрытия модального окна.
 * @returns {JSX.Element} Модальное окно выбора мероприятия.
 */

export const EventModal = ({
  setSelectedEvent,
  closeModal,
  setAddEventModal,
}) => {
  const [searchTermEvent, setSearchTermEvent] = useState("")
  const [filterEvent, setFilterEvent] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const eventsList = await ticketService.getEvents()
        setFilterEvent(eventsList)
      } catch (error) {
        setError("Ошибка при загрузке мероприятий")
        console.error("Error loading events:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchEvents()
  }, [])

  useEffect(() => {
    const filterData = () => {
      if (!searchTermEvent) {
        return
      }
      const results = filterEvent.filter((item) => {
        return item.name.toLowerCase().includes(searchTermEvent.toLowerCase())
      })
      setFilterEvent(results)
    }

    filterData()
  }, [searchTermEvent])

  const handleSearchChange = (event) => {
    setSearchTermEvent(event.target.value)
  }

  const handleEventSelect = (event) => {
    setSelectedEvent(event)
    closeModal()
  }

  const truncateString = (str, maxLength) => {
    if (str.length > maxLength) {
      return str.substring(0, maxLength) + "..."
    }
    return str
  }

  return (
    <div className="eventModal">
      <div className="titleBlockEventModal">
        <div className="titleEventModal">Выберите мероприятие</div>
        <div
          className="textAddEventModal"
          onClick={() => setAddEventModal(true)}
        >
          + добавить своё
        </div>
      </div>
      <div className="inputBlockEventModal">
        <svg
          width="13"
          height="13"
          viewBox="0 0 13 13"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{ zIndex: "3" }}
        >
          <path
            d="M11.8833 12.875L7.42083 8.4125C7.06667 8.69583 6.65937 8.92014 6.19896 9.08542C5.73854 9.25069 5.24861 9.33333 4.72917 9.33333C3.44236 9.33333 2.3533 8.88767 1.46198 7.99635C0.57066 7.10503 0.125 6.01597 0.125 4.72917C0.125 3.44236 0.57066 2.3533 1.46198 1.46198C2.3533 0.57066 3.44236 0.125 4.72917 0.125C6.01597 0.125 7.10503 0.57066 7.99635 1.46198C8.88767 2.3533 9.33333 3.44236 9.33333 4.72917C9.33333 5.24861 9.25069 5.73854 9.08542 6.19896C8.92014 6.65937 8.69583 7.06667 8.4125 7.42083L12.875 11.8833L11.8833 12.875ZM4.72917 7.91667C5.61458 7.91667 6.36719 7.60677 6.98698 6.98698C7.60677 6.36719 7.91667 5.61458 7.91667 4.72917C7.91667 3.84375 7.60677 3.09115 6.98698 2.47135C6.36719 1.85156 5.61458 1.54167 4.72917 1.54167C3.84375 1.54167 3.09115 1.85156 2.47135 2.47135C1.85156 3.09115 1.54167 3.84375 1.54167 4.72917C1.54167 5.61458 1.85156 6.36719 2.47135 6.98698C3.09115 7.60677 3.84375 7.91667 4.72917 7.91667Z"
            fill="#8f8f8f"
          />
        </svg>
        <input
          className="inputEventModal"
          placeholder="Поиск"
          value={searchTermEvent}
          onChange={handleSearchChange}
        />
      </div>

      <div className="blockEventModal">
        <div className="blockEventModalScroll">
          {isLoading ? (
            <div className="lineBlockEventModal">Загрузка мероприятий...</div>
          ) : error ? (
            <div className="lineBlockEventModal">{error}</div>
          ) : (
            filterEvent.map((ev) => (
              <div
                key={ev.id}
                className="lineBlockEventModal"
                onClick={() => handleEventSelect(ev)}
              >
                {truncateString(ev.name, 13)}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
