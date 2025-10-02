import axios from "axios"
/**
 * Модуль для настройки и экспорта экземпляра axios для API запросов.
 *
 * Создает настроенный экземпляр axios с базовыми параметрами:
 * - baseURL: URL API сервера (из переменных окружения или localhost:8000)
 * - withCredentials: true (для работы с куками)
 * - headers: установка Content-Type для JSON
 */

export const API_URL =
  process.env.REACT_APP_API_URL || "http://10.22.8.250:18080"
// export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080"
const $api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

/**
 * Интерцептор запросов для автоматического добавления токена авторизации.
 */
$api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authState")
      ? JSON.parse(localStorage.getItem("authState")).token
      : null

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default $api

/**
 * Интерцептор запросов для обработки ошибок.
 */
$api.interceptors.response.use(
  (response) => response,
  (error) => {
    try {
      const status = error?.response?.status
      let message = "Ошибка сети. Попробуйте позже."

      // Debug logging
      console.log("Axios interceptor error:", {
        status,
        message: error?.message,
        response: error?.response,
        config: error?.config?.url,
      })

      switch (status) {
        case 502:
          message = "Сервер временно недоступен. Попробуйте позже."
          break
        case 500:
          message = "Внутренняя ошибка сервера."
          break
        case 404:
          message = "Ресурс не найден."
          break
        case 403:
          message = "Доступ запрещён."
          break
        case 401:
          message = "Необходима авторизация."
          break
        default:
          if (error?.message === "Network Error") {
            message = "Ошибка сети. Попробуйте позже."
          } else if (error?.message && !status) {
            message = error.message
          }
          break
      }

      const data = error?.response?.data
      if (data) {
        const detail = data.detail || data.message || data.error || data.errors
        let detailText = ""
        if (typeof detail === "string") {
          detailText = detail
        } else if (Array.isArray(detail)) {
          detailText = detail
            .map((d) => (typeof d === "string" ? d : JSON.stringify(d)))
            .join("; ")
        } else if (typeof detail === "object") {
          const maybe = detail.msg || detail.detail || detail.message
          detailText =
            typeof maybe === "string" ? maybe : JSON.stringify(detail)
        }
        if (detailText) {
          message = `${message}: ${detailText}`
        }
      }

      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent("api:error", { detail: { message } })
        )
      }
    } catch (_) {
      // no-op
    }
    return Promise.reject(error)
  }
)
