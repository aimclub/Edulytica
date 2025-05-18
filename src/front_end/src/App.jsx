import React, { useEffect, useState } from "react"
import { BrowserRouter } from "react-router-dom"
import { useSelector } from "react-redux"

import AppRoutes from "./routes/AppRoutes"
import { validateToken } from "./utils/validateToken"

function App() {
  const isAuth = useSelector((state) => state.auth.isAuth)
  const [accountModal, setAccountModal] = useState(false)
  const [profileModal, setProfileModal] = useState(false)
  const [accountSection, setAccountSection] = useState("main")

  useEffect(() => {
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
