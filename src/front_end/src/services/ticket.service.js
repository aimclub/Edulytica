import $api from "../api/axios.api"

/**
 * Сервис для работы с тикетами
 */
class TicketService {
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
}

export const ticketService = new TicketService()
