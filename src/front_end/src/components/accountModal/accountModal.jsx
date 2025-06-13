import { useEffect, useState, useCallback } from "react"
import "./accountModal.scss"

/**
 *
 * @returns {JSX.Element} left modal window with user file history
 * @param {function} props.setAccountSection - Функция для установки текущей секции аккаунта.
 * @param {string} props.accountSection - Текущая секция аккаунта ("main", "result", "info", "help").
 * @param {function} props.setFileResult - Функция для установки имени выбранного файла, по которому далее открываем результаты работы.
 * @param {array} props.tickets - Массив тикетов.
 * @param {function} props.fetchTicketHistory - Функция для получения истории тикетов.
 */

export const AccountModal = ({
  setAccountSection,
  accountSection,
  setFileResult,
  tickets,
  fetchTicketHistory,
}) => {
  const [searchTerm, setSearchTerm] = useState("")
  const [filterHistory, setFilterHistory] = useState([])
  const [animate, setAnimate] = useState(false)
  const [, setIsLoading] = useState(false)
  const [, setError] = useState(null)

  useEffect(() => {
    setTimeout(() => setAnimate(true), 50)
  }, [])

  useEffect(() => {
    const filterData = () => {
      if (!searchTerm) {
        setFilterHistory(tickets)
        return
      }
      const results = tickets.filter((ticket) => {
        return ticket.document_id
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase())
      })
      setFilterHistory(results)
    }

    filterData()
  }, [searchTerm, tickets])

  const updateHistory = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      await fetchTicketHistory()
    } catch (err) {
      setError("Не удалось загрузить историю тикетов")
      console.error("Error loading ticket history:", err)
    } finally {
      setIsLoading(false)
    }
  }, [fetchTicketHistory])

  useEffect(() => {
    updateHistory()
  }, [updateHistory])

  const handleFileLine = (ticket) => {
    setAccountSection("result")
    setFileResult(ticket.document_id)
  }
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value)
  }
  const truncateString = (str, maxLength) => {
    if (str.length > maxLength) {
      return str.substring(0, maxLength) + "..."
    }
    return str
  }

  return (
    <div className={`accModal ${animate ? "animate" : ""}`}>
      <div className="titleBlockAccModal">
        <div
          onClick={() => {
            setAccountSection("info")
          }}
          className={
            accountSection === "info" ? "titleAccModalActive" : "titleAccModal"
          }
        >
          О нас
        </div>
        <div
          onClick={() => {
            setAccountSection("help")
          }}
          className={
            accountSection === "help" ? "titleAccModalActive" : "titleAccModal"
          }
        >
          Помощь
        </div>
        <div
          onClick={() => {
            setAccountSection("main")
          }}
          className={
            accountSection === "main" || accountSection === "result"
              ? "titleAccModalActive"
              : "titleAccModal"
          }
        >
          Работа с документом
        </div>
      </div>
      <svg
        width="227"
        height="2"
        viewBox="0 0 227 2"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M0 1H227" stroke="#BEBABA" strokeWidth="2" />
      </svg>

      <div className="historyBlockAccModal">
        <div className="titleAccModal">История документов</div>
        <div className="inputBlockAccModal">
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
            className="inputAccModal"
            placeholder="Поиск"
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
        <div className="containerFileAccModal">
          <div className="containerScrollFileAccModal">
            {filterHistory.map((ticket) => (
              <div
                className="fileLineAccModal"
                key={ticket.id}
                onClick={() => handleFileLine(ticket)}
              >
                <div className="fileAccModal">
                  {truncateString(ticket.document_id || "Без названия", 16)}
                </div>
                <svg
                  style={{ marginRight: "25px" }}
                  width="12"
                  height="12"
                  viewBox="0 0 12 12"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M2.5 5C1.95 5 1.5 5.45 1.5 6C1.5 6.55 1.95 7 2.5 7C3.05 7 3.5 6.55 3.5 6C3.5 5.45 3.05 5 2.5 5Z"
                    stroke="#BEBABA"
                    strokeWidth="0.5"
                  />
                  <path
                    d="M9.5 5C8.95 5 8.5 5.45 8.5 6C8.5 6.55 8.95 7 9.5 7C10.05 7 10.5 6.55 10.5 6C10.5 5.45 10.05 5 9.5 5Z"
                    stroke="#BEBABA"
                    strokeWidth="0.5"
                  />
                  <path
                    d="M6 5C5.45 5 5 5.45 5 6C5 6.55 5.45 7 6 7C6.55 7 7 6.55 7 6C7 5.45 6.55 5 6 5Z"
                    stroke="#BEBABA"
                    strokeWidth="0.5"
                  />
                </svg>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
