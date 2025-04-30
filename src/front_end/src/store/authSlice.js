import { createSlice } from "@reduxjs/toolkit"

/**
 * @typedef {Object} AuthState
 * @property {User|null} user - Текущий авторизованный пользователь или null
 * @property {boolean} isAuth - Флаг авторизации
 */

/** @type {AuthState} */
const initialState = {
  user: null,
  isAuth: false,
}

const authSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    loginUser: (state, action) => {
      state.user = action.payload
      state.isAuth = true
    },
    logoutUser: (state) => {
      state.isAuth = false
      state.user = null
    },
  },
})

export const { loginUser, logoutUser } = authSlice.actions
export default authSlice.reducer
