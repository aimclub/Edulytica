import React from "react"
import { Route, Routes, Navigate } from "react-router-dom"
import { Home } from "../pages/home/home.jsx"
import { Registration } from "../pages/registration/registration.jsx"
import { Account } from "../pages/account/account.jsx"
import { ProtectedRoute } from "./ProtectedRoute"

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
      <Route
        path="/"
        element={
          isAuth ? <Navigate to="/account" replace /> : <Home isAuth={isAuth} />
        }
      />
      {/* Защищенные маршруты аккаунта */}
      <Route
        path="/account"
        element={
          <ProtectedRoute>
            <Account
              accountModal={accountModal}
              setAccountModal={setAccountModal}
              profileModal={profileModal}
              setProfileModal={setProfileModal}
              accountSection={accountSection}
              setAccountSection={setAccountSection}
              isAuth={isAuth}
            />
          </ProtectedRoute>
        }
      />
      <Route
        path="/account/help"
        element={
          <ProtectedRoute>
            <Account
              accountModal={accountModal}
              setAccountModal={setAccountModal}
              profileModal={profileModal}
              setProfileModal={setProfileModal}
              accountSection={accountSection}
              setAccountSection={setAccountSection}
              isAuth={isAuth}
            />
          </ProtectedRoute>
        }
      />

      <Route
        path="/account/info"
        element={
          <ProtectedRoute>
            <Account
              accountModal={accountModal}
              setAccountModal={setAccountModal}
              profileModal={profileModal}
              setProfileModal={setProfileModal}
              accountSection={accountSection}
              setAccountSection={setAccountSection}
              isAuth={isAuth}
            />
          </ProtectedRoute>
        }
      />
      <Route
        path="/account/result"
        element={
          <ProtectedRoute>
            <Account
              accountModal={accountModal}
              setAccountModal={setAccountModal}
              profileModal={profileModal}
              setProfileModal={setProfileModal}
              accountSection={accountSection}
              setAccountSection={setAccountSection}
              isAuth={isAuth}
            />
          </ProtectedRoute>
        }
      />
      {/* Публичные маршруты с редиректом для авторизованных */}
      <Route
        path="/registration"
        element={
          isAuth ? (
            <Navigate to="/account" replace />
          ) : (
            <Registration registrationPage="registration" isAuth={isAuth} />
          )
        }
      />
      <Route
        path="/login"
        element={
          isAuth ? (
            <Navigate to="/account" replace />
          ) : (
            <Registration registrationPage="login" isAuth={isAuth} />
          )
        }
      />
      {/* Редирект для несуществующих маршрутов */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default AppRoutes
