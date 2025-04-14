import { configureStore } from "@reduxjs/toolkit"
import authReducer from "./authSlice"

const store = configureStore({
  reducer: {
    /**
     * Редюсер для управления авторизацией и пользователями
     */
    auth: authReducer,
  },
})

export default store
