import { useEffect, useState } from "react"
import Header from "../../components/header/header"
import { RegistrationForm } from "../../components/registrationForm/registrationForm"
import "./registration.scss"
import { Link } from "react-router-dom"
/**
 * @param {object} props - Объект с пропсами компонента
 * @param {string} props.registrationPage - Определяет, какую страницу отображать в форме регистрации (login или registration)
 * @param {boolean} props.authorized - Флаг, указывающий, авторизован ли пользователь
 * @param {function} props.setAuthorized - Функция для установки значения авторизации пользователя
 * @returns {JSX.Element} Страница регистрации
 */

export const Registration = ({
  registrationPage,
  authorized,
  setAuthorized,
}) => {
  useEffect(() => {}, [registrationPage])

  return (
    <div className="registrationPage">
      <div
        className=""
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "start",
          gap: "42px",
          width: "100%",
        }}
      >
        <Header authorized={authorized} setAuthorized={setAuthorized} />
        <Link to="/" style={{ textDecoration: "none" }}>
          <div
            className="blockLeftRegistrationPage"
            onClick={() => setAuthorized(false)}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M9.57 5.92969L3.5 11.9997L9.57 18.0697M20.5 11.9997H3.67"
                stroke="#B4B4B4"
                strokeWidth="2.5"
                strokeMiterlimit="10"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="textLeftRegistrationPage">Главная</div>
          </div>{" "}
        </Link>
      </div>
      <RegistrationForm
        registrationPage={registrationPage}
        authorized={authorized}
        setAuthorized={setAuthorized}
      />
    </div>
  )
}
