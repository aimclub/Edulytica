import "../feedback/feedbackModal.scss"
import "./eventModal.scss"
import { createPortal } from "react-dom"

export const EventInfoModal = ({ title, description, onClose }) => {
  const modalContent = (
    <div className="feedbackModalOverlay" onClick={onClose}>
      <div className="feedbackModal" onClick={(e) => e.stopPropagation()}>
        <div className="titleFeedbackModal">{title}</div>
        <div className="containerFeedbackModal">
          <div className="blockInputFeedbackModal">
            <div className="titleInputFeedbackModal">Описание</div>
            <div className="eventInfoDescription">{description}</div>
          </div>
        </div>
        <svg
          onClick={onClose}
          className="closeButtonFeedbackModal"
          width="24"
          height="24"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M8.53464 25.3327L6.66797 23.466L14.1346 15.9993L6.66797 8.53268L8.53464 6.66602L16.0013 14.1327L23.468 6.66602L25.3346 8.53268L17.868 15.9993L25.3346 23.466L23.468 25.3327L16.0013 17.866L8.53464 25.3327Z"
            fill="white"
          />
        </svg>
      </div>
    </div>
  )

  if (typeof document !== "undefined") {
    return createPortal(modalContent, document.body)
  }

  return modalContent
}
