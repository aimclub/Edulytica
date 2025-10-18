import { createSlice } from "@reduxjs/toolkit"
import $api from "../api/axios.api"

/**
 * @typedef {Object} AuthState
 * @property {User|null} currentUser - Текущий авторизованный пользователь или null
 * @property {boolean} isAuth - Флаг авторизации
 * @property {string|null} token - Токен авторизации
 */

// Получаем начальное состояние из localStorage или используем дефолтное
const getInitialState = () => {
  const savedState = localStorage.getItem("authState")
  if (savedState) {
    try {
      return JSON.parse(savedState)
    } catch (e) {
      console.error("Failed to parse saved auth state:", e)
    }
  }
  return {
    currentUser: null,
    isAuth: false,
    token: null,
  }
}

const authSlice = createSlice({
  name: "auth",
  initialState: getInitialState(),
  reducers: {
    loginUser: (state, action) => {
      state.currentUser = action.payload.user || state.currentUser
      state.isAuth = true
      state.token = action.payload.token
      // Сохраняем состояние в localStorage
      localStorage.setItem("authState", JSON.stringify(state))
    },
    logoutUser: (state) => {
      // Очищаем состояние
      state.currentUser = null
      state.isAuth = false
      state.token = null

      // Очищаем localStorage
      try {
        localStorage.removeItem("authState")
      } catch (error) {
        console.error("Error clearing localStorage:", error)
      }
    },
    updateToken: (state, action) => {
      state.token = action.payload
      // Обновляем состояние в localStorage
      localStorage.setItem("authState", JSON.stringify(state))
    },
    setUserData: (state, action) => {
      state.currentUser = action.payload
      // Обновляем состояние в localStorage
      localStorage.setItem("authState", JSON.stringify(state))
    },
  },
})

// Thunk для получения данных пользователя
export const fetchUserData = () => async (dispatch, getState) => {
  try {
    console.log("Fetching user data...")
    const response = await $api.get("/account")
    console.log("User data received:", response.data)
    dispatch(setUserData(response.data))
    return response.data
  } catch (error) {
    console.error("Error fetching user data:", error)
    throw error
  }
}

export const { loginUser, logoutUser, updateToken, setUserData } =
  authSlice.actions
export default authSlice.reducer
