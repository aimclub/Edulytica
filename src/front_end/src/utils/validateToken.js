/**
 * Модуль для валидации и обновления токена доступа пользователя.
 *
 * Этот файл содержит функцию validateToken, которая:
 * 1. Проверяет наличие токена в Redux store
 * 2. При наличии токена делает запрос на обновление токена доступа
 * 3. При успешном обновлении сохраняет новый токен и обновляет состояние авторизации
 * 4. При неудаче выполняет выход пользователя из системы
 *
 * @module validateToken
 */

import axios from "axios"
import { API_URL } from "../api/axios.api"
import store from "../store/store"
import { loginUser, logoutUser } from "../store/authSlice"

// Try to refresh access token; on success dispatch loginUser, otherwise logout
export async function validateToken() {
  const { token } = store.getState().auth
  if (!token) return false

  try {
    const resp = await axios.get(`${API_URL}/auth/get_access`, {
      withCredentials: true,
    })
    store.dispatch(loginUser({ token: resp.data.access_token }))
    return true
  } catch {
    store.dispatch(logoutUser())
    return false
  }
}
