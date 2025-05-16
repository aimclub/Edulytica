import axios from "axios"
import store from "../store/store"
import { loginUser, logoutUser } from "../store/authSlice"

export const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

const $api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

// Функция для проверки и обновления токена
export const validateToken = async () => {
  const token = store.getState().auth.token
  if (token) {
    try {
      const response = await axios.get(`${API_URL}/auth/get_access`, {
        withCredentials: true,
      })
      store.dispatch(loginUser({ token: response.data.access_token }))
      return true
    } catch (e) {
      store.dispatch(logoutUser())
      return false
    }
  }
  return false
}

// Интерцептор для обработки запросов к серверу
$api.interceptors.request.use((config) => {
  const token = store.getState().auth.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Интерцептор для обработки ответов от сервера
$api.interceptors.response.use(
  (config) => {
    return config
  },
  async (error) => {
    const originalRequest = error.config

    if (
      error.response.status === 401 &&
      error.config &&
      !error.config._isRetry
    ) {
      originalRequest._isRetry = true
      try {
        const response = await axios.get(`${API_URL}/auth/get_access`, {
          withCredentials: true,
        })
        store.dispatch(loginUser({ token: response.data.access_token }))
        originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
        return $api.request(originalRequest)
      } catch (e) {
        store.dispatch(logoutUser())
      }
    }
    throw error
  }
)

export default $api
