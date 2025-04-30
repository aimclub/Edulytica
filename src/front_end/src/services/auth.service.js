import axios from "axios"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"
//
class AuthService {
  async registration(login, email, password, repeatPassword) {
    try {
      const response = await axios.post(`${API_URL}/auth/registration`, {
        login,
        email,
        password1: password,
        password2: repeatPassword,
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { message: "Registration failed" }
    }
  }

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

  async login(login, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        login,
        password,
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { message: "Login failed" }
    }
  }
}

export const authService = new AuthService()
