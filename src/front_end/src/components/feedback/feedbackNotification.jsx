import { useState, useEffect, useCallback } from "react"
import "./feedbackNotification.scss"

export const FeedbackNotification = ({ onClose }) => {
  const [isVisible, setIsVisible] = useState(false)

  const handleClose = useCallback(() => {
    setIsVisible(false)
    setTimeout(() => {
      onClose?.()
    }, 300)
  }, [onClose])

  useEffect(() => {
    const showTimer = setTimeout(() => {
      setIsVisible(true)
    }, 100)

    const autoCloseTimer = setTimeout(() => {
      handleClose()
    }, 15000)

    return () => {
      clearTimeout(showTimer)
      clearTimeout(autoCloseTimer)
    }
  }, [handleClose])

  return (
    <div className={`feedbackNotification ${isVisible ? "visible" : ""}`}>
      <div className="notificationContent">
        <div className="notificationText">
          Есть вопрос/проблема/предложение? Вам сюда!
        </div>
        <button
          className="notificationClose"
          onClick={handleClose}
          aria-label="Закрыть уведомление"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path
              d="M9 3L3 9M3 3L9 9"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
      <div className="notificationArrow"></div>
    </div>
  )
}
