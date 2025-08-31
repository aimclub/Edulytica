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
   * @param {string} mega_task_id - ID мега-задачи (1 для рецензирования, 2 для анализа)
   * @returns {Promise<{ticket_id: string}>} ID созданного тикета
   */
  async createNewTicket(file, eventId, mega_task_id) {
    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("event_id", eventId)
      formData.append("mega_task_id", mega_task_id)

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
   * Скачивает файл результата тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<void>} Скачивает файл
   */
  async downloadResult(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket_result", {
        params: { ticket_id: ticketId },
        responseType: "blob",
      })

      // Получаем имя файла из заголовков ответа или используем дефолтное
      const contentDisposition = response.headers["content-disposition"]
      let filename = `result_${ticketId}.pdf`

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement("a")
      link.href = url
      link.download = filename

      // Добавляем ссылку в DOM и кликаем по ней
      document.body.appendChild(link)
      link.click()

      // Удаляем ссылку
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Error downloading result:", error)
      throw error
    }
  }

  /**
   * Скачивает исходный файл документа тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<void>} Скачивает файл
   */
  async downloadDocument(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket_file", {
        params: { ticket_id: ticketId },
        responseType: "blob",
      })

      // Получаем имя файла из заголовков ответа или используем дефолтное
      const contentDisposition = response.headers["content-disposition"]
      let filename = `document_${ticketId}.pdf`

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement("a")
      link.href = url
      link.download = filename

      // Добавляем ссылку в DOM и кликаем по ней
      document.body.appendChild(link)
      link.click()

      // Удаляем ссылку
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Error downloading document:", error)
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

  /**
   * Получает статус тикета
   * @param {string} ticketId - ID тикета
   * @returns {Promise<Object>} Статус тикета
   */
  async getTicketStatus(ticketId) {
    try {
      const response = await $api.get("/actions/get_ticket_status", {
        params: { ticket_id: ticketId },
      })
      return response.data
    } catch (error) {
      console.error("Error getting ticket status:", error)
      throw error
    }
  }

  /**
   * Парсит файл через /actions/parse_file_text
   * @param {Blob|File} file - Файл для парсинга
   * @returns {Promise<string>} Текст, распарсенный с бэкенда
   */
  async parseFileText(file) {
    try {
      const formData = new FormData()
      formData.append("file", file)
      const response = await $api.post("/actions/parse_file_text", formData, {
        headers: {
          "Content-Type": "application/pdf",
        },
      })
      return response.data.text
    } catch (error) {
      console.error("Error parsing file text:", error)
      throw error
    }
  }

  /**
   * Получает текст документа тикета напрямую
   * @param {string} ticketId - ID тикета
   * @returns {Promise<{detail: string, text: string}>} Текст документа
   */
  async getDocumentText(ticketId) {
    try {
      const response = await $api.get("/actions/get_document_text", {
        params: { ticket_id: ticketId },
      })
      return response.data
    } catch (error) {
      console.error("Error getting document text:", error)
      throw error
    }
  }

  /**
   * Получает текст результата тикета напрямую
   * @param {string} ticketId - ID тикета
   * @returns {Promise<{detail: string, text: string}>} Текст результата
   */
  async getResultText(ticketId) {
    try {
      const response = await $api.get("/actions/get_result_text", {
        params: { ticket_id: ticketId },
      })
      return response.data
    } catch (error) {
      console.error("Error getting result text:", error)
      throw error
    }
  }

  /**
   * Добавляет новое кастомное мероприятие
   * @param {string} eventName - Название мероприятия
   * @param {string} description - Описание/критерии мероприятия
   * @returns {Promise<Object>} Результат добавления
   */
  async addCustomEvent(eventName, description) {
    try {
      const response = await $api.post("/actions/add_custom_event", {
        event_name: eventName,
        description: description,
      })
      return response.data
    } catch (error) {
      console.error("Error adding custom event:", error)
      throw error
    }
  }
}

export const ticketService = new TicketService()
