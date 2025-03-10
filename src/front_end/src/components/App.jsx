import React from "react"
import { Route, Routes } from "react-router-dom"
import { Home } from "../pages/home/home"
import { Registration } from "../pages/registration/registration.jsx"
import { useState } from "react"
import { Account } from "../pages/account/account.jsx"
const App = () => {
  const [authorized, setAuthorized] = useState(false)
  const [accountModal, setAccountModal] = useState(true)
  const [profileModal, setProfileModal] = useState(false)
  return (
    <>
      <Routes>
        <Route
          path="/"
          element={
            <Home authorized={authorized} setAuthorized={setAuthorized} />
          }
        />
        <Route
          path="/account"
          element={
            <Account
              accountModal={accountModal}
              setAccountModal={setAccountModal}
              profileModal={profileModal}
              setProfileModal={setProfileModal}
              setAuthorized={setAuthorized}
            />
          }
        />
        <Route
          path="/registration"
          element={
            <Registration
              registrationPage="registration"
              authorized={authorized}
              setAuthorized={setAuthorized}
            />
          }
        />
        <Route
          path="/login"
          element={
            <Registration
              registrationPage="login"
              authorized={authorized}
              setAuthorized={setAuthorized}
            />
          }
        />
      </Routes>
    </>
  )
}
export default App
