import { useState, useCallback } from "react"
import { FeedbackModal } from "./feedbackModal"
import { ticketService } from "../../services/ticket.service"
import "./feedbackModal.scss"

export const FeedbackFab = () => {
  const [open, setOpen] = useState(false)

  const handleSubmit = useCallback(async (payload) => {
    try {
      await ticketService.sendFeedback(payload)
    } catch (e) {
      throw e
    }
  }, [])

  return (
    <>
      <button
        className="feedbackFabButton"
        aria-label="Обратная связь"
        onClick={() => setOpen(true)}
        title="Обратная связь"
      >
        <svg
          className="feedbackFabIcon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 3c-4.97 0-9 3.58-9 8 0 2.04.86 3.9 2.29 5.32L4 21l4.83-1.3C10.18 20.55 11.07 21 12 21c4.97 0 9-3.58 9-8s-4.03-10-9-10Zm-4 8h8m-8 3h5m3-6H8"
            stroke="#EAEAEA"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      {open && (
        <FeedbackModal onClose={() => setOpen(false)} onSubmit={handleSubmit} />
      )}
    </>
  )
}
