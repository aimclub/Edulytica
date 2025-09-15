import { useEffect, useState, useCallback, useRef } from "react"
import { useNavigate } from "react-router-dom"
import "./accountModal.scss"
import { useDispatch } from "react-redux"
import { fetchTicket } from "../../store/ticketSlice"
import { ContextMenu } from "./ContextMenu"
import { RenameTicketModal } from "../renameTicketModal/renameTicketModal"
import { NotificationModal } from "../notificationModal/notificationModal"
import { ticketService } from "../../services/ticket.service"

/**
 *
 * @returns {JSX.Element} left modal window with user file history
 * @param {function} props.setAccountSection - Функция для установки текущей секции аккаунта.
 * @param {string} props.accountSection - Текущая секция аккаунта ("main", "result", "info", "help").
 * @param {function} props.setFileResult - Функция для установки имени выбранного файла, по которому далее открываем результаты работы.
 * @param {array} props.tickets - Массив тикетов с полями name, document_id, id.
 * @param {function} props.fetchTicketHistory - Функция для получения истории тикетов.
 * @param {object} props.currentTicket - Текущий тикет.
 */

export const AccountModal = ({
  setAccountSection,
  accountSection,
  tickets,
  fetchTicketHistory,
  currentTicket,
  onTicketClick,
}) => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState("")
  const [filterHistory, setFilterHistory] = useState([])
  const [animate, setAnimate] = useState(false)
  const [contextMenu, setContextMenu] = useState({
    visible: false,
    ticketId: null,
    position: { x: 0, y: 0 },
  })
  const [renameTicketModal, setRenameTicketModal] = useState({
    visible: false,
    ticketId: null,
    ticketName: "",
  })
  const [notificationModal, setNotificationModal] = useState({
    visible: false,
    text: "",
    eta: "",
  })
  const scrollContainerRef = useRef(null)

  useEffect(() => {
    setTimeout(() => setAnimate(true), 50)
  }, [])

  // Закрываем контекстное меню при клике вне его
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contextMenu.visible) {
        closeContextMenu()
      }
    }

    if (contextMenu.visible) {
      document.addEventListener("click", handleClickOutside)
      return () => document.removeEventListener("click", handleClickOutside)
    }
  }, [contextMenu.visible])

  // Закрываем контекстное меню при скролле контейнера с историей документов
  useEffect(() => {
    const handleScroll = () => {
      if (contextMenu.visible) {
        closeContextMenu()
      }
    }

    const scrollContainer = scrollContainerRef.current
    if (contextMenu.visible && scrollContainer) {
      scrollContainer.addEventListener("scroll", handleScroll, {
        passive: true,
      })
      return () => scrollContainer.removeEventListener("scroll", handleScroll)
    }
  }, [contextMenu.visible])

  // Обновляем позицию контекстного меню при изменении размера окна
  useEffect(() => {
    const handleResize = () => {
      if (contextMenu.visible && contextMenu.ticketId) {
        const threeDotsElement = document.querySelector(
          `[data-ticket-id="${contextMenu.ticketId}"]`
        )
        if (threeDotsElement) {
          const rect = threeDotsElement.getBoundingClientRect()
          setContextMenu((prev) => ({
            ...prev,
            position: {
              x: rect.right + window.scrollX,
              y: rect.top + window.scrollY,
            },
          }))
        }
      }
    }

    if (contextMenu.visible) {
      window.addEventListener("resize", handleResize, { passive: true })
      return () => window.removeEventListener("resize", handleResize)
    }
  }, [contextMenu.visible, contextMenu.ticketId])

  useEffect(() => {
    const filterData = () => {
      if (!searchTerm) {
        setFilterHistory(tickets)
        return
      }
      const results = tickets.filter((ticket) => {
        const searchableText = (ticket.name || "").toLowerCase()
        return searchableText.includes(searchTerm.toLowerCase())
      })
      setFilterHistory(results)
    }

    filterData()
  }, [searchTerm, tickets])

  // Создаем функцию для начальной загрузки
  const initialTicketLoad = useCallback(async () => {
    if (tickets.length === 0) {
      // Проверяем, есть ли уже данные
      await fetchTicketHistory()
    }
  }, [tickets.length, fetchTicketHistory])

  // Используем для начальной загрузки
  useEffect(() => {
    initialTicketLoad()
  }, [initialTicketLoad])

  // Принудительно обновлять историю тикетов при открытии секции 'main' или 'result'
  useEffect(() => {
    if (accountSection === "main" || accountSection === "result") {
      fetchTicketHistory()
    }
  }, [accountSection]) // eslint-disable-line react-hooks/exhaustive-deps

  // Удаляем documentId из URL, если мы не в секции 'result'
  useEffect(() => {
    if (
      accountSection !== "result" &&
      window.location.pathname !== "/account/result"
    ) {
      const searchParams = new URLSearchParams(window.location.search)
      if (searchParams.has("ticketId")) {
        searchParams.delete("ticketId")
        const newUrl = searchParams.toString()
          ? `?${searchParams.toString()}`
          : window.location.pathname
        window.history.replaceState(null, "", newUrl)
      }
    }
  }, [accountSection])

  const handleFileLine = (ticket) => {
    setAccountSection("result")
    navigate(`/account/result?ticketId=${ticket.id}`)

    // Показываем уведомление сразу при клике
    if (onTicketClick) {
      onTicketClick(ticket)
    }

    dispatch(fetchTicket(ticket.id))
  }
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value)
  }

  const handleContextMenuClick = (event, ticket) => {
    event.stopPropagation()
    const rect = event.currentTarget.getBoundingClientRect()
    setContextMenu({
      visible: true,
      ticketId: ticket.id,
      position: {
        x: rect.right + window.scrollX,
        y: rect.top + window.scrollY,
      },
    })
  }

  const handleContextMenuAction = (action, ticketId) => {
    setContextMenu({ visible: false, ticketId: null, position: { x: 0, y: 0 } })

    switch (action) {
      case "rename":
        const ticket = tickets.find((t) => t.id === ticketId)
        console.log("Found ticket:", ticket)
        if (ticket) {
          setRenameTicketModal({
            visible: true,
            ticketId: ticketId,
            ticketName: ticket.name || "Без названия",
          })
        } else {
          console.warn("Ticket not found for rename action:", ticketId)
        }
        break
      case "toggle_share":
        handleToggleTicketShare(ticketId)
        break
      case "delete":
        handleDeleteTicket(ticketId)
        break
      default:
        break
    }
  }

  const getShareStatusText = (ticket) => {
    return ticket.shared ? "Закрыть тикет" : "Открыть тикет"
  }

  const closeContextMenu = () => {
    setContextMenu({ visible: false, ticketId: null, position: { x: 0, y: 0 } })
  }

  /**
   * Показывает уведомление
   * @param {string} text - Текст уведомления
   * @param {string} type - Тип уведомления: 'success', 'error', 'loading'
   * @param {string} eta - Время выполнения (опционально)
   */
  const showNotification = (text, type = "success", eta = "") => {
    setNotificationModal({
      visible: true,
      text,
      type,
      eta,
    })
  }

  /**
   * Закрывает уведомление
   */
  const closeNotification = () => {
    setNotificationModal({
      visible: false,
      text: "",
      type: "success",
      eta: "",
    })
  }

  /**
   * Обработчик успешного переименования тикета
   * @param {string} ticketId - ID переименованного тикета
   * @param {string} newName - Новое название тикета
   */
  const handleTicketRenamed = async (ticketId, newName) => {
    setFilterHistory((prevFilterHistory) =>
      prevFilterHistory.map((ticket) =>
        ticket.id === ticketId ? { ...ticket, name: newName } : ticket
      )
    )
    await fetchTicketHistory()
  }

  /**
   * Обработчик переключения статуса публикации тикета
   * @param {string} ticketId - ID тикета
   */
  const handleToggleTicketShare = async (ticketId) => {
    try {
      const ticket = tickets.find((t) => t.id === ticketId)
      const wasShared = ticket?.shared || false

      await ticketService.toggleTicketShare(ticketId)

      const newStatus = wasShared ? "закрыт" : "открыт"
      showNotification(`Тикет ${newStatus} для публичного просмотра`, "success")

      setFilterHistory((prevFilterHistory) =>
        prevFilterHistory.map((ticket) =>
          ticket.id === ticketId
            ? { ...ticket, shared: !ticket.shared }
            : ticket
        )
      )

      await fetchTicketHistory()
    } catch (error) {
      console.error("Ошибка при переключении статуса тикета:", error)
      showNotification("Ошибка при изменении статуса тикета", "error")
    }
  }

  /**
   * Обработчик удаления тикета
   * @param {string} ticketId - ID тикета
   */
  const handleDeleteTicket = async (ticketId) => {
    try {
      await ticketService.deleteTicket(ticketId)
      showNotification("Тикет успешно удален", "success")
      setFilterHistory((prev) =>
        prev.filter((ticket) => ticket.id !== ticketId)
      )

      await fetchTicketHistory()

      if (currentTicket && currentTicket.ticketId === ticketId) {
        setAccountSection("main")
        navigate("/account")
      }
    } catch (error) {
      console.error("Ошибка при удалении тикета:", error)
    }
  }

  const truncateString = (str, maxLength) => {
    if (str.length > maxLength) {
      return str.substring(0, maxLength) + "..."
    }
    return str
  }

  return (
    <>
      <div className={`accModal ${animate ? "animate" : ""}`}>
        <div className="titleBlockAccModal">
          <div
            onClick={() => {
              setAccountSection("info")
            }}
            className={
              accountSection === "info"
                ? "titleAccModalActive"
                : "titleAccModal"
            }
          >
            О нас
          </div>
          <div
            onClick={() => {
              setAccountSection("help")
            }}
            className={
              accountSection === "help"
                ? "titleAccModalActive"
                : "titleAccModal"
            }
          >
            Помощь
          </div>
          <div
            onClick={() => {
              setAccountSection("main")
              navigate("/account")
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
            <div
              className="containerScrollFileAccModal"
              ref={scrollContainerRef}
            >
              {filterHistory.map((ticket) => (
                <div
                  className={`fileLineAccModal ${
                    accountSection === "result" &&
                    currentTicket &&
                    ticket.id === currentTicket.ticketId
                      ? "activeTicket"
                      : ""
                  }`}
                  key={ticket.id}
                  onClick={() => handleFileLine(ticket)}
                >
                  <div className="fileAccModal">
                    {truncateString(ticket.name || "Без названия", 16)}
                    {ticket.isTemporary && (
                      <span
                        style={{
                          fontSize: "10px",
                          color: "#89AAFF",
                          marginLeft: "4px",
                        }}
                      >
                        (временный)
                      </span>
                    )}
                  </div>
                  {!ticket.isTemporary && (
                    <svg
                      style={{ marginRight: "25px", cursor: "pointer" }}
                      width="12"
                      height="12"
                      viewBox="0 0 12 12"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      data-ticket-id={ticket.id}
                      onClick={(e) => handleContextMenuClick(e, ticket)}
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
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Глобальное контекстное меню */}
      <ContextMenu
        visible={contextMenu.visible}
        ticketId={contextMenu.ticketId}
        onAction={handleContextMenuAction}
        position={contextMenu.position}
        getShareStatusText={() =>
          getShareStatusText(tickets.find((t) => t.id === contextMenu.ticketId))
        }
      />
      {renameTicketModal.visible && (
        <>
          {console.log(
            "Rendering RenameTicketModal with state:",
            renameTicketModal
          )}
          <RenameTicketModal
            setRenameTicketModal={(visible) =>
              setRenameTicketModal((prev) => ({ ...prev, visible }))
            }
            ticketId={renameTicketModal.ticketId}
            currentTicketName={renameTicketModal.ticketName}
            onTicketRenamed={handleTicketRenamed}
          />
        </>
      )}

      {/* Уведомления */}
      <NotificationModal
        visible={notificationModal.visible}
        text={notificationModal.text}
        type={notificationModal.type}
        eta={notificationModal.eta}
        onClose={closeNotification}
      />
    </>
  )
}
