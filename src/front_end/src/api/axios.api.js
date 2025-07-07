import axios from "axios"
/**
 * Модуль для настройки и экспорта экземпляра axios для API запросов.
 *
 * Создает настроенный экземпляр axios с базовыми параметрами:
 * - baseURL: URL API сервера (из переменных окружения или localhost:8000)
 * - withCredentials: true (для работы с куками)
 * - headers: установка Content-Type для JSON
 */

export const API_URL = process.env.REACT_APP_API_URL || "http://10.22.8.250:18080"

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
