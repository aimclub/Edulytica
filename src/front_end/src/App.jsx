import React, { useState } from "react"
import AppRoutes from "./routes/AppRoutes.jsx"
import { BrowserRouter } from "react-router-dom"

const App = () => {
  /**
   * Указывает, авторизован ли пользователь
   * @type {[boolean, React.Dispatch<React.SetStateAction<boolean>>]}
   */
  const [authorized, setAuthorized] = useState(false)

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
        authorized={authorized}
        setAuthorized={setAuthorized}
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
