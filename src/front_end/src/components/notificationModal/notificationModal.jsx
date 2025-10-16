import { motion } from "framer-motion"
import { useEffect, useRef } from "react"
import "./notificationModal.scss"

// Константы для типов уведомлений
const NOTIFICATION_TYPES = {
  SUCCESS: "success",
  ERROR: "error",
  LOADING: "loading",
}

// Константы для типов сообщений
const MESSAGE_TYPES = {
  TICKET_STATUS: "ticketStatus",
  TICKET_DELETED: "ticketDeleted",
  TICKET_READY: "ticketReady",
  RESULT_NOT_READY: "resultNotReady",
  REQUEST_ACCEPTED: "requestAccepted",
  WIDE_MESSAGE: "wideMessage",
  PDF_FORMAT: "pdfFormat",
}

// Константы для таймаутов
const TIMEOUTS = {
  DEFAULT: 15000,
  TICKET_STATUS: 8000,
  TICKET_DELETED: 8000,
}

// Вспомогательные функции для определения типов сообщений
const getMessageType = (text) => {
  if (!text || typeof text !== "string") return null

  if (text.includes("Тикет") && text.includes("для публичного просмотра")) {
    return MESSAGE_TYPES.TICKET_STATUS
  }
  if (text.includes("Тикет успешно удален")) {
    return MESSAGE_TYPES.TICKET_DELETED
  }
  if (text.includes("Тикет готов")) {
    return MESSAGE_TYPES.TICKET_READY
  }
  if (text.includes("Результат еще не готов, ожидайте")) {
    return MESSAGE_TYPES.RESULT_NOT_READY
  }
  if (text.includes("Ваш запрос принят в обработку")) {
    return MESSAGE_TYPES.REQUEST_ACCEPTED
  }
  if (text.includes("загрузите файл в формате PDF.")) {
    return MESSAGE_TYPES.PDF_FORMAT
  }
  if (
    text.includes("Максимальный допустимый размер") ||
    text.includes("превышает 50") ||
    text.includes("Выбор мероприятия обязателен")
  ) {
    return MESSAGE_TYPES.WIDE_MESSAGE
  }

  return null
}

const getTimeoutDuration = (messageType) => {
  switch (messageType) {
    case MESSAGE_TYPES.TICKET_STATUS:
    case MESSAGE_TYPES.TICKET_DELETED:
      return TIMEOUTS.TICKET_STATUS
    default:
      return TIMEOUTS.DEFAULT
  }
}

// Функция для получения CSS классов
const getNotificationClasses = (type, messageType, isWideMessage, centered) => {
  const baseClasses = ["notificationModal"]

  if (isWideMessage) {
    baseClasses.push("wideNotificationModal")
  }

  return baseClasses.join(" ")
}

const getContentClasses = (type) => {
  const baseClasses = ["contentNotificationModal"]

  if (type === NOTIFICATION_TYPES.ERROR) {
    baseClasses.push("errorContentNotificationModal")
  }

  return baseClasses.join(" ")
}

const getTextClasses = (type, messageType, isWideMessage, centered) => {
  const baseClasses = ["textNotificationModal"]

  if (centered) {
    baseClasses.push("centeredTextNotificationModal")
  }

  if (
    type === NOTIFICATION_TYPES.LOADING ||
    type === NOTIFICATION_TYPES.SUCCESS
  ) {
    baseClasses.push("withTopMarginNotificationModal")
  }

  if (type === NOTIFICATION_TYPES.ERROR) {
    baseClasses.push("withErrorMarginNotificationModal")
  }

  if (isWideMessage) {
    baseClasses.push("wideNotificationModal")
  }

  // Добавляем специфичные классы для типов сообщений
  if (messageType) {
    baseClasses.push(`${messageType}NotificationModal`)
  }

  return baseClasses.join(" ")
}

const getIconClasses = (type) => {
  switch (type) {
    case NOTIFICATION_TYPES.LOADING:
      return "clockIconNotificationModal"
    case NOTIFICATION_TYPES.ERROR:
      return "errorIconNotificationModal"
    case NOTIFICATION_TYPES.SUCCESS:
    default:
      return "successIconNotificationModal"
  }
}

/**
 * Компонент для отображения модального окна уведомления в правом углу
 * @param {Object} props - Свойства компонента
 * @param {boolean} props.visible - Видимо ли уведомление
 * @param {string} props.text - Основной текст уведомления
 * @param {string} props.type - Тип уведомления: 'success', 'error', 'loading'
 * @param {string} props.eta - Примерное время выполнения
 * @param {Function} props.onClose - Функция для закрытия уведомления
 * @param {boolean} props.centered - Центрировать ли текст
 * @returns {JSX.Element} Компонент модального окна уведомления
 */
export const NotificationModal = ({
  visible,
  text,
  type = NOTIFICATION_TYPES.SUCCESS,
  eta,
  onClose,
  centered = false,
}) => {
  const timeoutRef = useRef(null)
  const onCloseRef = useRef(onClose)
  const textRef = useRef(text)
  onCloseRef.current = onClose
  textRef.current = text

  useEffect(() => {
    if (visible) {
      const messageType = getMessageType(textRef.current)
      const timeoutDuration = getTimeoutDuration(messageType)

      timeoutRef.current = setTimeout(() => {
        onCloseRef.current()
      }, timeoutDuration)
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
    }
  }, [visible])

  if (!visible) return null

  const messageType = getMessageType(text)
  const isWideMessage = messageType === MESSAGE_TYPES.WIDE_MESSAGE

  return (
    <motion.div
      initial={{ opacity: 0, x: 100, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={getNotificationClasses(
        type,
        messageType,
        isWideMessage,
        centered
      )}
      role="status"
      aria-live="polite"
    >
      <div className={getContentClasses(type)}>
        <div className="iconNotificationModal">
          <div className={getIconClasses(type)}>
            {type === NOTIFICATION_TYPES.LOADING ? (
              <svg
                width="20"
                height="20"
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M24 12V24L32 28M44 24C44 35.0457 35.0457 44 24 44C12.9543 44 4 35.0457 4 24C4 12.9543 12.9543 4 24 4C35.0457 4 44 12.9543 44 24Z"
                  stroke="currentColor"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : type === NOTIFICATION_TYPES.ERROR ? (
              <svg
                width="20"
                height="20"
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M24 16V24M24 32H24.02M44 24C44 35.0457 35.0457 44 24 44C12.9543 44 4 35.0457 4 24C4 12.9543 12.9543 4 24 4C35.0457 4 44 12.9543 44 24Z"
                  stroke="#e74c3c"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : (
              "✓"
            )}
          </div>
        </div>

        <div
          className={getTextClasses(type, messageType, isWideMessage, centered)}
        >
          <h3 className="titleNotificationModal">{text}</h3>
          {eta && (
            <p className="etaNotificationModal">
              Примерное время ожидания: {eta}
            </p>
          )}
        </div>

        <button
          className="closeNotificationModal"
          onClick={() => {
            if (timeoutRef.current) {
              clearTimeout(timeoutRef.current)
              timeoutRef.current = null
            }
            onClose()
          }}
          aria-label="Закрыть уведомление"
        >
          ✕
        </button>
      </div>
    </motion.div>
  )
}
