import $api from "../api/axios.api"

/**
 * Сервис для работы с тикетами
 */
class TicketService {
  /**
   * Получает список всех мероприятий
   * @returns {Promise<Array>} Массив мероприятий
   */
  async getEvents() {
    try {
      const response = await $api.get("/actions/get_events")
      return response.data.events
    } catch (error) {
      console.error("Error fetching events:", error)
      throw error
    }
  }

  /**
   * Получает историю тикетов пользователя
   * @returns {Promise<Array>} Массив тикетов
   */
  async getTicketHistory() {
    try {
      const response = await $api.get("/account/ticket_history")
      return response.data.tickets
    } catch (error) {
      console.error("Error fetching ticket history:", error)
      throw error
    }
  }

  /**
   * Создает новый тикет
   * @param {File} file - Загруженный файл
   * @param {string} eventId - ID мероприятия
   * @returns {Promise<{ticket_id: string}>} ID созданного тикета
   */
  async createNewTicket(file, eventId) {
    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("event_id", eventId)

      const response = await $api.post("/actions/new_ticket", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      return response.data
    } catch (error) {
      console.error("Error creating new ticket:", error)
      throw error
    }
  }

  /**
   * Получает ID мероприятия по его названию
   * @param {string} eventName - Название мероприятия
   * @returns {Promise<{event_id: string}>} ID мероприятия
   */
  async getEventId(eventName) {
    try {
      const response = await $api.get("/actions/get_event_id", {
        params: { event_name: eventName },
      })
      return response.data
    } catch (error) {
      console.error("Error getting event ID:", error)
      throw error
    }
  }

  /**
   * Получает информацию о тикете
   * @param {string} ticketId - ID тикета
   * @returns {Promise<Object>} Информация о тикете
   */
  async getTicket(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket", {
        params: { ticket_id: ticketId },
      })
      return response.data
    } catch (error) {
      console.error("Error getting ticket:", error)
      throw error
    }
  }

  /**
   * Получает файл тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<Blob>} Файл тикета
   */
  async getTicketFile(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket_file", {
        params: { ticket_id: ticketId },
        responseType: "blob",
      })
      return response.data
    } catch (error) {
      console.error("Error getting ticket file:", error)
      throw error
    }
  }

  /**
   * Получает сводку тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<Blob>} Сводка тикета
   */
  async getTicketSummary(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket_summary", {
        params: { ticket_id: ticketId },
        responseType: "blob",
      })
      return response.data
    } catch (error) {
      console.error("Error getting ticket summary:", error)
      throw error
    }
  }

  /**
   * Получает результат тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<Blob>} Результат тикета
   */
  async getTicketResult(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket_result", {
        params: { ticket_id: ticketId },
        responseType: "blob",
      })
      return response.data
    } catch (error) {
      console.error("Error getting ticket result:", error)
      throw error
    }
  }

  /**
   * Изменяет статус публикации тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<Object>} Результат операции
   */
  async shareTicket(ticketId) {
    try {
      const response = await $api.post("/actions/ticket_share", {
        ticket_id: ticketId,
      })
      return response.data
    } catch (error) {
      console.error("Error sharing ticket:", error)
      throw error
    }
  }
}

export const ticketService = new TicketService()
