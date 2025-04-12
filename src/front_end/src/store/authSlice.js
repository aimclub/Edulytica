import { createSlice } from "@reduxjs/toolkit"

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
