import $api from "../api/axios.api"
import store from "../store/store"
import { loginUser, logoutUser } from "../store/authSlice"

/**
 * @typedef {Object} LoginCredentials
 * @property {string} login - Логин пользователя
 * @property {string} password - Пароль пользователя
 */

/**
 * @typedef {Object} RegistrationCredentials
 * @property {string} login - Логин пользователя
 * @property {string} email - Email пользователя
 * @property {string} password - Пароль пользователя
 * @property {string} repeatPassword - Повторный ввод пароля
 */

/**
 * @typedef {Object} LoginResponse
 * @property {string} access_token - JWT токен доступа
 */

/**
 * Сервис для работы с аутентификацией
 */
class AuthService {
  /**
   * Выполняет вход пользователя в систему
   */
  async login(credentials) {
    try {
      const response = await $api.post("/auth/login", credentials)
      store.dispatch(loginUser({ token: response.data.access_token }))
      return response.data
    } catch (error) {
      console.error("Login error:", error)
      throw error.response?.data || { message: "Login failed" }
    }
  }

  /**
   * Регистрирует нового пользователя
   */
  async registration(credentials) {
    try {
      const response = await $api.post("/auth/registration", {
        login: credentials.login,
        email: credentials.email,
        password1: credentials.password,
        password2: credentials.repeatPassword,
      })
      return response.data
    } catch (error) {
      console.error("Registration error:", error)
      throw error.response?.data || { message: "Registration failed" }
    }
  }

  /**
   * Проверяет код подтверждения при регистрации
   */
  async checkCode(code) {
    try {
      const response = await $api.post("/auth/check_code", { code })
      return response.data
    } catch (error) {
      console.error("Code verification error:", error)
      throw error.response?.data || { message: "Code verification failed" }
    }
  }

  /**
   * Выполняет выход пользователя из системы
   */
  async logout() {
    try {
      await $api.get("/auth/logout")
      store.dispatch(logoutUser())
    } catch (error) {
      console.error("Logout error:", error)
      throw error.response?.data || { message: "Logout failed" }
    }
  }
}

export const authService = new AuthService()
