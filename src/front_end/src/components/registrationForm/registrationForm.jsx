import { useState, useEffect } from "react"
import { Input } from "../../utils/input/input"
import "./registrationForm.scss"
import { Link } from "react-router-dom"
export const RegistrationForm = ({
  registrationPage,
  authorized,
  setAuthorized,
}) => {
  const [switchClick, setSwitchClick] = useState(false)
  const [loginModal, setLoginModal] = useState(registrationPage)
  const handleSwitch = () => {
    setSwitchClick((prev) => !prev)
  }
  const handleClickModal = (clickModal) => {
    setLoginModal(clickModal)
  }
  const handleBtnRegistrationForm = () => {
    setAuthorized((pr) => !pr)
  }
  useEffect(() => {
    setLoginModal(registrationPage)
  }, [registrationPage])

  return (
    <div className="registrationForm">
      {loginModal === "login" ? (
        <>
          <div className="titleRegistrationForm">Вход</div>
          <div className="containerRegistrationForm">
            <div className="inputContainerRegistrationForm">
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">Почта \ Логин</div>
                <Input type="text" placeholder="Введите почту или логин..." />
              </div>
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">Пароль</div>
                <Input type="password" placeholder="Введите пароль..." />
              </div>
            </div>
            <div className="switchContRegistrationForm">
              {!switchClick ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="44"
                  height="25"
                  viewBox="0 0 44 25"
                  fill="none"
                  onClick={handleSwitch}
                >
                  <rect y="0.5" width="44" height="24" rx="12" fill="#B4B4B4" />
                  <circle cx="12" cy="12.5" r="10" fill="#303030" />
                </svg>
              ) : (
                <svg
                  width="44"
                  height="25"
                  viewBox="0 0 44 25"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  onClick={handleSwitch}
                >
                  <rect y="0.5" width="44" height="24" rx="12" fill="#2B63F6" />
                  <circle cx="32" cy="12.5" r="10" fill="white" />
                </svg>
              )}

              <div className="textSwitchContRegistrationForm">
                Запомнить меня
              </div>
            </div>
            <div className="blockBtnRegistrationForm">
              <Link style={{ width: "100%" }} to="/account">
                {" "}
                <button
                  className="btnRegistrationForm"
                  onClick={handleBtnRegistrationForm}
                >
                  Войти в аккаунт
                </button>
              </Link>
              <div
                className="textBtnRegistrationForm"
                onClick={() => {
                  handleClickModal("registration")
                }}
              >
                Cоздать аккаунт?
              </div>
            </div>
          </div>
        </>
      ) : loginModal === "registration" ? (
        <>
          <div className="titleRegistrationForm">Регистрация</div>
          <div className="containerRegistrationForm">
            <div className="inputContainerRegistrationForm">
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">Почта</div>
                <Input type="text" placeholder="Введите почту..." />
              </div>
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">Логин</div>
                <Input type="text" placeholder="Введите логин..." />
              </div>
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">Пароль</div>
                <Input type="password" placeholder="Введите пароль..." />
              </div>
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">
                  Повторный пароль
                </div>
                <Input
                  type="password"
                  placeholder="Введите повторно пароль..."
                />
              </div>
            </div>
            <div className="blockBtnRegistrationForm">
              <button
                className="btnRegistrationForm"
                onClick={() => {
                  handleClickModal("registration2")
                }}
              >
                Создать аккаунт
              </button>

              <div
                className="textBtnRegistrationForm"
                onClick={() => {
                  handleClickModal("login")
                }}
              >
                Уже есть аккаунт?
              </div>
            </div>
          </div>
        </>
      ) : loginModal === "registration2" ? (
        <>
          <div className="titleRegistrationForm">Регистрация</div>
          <div className="containerRegistrationForm">
            <div className="inputContainerRegistrationForm">
              <div className="messageContRegistrationForm">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="19"
                  viewBox="0 0 15 19"
                  fill="none"
                >
                  <path
                    d="M2.313 10.9464L3.16971 11.4623L3.17195 11.4585L2.313 10.9464ZM1.40259 12.4585L0.545888 11.9427L0.545737 11.943L1.40259 12.4585ZM2.25759 14.7781L1.93699 15.7253L1.9407 15.7266L2.25759 14.7781ZM12.763 14.7781L12.4491 13.8286L12.4461 13.8296L12.763 14.7781ZM13.618 12.4585L14.4755 11.944L14.4747 11.9427L13.618 12.4585ZM12.7076 10.9464L11.8414 11.4462L11.8461 11.4542L11.8509 11.4622L12.7076 10.9464ZM8.97884 2.50727L8.70003 3.46761C9.06595 3.57385 9.46045 3.4629 9.71736 3.1815C9.97426 2.9001 10.0489 2.49716 9.9099 2.14239L8.97884 2.50727ZM8.21884 2.34893L8.0948 3.34122L8.09851 3.34167L8.21884 2.34893ZM6.04967 2.50727L5.11861 2.14239C4.97956 2.49721 5.05427 2.90023 5.31127 3.18163C5.56827 3.46303 5.96287 3.5739 6.32881 3.46752L6.04967 2.50727ZM7.51426 1.27768C4.34155 1.27768 1.76425 3.85498 1.76425 7.02768H3.76425C3.76425 4.95955 5.44612 3.27768 7.51426 3.27768V1.27768ZM1.76425 7.02768V9.3156H3.76425V7.02768H1.76425ZM1.76425 9.3156C1.76425 9.43657 1.7347 9.64673 1.6671 9.89026C1.59958 10.1335 1.51638 10.3298 1.45406 10.4344L3.17195 11.4585C3.35505 11.1514 3.49747 10.7738 3.59423 10.4252C3.6909 10.077 3.76425 9.67754 3.76425 9.3156H1.76425ZM1.4563 10.4306L0.545888 11.9427L2.25929 12.9743L3.16971 11.4622L1.4563 10.4306ZM0.545737 11.943C0.123312 12.645 0.0248347 13.454 0.295594 14.1852C0.565917 14.9153 1.16586 15.4643 1.93699 15.7253L2.57818 13.8309C2.32015 13.7435 2.21155 13.5999 2.17115 13.4908C2.13118 13.3828 2.11978 13.2062 2.25944 12.9741L0.545737 11.943ZM1.9407 15.7266C5.55845 16.9353 9.46214 16.9353 13.0799 15.7266L12.4461 13.8296C9.2397 14.9009 5.78089 14.9009 2.57448 13.8296L1.9407 15.7266ZM13.0769 15.7276C14.6469 15.2086 15.3257 13.361 14.4755 11.944L12.7605 12.973C12.9553 13.2977 12.795 13.7143 12.4491 13.8286L13.0769 15.7276ZM14.4747 11.9427L13.5643 10.4306L11.8509 11.4622L12.7613 12.9743L14.4747 11.9427ZM13.5738 10.4467C13.5112 10.3382 13.4283 10.1378 13.3613 9.89325C13.2939 9.64765 13.2643 9.43687 13.2643 9.3156H11.2643C11.2643 9.67724 11.3375 10.0761 11.4325 10.4222C11.5277 10.7695 11.6665 11.143 11.8414 11.4462L13.5738 10.4467ZM13.2643 9.3156V7.02768H11.2643V9.3156H13.2643ZM13.2643 7.02768C13.2643 3.8629 10.679 1.27768 7.51426 1.27768V3.27768C9.57447 3.27768 11.2643 4.96747 11.2643 7.02768H13.2643ZM9.25765 1.54692C8.96878 1.46305 8.66208 1.39534 8.33917 1.3562L8.09851 3.34167C8.2981 3.36586 8.49807 3.40898 8.70003 3.46761L9.25765 1.54692ZM8.34287 1.35665C7.45542 1.24572 6.58944 1.30896 5.77053 1.54702L6.32881 3.46752C6.87157 3.30974 7.46226 3.26214 8.0948 3.34121L8.34287 1.35665ZM6.98073 2.87214C7.06438 2.65868 7.27211 2.50977 7.51426 2.50977V0.509766C6.4264 0.509766 5.49413 1.18418 5.11861 2.14239L6.98073 2.87214ZM7.51426 2.50977C7.7564 2.50977 7.96413 2.65868 8.04778 2.87214L9.9099 2.14239C9.53438 1.18419 8.60211 0.509766 7.51426 0.509766V2.50977ZM8.88926 15.0631C8.88926 15.8171 8.26822 16.4381 7.51426 16.4381V18.4381C9.37279 18.4381 10.8893 16.9216 10.8893 15.0631H8.88926ZM7.51426 16.4381C7.14173 16.4381 6.79123 16.2825 6.54303 16.0343L5.12881 17.4485C5.73561 18.0553 6.58845 18.4381 7.51426 18.4381V16.4381ZM6.54303 16.0343C6.29483 15.7861 6.13926 15.4356 6.13926 15.0631H4.13926C4.13926 15.9889 4.52201 16.8417 5.12881 17.4485L6.54303 16.0343Z"
                    fill="#89AAFF"
                  />
                </svg>
                <div className="textMessageContRegistrationForm">
                  на вашу почту был отправлен код
                </div>
              </div>
              <div className="blockInputRegistrationForm">
                <div className="titleInputRegistrationForm">Введите код</div>
                <Input type="password" placeholder="" />
              </div>
            </div>
            <div className="blockBtnRegistrationForm">
              <Link style={{ width: "100%" }} to="/account">
                {" "}
                <button
                  className="btnRegistrationForm"
                  onClick={handleBtnRegistrationForm}
                >
                  Отправить
                </button>
              </Link>
              <div className="textBtnRegistrationForm">
                Отправить код повторно
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  )
}
