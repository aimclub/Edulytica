// import $api from "../api/axios.api"

/**
 * Сервис для работы с тикетами
 */
class TicketService {
  /**
   * Получает историю тикетов пользователя
   * @returns {Promise<Array>} Массив тикетов
   */
  async getTicketHistory() {
    // try {
    //    const response = await $api.get("/account/ticket_history")
    //    return response.data.tickets

    // } catch (error) {
    //   console.error("Error fetching ticket history:", error)
    //   throw error
    // }

    //временная заглушка
    return [
      {
        id: "uuid",
        shared: false,
        user_id: "uuid",
        ticket_type_id: "uuid",
        ticket_status_id: "uuid",
        event_id: "uuid",
        custom_event_id: "uuid",
        custom_event_user_id: "uuid",
        document_id: "1",
        document_summary_id: "uuid",
        document_report_id: "uuid",
        created_at: "2024-06-01T12:34:56+03:00",
      },
      {
        id: "uuid",
        shared: false,
        user_id: "uuid",
        ticket_type_id: "uuid",
        ticket_status_id: "uuid",
        event_id: "uuid",
        custom_event_id: "uuid",
        custom_event_user_id: "uuid",
        document_id: "2",
        document_summary_id: "uuid",
        document_report_id: "uuid",
        created_at: "2024-06-01T12:34:56+03:00",
      },
      {
        id: "uuid",
        shared: false,
        user_id: "uuid",
        ticket_type_id: "uuid",
        ticket_status_id: "uuid",
        event_id: "uuid",
        custom_event_id: "uuid",
        custom_event_user_id: "uuid",
        document_id: "3",
        document_summary_id: "uuid",
        document_report_id: "uuid",
        created_at: "2024-06-01T12:34:56+03:00",
      },
    ]
  }
}

export const ticketService = new TicketService()
