import axios from "axios"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

/**
 * @typedef {Object} User
 * @property {string} id - Уникальный идентификатор пользователя
 * @property {string} email - Email пользователя
 * @property {string} login - Логин пользователя
 * @property {string} name - Имя пользователя
 * @property {string} surname - Фамилия пользователя
 * @property {string} birthday - Дата рождения пользователя
 * @property {string} token - JWT токен пользователя
 */

/**
 * @typedef {Object} LoginCredentials
 * @property {string} login - Логин пользователя
 * @property {string} password - Пароль пользователя
 */

/**
 * @typedef {Object} RegisterCredentials
 * @property {string} email - Email пользователя
 * @property {string} login - Логин пользователя
 * @property {string} password - Пароль пользователя
 * @property {string} repeatPassword - Повторный ввод пароля
 */

/**
 * @typedef {Object} LoginResponse
 * @property {User} user - Данные пользователя
 */

/**
 * @typedef {Object} ErrorResponse
 * @property {string} message - Сообщение об ошибке
 */

/**
 * Сервис для работы с аутентификацией
 */
class AuthService {
  /**
   * Выполняет вход пользователя
   * @param {LoginCredentials} credentials - Данные для входа
   * @returns {Promise<LoginResponse>} Данные пользователя и токен
   * @throws {ErrorResponse} Ошибка входа
   */
  async login(credentials) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, credentials)
      if (response.data.token) {
        localStorage.setItem("token", response.data.token)
      }
      return response.data
    } catch (error) {
      throw error.response?.data || { message: "Login failed" }
    }
  }

  /**
   * Выполняет регистрацию нового пользователя
   * @param {RegisterCredentials} credentials - Данные для регистрации
   * @returns {Promise<LoginResponse>} Данные пользователя и токен
   * @throws {ErrorResponse} Ошибка регистрации
   */
  async registration(login, email, password, repeatPassword) {
    try {
      const response = await axios.post(`${API_URL}/auth/registration`, {
        login,
        email,
        password1: password,
        password2: repeatPassword,
      })
      if (response.data.token) {
        localStorage.setItem("token", response.data.token)
      }
      return response.data
    } catch (error) {
      throw error.response?.data || { message: "Registration failed" }
    }
  }

  /**
   * Проверяет код подтверждения
   * @param {string} code - Код подтверждения
   * @returns {Promise<{valid: boolean}>} Результат проверки кода
   * @throws {ErrorResponse} Ошибка проверки кода
   */
  async checkCode(code) {
    try {
      const response = await axios.post(`${API_URL}/auth/check_code`, {
        code,
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { message: "Code verification failed" }
    }
  }
}

export const authService = new AuthService()
