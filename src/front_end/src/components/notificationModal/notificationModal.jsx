import { motion } from "framer-motion"
import { useEffect, useRef } from "react"
import "./notificationModal.scss"

/**
 * Компонент для отображения модального окна уведомления в правом углу
 * @param {Object} props - Свойства компонента
 * @param {boolean} props.visible - Видимо ли уведомление
 * @param {string} props.text - Основной текст уведомления
 * @param {string} props.eta - Примерное время выполнения
 * @param {Function} props.onClose - Функция для закрытия уведомления
 * @param {boolean} props.centered - Центрировать ли текст
 * @returns {JSX.Element} Компонент модального окна уведомления
 */
export const NotificationModal = ({
  visible,
  text,
  eta,
  onClose,
  centered = false,
}) => {
  const timeoutRef = useRef(null)

  useEffect(() => {
    if (visible) {
      timeoutRef.current = setTimeout(() => {
        onClose()
      }, 15000)
    }
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
    }
  }, [visible, onClose])

  if (!visible) return null

  return (
    <motion.div
      initial={{ opacity: 0, x: 100, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.9 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="notification-modal"
      role="status"
      aria-live="polite"
    >
      <div className="notification-content">
        <div className="notification-icon">
          <div
            className={
              text === "Результат еще не готов, ожидайте"
                ? "clock-icon"
                : "success-icon"
            }
          >
            {text === "Результат еще не готов, ожидайте" ? (
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
            ) : (
              "✓"
            )}
          </div>
        </div>

        <div
          className={`notification-text ${centered ? "centered" : ""} ${
            text === "Результат еще не готов, ожидайте" ? "with-top-margin" : ""
          }`}
        >
          <h3 className="notification-title">{text}</h3>
          {eta && (
            <p className="notification-eta">Примерное время ожидания: {eta}</p>
          )}
        </div>

        <button
          className="notification-close"
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
