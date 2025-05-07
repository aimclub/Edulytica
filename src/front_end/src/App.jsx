import React, { useState, useEffect } from "react"
import AppRoutes from "./routes/AppRoutes.jsx"
import { BrowserRouter } from "react-router-dom"
import { useSelector } from "react-redux"

const App = () => {
  const { isAuth } = useSelector((state) => state.auth)
  const [authorized, setAuthorized] = useState(isAuth)

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

  // Обновляем authorized при изменении isAuth
  useEffect(() => {
    setAuthorized(isAuth)
  }, [isAuth])

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
