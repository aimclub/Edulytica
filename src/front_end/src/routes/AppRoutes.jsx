import React from "react"
import { Route, Routes } from "react-router-dom"
import { Home } from "../pages/home/home.jsx"
import { Registration } from "../pages/registration/registration.jsx"
import { Account } from "../pages/account/account.jsx"
/**
 * Компонент, определяющий маршруты приложения.
 * @param {boolean} props.authorized - Определяет, авторизован ли пользователь
 * @param {React.Dispatch<React.SetStateAction<boolean>>} props.setAuthorized - Функция для установки состояния авторизации
 * @param {boolean} props.accountModal - Определяет, отображать ли модальное окно аккаунта, которое с историей файлов
 * @param {React.Dispatch<React.SetStateAction<boolean>>} props.setAccountModal - Функция для установки состояния видимости модального окна аккаунта
 * @param {boolean} props.profileModal - Определяет, отображать ли модальное окно профиля
 * @param {React.Dispatch<React.SetStateAction<boolean>>} props.setProfileModal - Функция для установки состояния видимости модального окна профиля
 * @returns {JSX.Element} JSX-элемент, определяющий структуру маршрутов
 */

const AppRoutes = ({
  authorized,
  setAuthorized,
  accountModal,
  setAccountModal,
  profileModal,
  setProfileModal,
  accountSection,
  setAccountSection,
}) => {
  return (
    <Routes>
      <Route
        path="/"
        element={<Home authorized={authorized} setAuthorized={setAuthorized} />}
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
            accountSection={accountSection}
            setAccountSection={setAccountSection}
          />
        }
      />
      <Route
        path="/account/help"
        element={
          <Account
            accountModal={accountModal}
            setAccountModal={setAccountModal}
            profileModal={profileModal}
            setProfileModal={setProfileModal}
            setAuthorized={setAuthorized}
            accountSection={accountSection}
            setAccountSection={setAccountSection}
          />
        }
      />
      <Route
        path="/account/info"
        element={
          <Account
            accountModal={accountModal}
            setAccountModal={setAccountModal}
            profileModal={profileModal}
            setProfileModal={setProfileModal}
            setAuthorized={setAuthorized}
            accountSection={accountSection}
            setAccountSection={setAccountSection}
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
  )
}

export default AppRoutes
