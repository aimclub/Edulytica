import { createSlice } from "@reduxjs/toolkit"

/**
 * @typedef {Object} AuthState
 * @property {User[]} users - Массив зарегистрированных пользователей
 * @property {User|null} currentUser - Текущий авторизованный пользователь или null
 */

/** @type {AuthState} */
const initialState = {
  users: [
    {
      login: "fedorova",
      email: "maryfedorova2309@mail.ru",
      password: "Masha2309",
    },
    {
      login: "fedorova_m",
      email: "maryfedorova2309@gmail.com",
      password: "Masha2309",
    },
  ],
  currentUser: null,
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    registerUser: (state, action) => {
      /**
       * Регистрирует нового пользователя и добавляет его в список пользователей.
       * @param {AuthState} state - Текущее состояние auth-среза
       * @param {{ payload: User }} action - Действие с данными пользователя
       */
      state.users.push({
        login: action.payload.login,
        email: action.payload.email,
        password: action.payload.password,
      })
    },
    loginUser: (state, action) => {
      state.currentUser = action.payload
    },
  },
})

export const { registerUser, loginUser } = authSlice.actions
export default authSlice.reducer
