import React from "react"
import { Route, Routes } from "react-router-dom"
import { Home } from "../pages/home/home.jsx"
import { Registration } from "../pages/registration/registration.jsx"
import { Account } from "../pages/account/account.jsx"

/**
 * Компонент, определяющий маршруты приложения.
 * @param {boolean} props.isAuth - Определяет, авторизован ли пользователь
 * @param {boolean} props.accountModal - Определяет, отображать ли модальное окно аккаунта, которое с историей файлов
 * @param {React.Dispatch<React.SetStateAction<boolean>>} props.setAccountModal - Функция для установки состояния видимости модального окна аккаунта
 * @param {boolean} props.profileModal - Определяет, отображать ли модальное окно профиля
 * @param {React.Dispatch<React.SetStateAction<boolean>>} props.setProfileModal - Функция для установки состояния видимости модального окна профиля
 * @returns {JSX.Element} JSX-элемент, определяющий структуру маршрутов
 */

const AppRoutes = ({
  isAuth,
  accountModal,
  setAccountModal,
  profileModal,
  setProfileModal,
  accountSection,
  setAccountSection,
}) => {
  return (
    <Routes>
      <Route path="/" element={<Home isAuth={isAuth} />} />
      <Route
        path="/account"
        element={
          <Account
            accountModal={accountModal}
            setAccountModal={setAccountModal}
            profileModal={profileModal}
            setProfileModal={setProfileModal}
            accountSection={accountSection}
            setAccountSection={setAccountSection}
            isAuth={isAuth}
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
            accountSection={accountSection}
            setAccountSection={setAccountSection}
          />
        }
      />
      <Route
        path="/account/result"
        element={
          <Account
            accountModal={accountModal}
            setAccountModal={setAccountModal}
            profileModal={profileModal}
            setProfileModal={setProfileModal}
            accountSection={accountSection}
            setAccountSection={setAccountSection}
            isAuth={isAuth}
          />
        }
      />
      <Route
        path="/registration"
        element={
          <Registration registrationPage="registration" isAuth={isAuth} />
        }
      />
      <Route
        path="/login"
        element={<Registration registrationPage="login" isAuth={isAuth} />}
      />
    </Routes>
  )
}

export default AppRoutes
