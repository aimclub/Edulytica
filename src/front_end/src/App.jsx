import React, { useState, useEffect } from "react"
import AppRoutes from "./routes/AppRoutes.jsx"
import { BrowserRouter } from "react-router-dom"
import { useSelector } from "react-redux"
import { validateToken } from "./api/axios.api"

const App = () => {
  const { isAuth } = useSelector((state) => state.auth)

  useEffect(() => {
    // Проверяем токен при загрузке приложения
    validateToken()
  }, [])

  /**
   * Контролирует видимость модального левого окна с историей файлов
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [accountModal, setAccountModal] = useState(true)
  const [accountSection, setAccountSection] = useState("main")
  /**
   * Контролирует видимость модального окна профиля
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [profileModal, setProfileModal] = useState(false)

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
