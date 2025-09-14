import { motion } from "framer-motion"
import { useEffect, useRef, useCallback, useMemo } from "react"
import "./notificationModal.scss"

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
  type = "success",
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
      const isTicketStatus =
        textRef.current.includes("Тикет") &&
        textRef.current.includes("для публичного просмотра")
      const isTicketDeleted = textRef.current.includes("Тикет успешно удален")
      const timeoutDuration = isTicketStatus || isTicketDeleted ? 8000 : 15000

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

  return (
    <motion.div
      initial={{ opacity: 0, x: 100, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="notificationModal"
      role="status"
      aria-live="polite"
    >
      <div
        className={`contentNotificationModal ${
          type === "error" ? "errorContentNotificationModal" : ""
        }`}
      >
        <div className="iconNotificationModal">
          <div
            className={
              type === "loading"
                ? "clockIconNotificationModal"
                : type === "error"
                ? "errorIconNotificationModal"
                : "successIconNotificationModal"
            }
          >
            {type === "loading" ? (
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
            ) : type === "error" ? (
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
          className={`textNotificationModal ${
            centered ? "centeredTextNotificationModal" : ""
          } ${type === "loading" ? "withTopMarginNotificationModal" : ""} ${
            type === "success" ? "withTopMarginNotificationModal" : ""
          } ${type === "error" ? "withErrorMarginNotificationModal" : ""} ${
            text.includes("Тикет") && text.includes("для публичного просмотра")
              ? "ticketStatusNotificationModal"
              : ""
          } ${
            text.includes("Результат еще не готов, ожидайте")
              ? "resultNotReadyNotificationModal"
              : ""
          } ${
            text.includes("Ваш запрос принят в обработку")
              ? "requestAcceptedNotificationModal"
              : ""
          } ${
            text.includes("Тикет успешно удален")
              ? "ticketDeletedNotificationModal"
              : ""
          }`}
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
