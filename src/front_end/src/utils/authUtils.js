import { authService } from "../services/auth.service"
import store from "../store/store"

/**
 * Проверяет, истек ли токен доступа
 * @param {string} token - JWT токен
 * @returns {boolean} true если токен истек
 */
export const isTokenExpired = (token) => {
  if (!token) return true

  try {
    const payload = JSON.parse(atob(token.split(".")[1]))
    const currentTime = Date.now() / 1000

    return payload.exp < currentTime
  } catch (error) {
    console.error("Error parsing token:", error)
    return true
  }
}

/**
 * Выполняет принудительный logout при истечении токенов
 */
export const forceLogout = async () => {
  try {
    await authService.logout()
  } catch (error) {
    store.dispatch({ type: "auth/logoutUser" })
  }
  // Если мы не на главной странице, делаем редирект
  if (window.location.pathname !== "/") {
    window.location.href = "/"
  }
}
