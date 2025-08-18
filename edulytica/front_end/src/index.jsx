import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App"
import "./assets/css/global.scss"
import { Provider } from "react-redux"
import store from "./store/store"
import $api, { API_URL } from "./api/axios.api"
import axios from "axios"
import { loginUser } from "./store/authSlice"
import { forceLogout } from "./utils/authUtils"

/**
 * Интерцептор для обработки ответов API.
 *
 * Логика работы:
 * 1. При получении ошибки 401 (Unauthorized):
 *    - Проверяет, не была ли уже попытка повтора запроса
 *    - Делает запрос на обновление токена
 *    - При успехе обновляет токен в store и повторяет исходный запрос
 *    - При неудаче выполняет выход пользователя и редирект на главную
 * 2. При других ошибках - отклоняет промис с ошибкой
 */
$api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    // Не обрабатывать 401 для /auth/logout и /auth/get_access
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes("/auth/logout") &&
      !originalRequest.url.includes("/auth/get_access")
    ) {
      originalRequest._retry = true
      try {
        const resp = await axios.get(`${API_URL}/auth/get_access`, {
          withCredentials: true,
        })
        store.dispatch(loginUser({ token: resp.data.access_token }))
        originalRequest.headers.Authorization = `Bearer ${resp.data.access_token}`
        return $api.request(originalRequest)
      } catch (refreshError) {
        await forceLogout("Сессия истекла")
      }
    }
    return Promise.reject(error)
  }
)

const root = ReactDOM.createRoot(document.getElementById("root"))
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
)
