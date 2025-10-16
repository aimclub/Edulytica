import { useEffect, useState, useCallback } from "react"
import "./eventModal.scss"
import { ticketService } from "../../services/ticket.service"
import eventDescriptions from "./eventDescriptions.json"
import { EventInfoModal } from "./eventInfoModal"

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
  onShowEventInfo,
}) => {
  const [searchTermEvent, setSearchTermEvent] = useState("")
  const [filterEvent, setFilterEvent] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [events, setEvents] = useState([])
  const [infoModal, setInfoModal] = useState({
    visible: false,
    title: "",
    description: "",
  })

  const filterData = useCallback(() => {
    if (!searchTermEvent) {
      setFilterEvent(events)
      return
    }
    const results = events.filter((item) => {
      return item.name.toLowerCase().includes(searchTermEvent.toLowerCase())
    })
    setFilterEvent(results)
  }, [searchTermEvent, events])

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const eventsList = await ticketService.getEvents()
        setEvents(eventsList)
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
    if (events) {
      filterData()
    }
  }, [events, filterData])

  const handleSearchChange = (event) => {
    setSearchTermEvent(event.target.value)
  }

  const handleEventSelect = (event) => {
    setSelectedEvent(event)
    closeModal()
  }

  const openEventInfo = (ev) => {
    const key = ev?.name
    const fallbackTitle = key || "Мероприятие"
    const descriptionFromJson = key && eventDescriptions[key]?.description
    const titleFromJson = key && eventDescriptions[key]?.title
    const description =
      ev?.info ||
      descriptionFromJson ||
      "Описание для данного мероприятия пока отсутствует."
    const title = titleFromJson || fallbackTitle
    setInfoModal({ visible: true, title, description })
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
        {/* Temporarily hidden: add your own event button */}
        {/**
         * <div
         *   className="textAddEventModal"
         *   onClick={() => setAddEventModal(true)}
         * >
         *   + добавить своё
         * </div>
         */}
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
              <div key={ev.id} className="lineBlockEventModal">
                <div className="lineBlockEventModalRow">
                  <svg
                    className="eventInfoSvgButton"
                    onClick={(e) => {
                      e.stopPropagation()
                      openEventInfo(ev)
                    }}
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10Zm0-13a1.25 1.25 0 1 0 0-2.5 1.25 1.25 0 0 0 0 2.5Zm-1.25 8.5h2.5v-7h-2.5v7Z"
                      fill="#bebaba"
                    />
                  </svg>
                  <div
                    onClick={() => handleEventSelect(ev)}
                    style={{ flex: "1 1 auto" }}
                  >
                    {truncateString(ev.name, 13)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      {infoModal.visible && (
        <EventInfoModal
          title={infoModal.title}
          description={infoModal.description}
          onClose={() =>
            setInfoModal({ visible: false, title: "", description: "" })
          }
        />
      )}
    </div>
  )
}
