import { useState } from "react"
import "./feedbackModal.scss"
import {
  validateFeedbackName,
  validateFeedbackEmail,
  validateFeedbackMessage,
  validateBackend,
} from "../../utils/validation/validationUtils"

export const FeedbackModal = ({ onClose, onSubmit }) => {
  const [message, setMessage] = useState("")
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  /**
   * Валидация формы обратной связи
   */
  const validateFeedbackForm = () => {
    const newErrors = {
      name: validateFeedbackName(name),
      email: validateFeedbackEmail(email),
      message: validateFeedbackMessage(message),
    }

    setErrors(newErrors)
    return (
      Object.keys(newErrors).filter((key) => newErrors[key] !== null).length ===
      0
    )
  }

  const handleSubmit = async () => {
    if (!validateFeedbackForm()) {
      return
    }

    setIsLoading(true)
    setErrors({})

    try {
      if (onSubmit) {
        await onSubmit({
          name: name.trim(),
          email: email.trim(),
          text: message.trim(),
        })
      }
      onClose?.()
    } catch (error) {
      console.error("Ошибка при отправке обратной связи:", error)
      const backendErrors = validateBackend(error.detail)
      setErrors((prevErrors) => ({
        ...prevErrors,
        ...backendErrors,
      }))
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey) && !isLoading) {
      handleSubmit()
    }
  }

  return (
    <div className="feedbackModalOverlay" onClick={onClose}>
      <div className="feedbackModal" onClick={(e) => e.stopPropagation()}>
        <div className="titleFeedbackModal">Обратная связь</div>
        <div className="containerFeedbackModal">
          <div className="blockInputFeedbackModal">
            <div className="titleInputFeedbackModal">ФИО</div>
            <input
              type="text"
              className="inputFeedbackModal"
              placeholder="Иванов Иван Иванович"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isLoading}
            />
            {errors.name && (
              <div className="errorTextFeedbackModal">{errors.name}</div>
            )}
          </div>
          <div className="blockInputFeedbackModal">
            <div className="titleInputFeedbackModal">Почта</div>
            <input
              type="email"
              className="inputFeedbackModal"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
            {errors.email && (
              <div className="errorTextFeedbackModal">{errors.email}</div>
            )}
          </div>
          <div className="blockInputFeedbackModal">
            <div className="titleInputFeedbackModal">Сообщение</div>
            <textarea
              className="textareaFeedbackModal"
              placeholder="Опишите проблему, идею или вопрос..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            {(errors.message || errors.general) && (
              <div className="errorTextFeedbackModal">
                {errors.message || errors.general}
              </div>
            )}
          </div>

          <div
            className={`btnBottomFeedbackModal ${isLoading ? "loading" : ""}`}
            onClick={!isLoading ? handleSubmit : undefined}
          >
            {isLoading ? "Отправка..." : "Отправить"}
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
}
