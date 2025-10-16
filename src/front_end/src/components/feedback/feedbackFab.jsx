import { useState, useCallback, useEffect } from "react"
import { FeedbackModal } from "./feedbackModal"
import { FeedbackNotification } from "./feedbackNotification"
import { ticketService } from "../../services/ticket.service"
import "./feedbackModal.scss"

export const FeedbackFab = () => {
  const [open, setOpen] = useState(false)
  const [showNotification, setShowNotification] = useState(false)

  const handleSubmit = useCallback(async (payload) => {
    try {
      await ticketService.sendFeedback(payload)
    } catch (e) {
      throw e
    }
  }, [])

  useEffect(() => {
    const hasSeenNotification = localStorage.getItem("feedbackNotificationSeen")

    if (!hasSeenNotification) {
      const timer = setTimeout(() => {
        setShowNotification(true)
      }, 1000)

      return () => clearTimeout(timer)
    }
  }, [])

  const handleNotificationClose = useCallback(() => {
    setShowNotification(false)
    localStorage.setItem("feedbackNotificationSeen", "true")
  }, [])

  return (
    <>
      <button
        className="feedbackFabButton"
        aria-label="Обратная связь"
        onClick={() => {
          setOpen(true)
          setShowNotification(false)
          localStorage.setItem("feedbackNotificationSeen", "true")
        }}
        title="Обратная связь"
      >
        <svg
          className="feedbackFabIcon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"
            fill="#EAEAEA"
          />
        </svg>
      </button>
      {open && (
        <FeedbackModal onClose={() => setOpen(false)} onSubmit={handleSubmit} />
      )}
      {showNotification && (
        <FeedbackNotification onClose={handleNotificationClose} />
      )}
    </>
  )
}
