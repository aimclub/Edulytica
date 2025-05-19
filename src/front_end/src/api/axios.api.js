import axios from "axios"
/**
 * Модуль для настройки и экспорта экземпляра axios для API запросов.
 *
 * Создает настроенный экземпляр axios с базовыми параметрами:
 * - baseURL: URL API сервера (из переменных окружения или localhost:8000)
 * - withCredentials: true (для работы с куками)
 * - headers: установка Content-Type для JSON
 */

export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

const $api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

export default $api
