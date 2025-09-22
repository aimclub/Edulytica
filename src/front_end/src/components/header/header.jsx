import { useState } from "react"
import logo from "../../assets/images/logo.png"
import "./header.scss"
import { Link } from "react-router-dom"

/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.isAuth - Флаг, указывающий, авторизован ли пользователь
 * @param {function} props.setAccountModal - Функция для открытия/закрытия левого модального окна c историей документов.
 * @param {function} props.setProfileModal - Функция для открытия/закрытия модального окна профиля.
 * @returns {JSX.Element} верхний блок страницы, изменяющийся при авторизации
 */
const Header = ({ isAuth, setAccountModal, setProfileModal }) => {
  // Хранит состояние открытия/закрытия левого модального окна c историей документов
  const [openModalInformation, setOpenModalInformation] = useState(true)

  //Скрытие/открытие левого модального окна c историей документов
  const handleClickLogo = () => {
    setOpenModalInformation((pr) => !pr)
    setAccountModal((pr) => !pr)
  }

  //Скрытие/открытие модального окна c информацией о профиле
  const handleSvgAccount = () => {
    setProfileModal((pr) => !pr)
  }

  return (
    <div className="header">
      {!isAuth ? (
        <>
          <div className="logoHeader">
            <img src={logo} alt="logo" className="logoHeaderImg" />
          </div>
          <div className="btnContainerHeader" style={{ marginTop: "18px" }}>
            <Link to="/login" style={{ textDecoration: "none" }}>
              <div className="loginButtonHeader">Войти</div>
            </Link>
            <Link to="/registration" style={{ textDecoration: "none" }}>
              <div className="registrationButtonHeader">Зарегистрироваться</div>
            </Link>
          </div>
        </>
      ) : (
        <>
          <div className="logoAuthorized" onClick={handleClickLogo}>
            <img src={logo} alt="logo" className="logoHeaderImg" />
            {!openModalInformation ? (
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M8.47 11.49L12 15.01L15.53 11.49M22 12.75C22 18.2728 17.5228 22.75 12 22.75C6.47715 22.75 2 18.2728 2 12.75C2 7.22715 6.47715 2.75 12 2.75C17.5228 2.75 22 7.22715 22 12.75Z"
                  stroke="white"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : (
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M16.5269 14.0029L13.0083 10.4715L9.46697 13.9801M3.00106 12.6993C3.01885 7.17648 7.5104 2.71378 13.0332 2.73157C18.556 2.74935 23.0187 7.2409 23.001 12.7637C22.9832 18.2865 18.4916 22.7493 12.9688 22.7315C7.44598 22.7137 2.98327 18.2221 3.00106 12.6993Z"
                  stroke="white"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>
          <div
            className="svgAccount"
            style={{ marginTop: "18px" }}
            onClick={handleSvgAccount}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M19 21V19C19 17.9391 18.5786 16.9217 17.8284 16.1716C17.0783 15.4214 16.0609 15 15 15H9C7.93913 15 6.92172 15.4214 6.17157 16.1716C5.42143 16.9217 5 17.9391 5 19V21"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z"
                stroke="black"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </>
      )}
    </div>
  )
}

export default Header
