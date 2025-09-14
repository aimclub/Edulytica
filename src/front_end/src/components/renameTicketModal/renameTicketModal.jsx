import { useState, useEffect } from "react"
import { Input } from "../../utils/input/input"
import "./renameTicketModal.scss"
import { ticketService } from "../../services/ticket.service"
import {
  validateTicketName,
  validateBackend,
} from "../../utils/validation/validationUtils"

export const RenameTicketModal = ({
  setRenameTicketModal,
  ticketId,
  currentTicketName,
  onTicketRenamed,
}) => {
  const [newName, setNewName] = useState(currentTicketName || "")
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState({})

  /**
   * Обновляет локальное состояние при изменении currentTicketName.
   */
  useEffect(() => {
    setNewName(currentTicketName || "")
  }, [currentTicketName])

  /**
   * Валидация формы переименования тикета
   */
  const validateRenameForm = () => {
    const newErrors = {
      name: validateTicketName(newName),
    }

    Object.keys(newErrors).forEach(
      (key) => newErrors[key] === null && delete newErrors[key]
    )
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  /**
   * Обработчик отправки формы переименования тикета.
   * Отправляет новое имя тикета на сервер.
   */
  const handleRenameTicket = async () => {
    if (!validateRenameForm()) {
      return
    }

    if (newName.trim() === currentTicketName) {
      setRenameTicketModal(false)
      return
    }

    setIsLoading(true)
    setErrors({})

    try {
      await ticketService.renameTicket(ticketId, newName.trim())

      // Вызываем callback для обновления данных
      if (onTicketRenamed) {
        onTicketRenamed(ticketId, newName.trim())
      }

      setRenameTicketModal(false)
    } catch (error) {
      console.error("Ошибка при переименовании тикета:", error)
      const backendErrors = validateBackend(error.detail)
      setErrors((prevErrors) => ({
        ...prevErrors,
        ...backendErrors,
      }))
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Обработчик нажатия клавиши Enter в поле ввода.
   */
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isLoading) {
      handleRenameTicket()
    }
  }

  return (
    <div className="renameTicketModalOverlay">
      <div className="renameTicketModal">
        <div className="titleRenameTicketModal">Переименовать тикет</div>
        <div className="containerRenameTicketModal">
          <div className="blockInputRenameTicketModal">
            <div className="titleInputRenameTicketModal">Новое имя</div>
            <Input
              type="text"
              placeholder="Введите новое название тикета..."
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            {errors.name && (
              <div className="errorTextRenameTicketModal">{errors.name}</div>
            )}
          </div>
          <div
            className={`btnBottomRenameTicketModal ${
              isLoading ? "loading" : ""
            }`}
            onClick={handleRenameTicket}
          >
            {isLoading ? "Сохранение..." : "Переименовать"}
          </div>
        </div>
        <svg
          onClick={() => setRenameTicketModal(false)}
          className="closeButtonRenameTicketModal"
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
