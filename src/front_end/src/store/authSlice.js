import { createSlice } from "@reduxjs/toolkit"

/**
 * @typedef {Object} AuthState
 * @property {User|null} currentUser - Текущий авторизованный пользователь или null
 * @property {boolean} isAuth - Флаг авторизации
 * @property {string|null} token - Токен авторизации
 */

/** @type {AuthState} */
const initialState = {
  currentUser: null,
  isAuth: false,
  token: null,
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginUser: (state, action) => {
      state.currentUser = action.payload
      state.isAuth = true
      state.token = action.payload.token
    },
    logoutUser: (state) => {
      state.currentUser = null
      state.isAuth = false
      state.token = null
    },
  },
})

export const { loginUser, logoutUser } = authSlice.actions
export default authSlice.reducer
