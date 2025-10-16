import { configureStore } from "@reduxjs/toolkit"
import authReducer from "./authSlice"
import ticketReducer from "./ticketSlice"

const store = configureStore({
  reducer: {
    /**
     * Редюсер для управления авторизацией и пользователями
     */
    auth: authReducer,
    /**
     * Редюсер для управления тикетами
     */
    ticket: ticketReducer,
  },
})

export default store
