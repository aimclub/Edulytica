import React, { useEffect, useState } from "react"
import { BrowserRouter } from "react-router-dom"
import { useSelector, useDispatch } from "react-redux"
import AppRoutes from "./routes/AppRoutes"
import { validateToken } from "./utils/validateToken"
import { useErrorHandler } from "./hooks/useErrorHandler"
import { NotificationModal } from "./components/notificationModal/notificationModal"
import { setError } from "./store/ticketSlice"

function App() {
  const dispatch = useDispatch()
  const isAuth = useSelector((state) => state.auth.isAuth)
  const ticketError = useSelector((state) => state.ticket.error)
  const { error, showNotification, handleError, clearError } = useErrorHandler()

  /**
   * Контролирует видимость модального левого окна с историей файлов
   */
  const [accountModal, setAccountModal] = useState(true)
  const [accountSection, setAccountSection] = useState("main")

  /**
   * Контролирует видимость модального окна профиля
   */
  const [profileModal, setProfileModal] = useState(false)

  useEffect(() => {
    // Проверяем токен при загрузке приложения
    validateToken()

    // Слушатель ошибок API из axios interceptor
    const handleApiError = (e) => {
      try {
        const msg = e?.detail?.message || "Что-то пошло не так"
        handleError(new Error(msg))
      } catch (_) {}
    }

    window.addEventListener("api:error", handleApiError)

    return () => {
      window.removeEventListener("api:error", handleApiError)
    }
  }, [handleError])

  useEffect(() => {}, [isAuth])

  // Обработка ошибок из Redux store
  useEffect(() => {
    if (ticketError) {
      console.log("Redux ticket error:", ticketError)
      handleError(new Error(ticketError))
      // Очищаем ошибку в store после показа модального окна
      setTimeout(() => {
        dispatch(setError(null))
      }, 100)
    }
  }, [ticketError, handleError, dispatch])

  return (
    <>
      <BrowserRouter>
        <AppRoutes
          isAuth={isAuth}
          accountModal={accountModal}
          setAccountModal={setAccountModal}
          profileModal={profileModal}
          setProfileModal={setProfileModal}
          accountSection={accountSection}
          setAccountSection={setAccountSection}
        />
      </BrowserRouter>
      <NotificationModal
        visible={showNotification}
        text={
          error
            ? `Что-то пошло не так: ${error.message || "Unknown error"}`
            : "Что-то пошло не так"
        }
        eta=""
        onClose={clearError}
        centered
      />
    </>
  )
}

export default App
