import React, { useEffect, useState } from "react"
import { BrowserRouter } from "react-router-dom"
import { useSelector } from "react-redux"

import AppRoutes from "./routes/AppRoutes"
import { validateToken } from "./utils/validateToken"

function App() {
  const isAuth = useSelector((state) => state.auth.isAuth)

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
  }, [])

  useEffect(() => {}, [isAuth])

  return (
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
  )
}

export default App
