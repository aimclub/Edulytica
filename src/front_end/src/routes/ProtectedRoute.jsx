import { useSelector } from "react-redux"
import { Navigate, useLocation } from "react-router-dom"

/**
 * Компонент для защиты маршрутов, требующих авторизации.
 * Если пользователь не авторизован, перенаправляет на главную страницу.
 */
export const ProtectedRoute = ({ children }) => {
  const isAuth = useSelector((state) => state.auth.isAuth)
  const location = useLocation()

  if (!isAuth) {
    return <Navigate to="/" replace state={{ from: location }} />
  }

  return children
}
