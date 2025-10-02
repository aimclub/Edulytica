import { useCallback, useEffect, useState } from "react"
import logo from "../../assets/images/logo.png"
import "./header.scss"
import { Link, useLocation } from "react-router-dom"

/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.isAuth - Флаг, указывающий, авторизован ли пользователь
 * @param {function} props.setAccountModal - Функция для открытия/закрытия левого модального окна c историей документов.
 * @param {function} props.setProfileModal - Функция для открытия/закрытия модального окна профиля.
 * @returns {JSX.Element} верхний блок страницы, изменяющийся при авторизации
 */
const Header = ({ isAuth, setAccountModal, setProfileModal }) => {
  const [openModalInformation, setOpenModalInformation] = useState(true)
  const [isInfoBlockExpanded, setIsInfoBlockExpanded] = useState(false)
  const location = useLocation()
  const [infoBlockStyle, setInfoBlockStyle] = useState({})
  const [isInfoBlockReady, setIsInfoBlockReady] = useState(false)

  const handleClickLogo = () => {
    setOpenModalInformation((pr) => !pr)
    setAccountModal((pr) => !pr)
  }

  const handleSvgAccount = () => {
    setProfileModal((pr) => !pr)
  }

  const isAccountPage = location?.pathname?.startsWith("/account")
  const toggleInfoBlock = () => setIsInfoBlockExpanded((p) => !p)

  const computeAndSetInfoBlock = useCallback(() => {
    const target =
      document.querySelector(".blockAddFile") ||
      document.querySelector(".addFileTopCont")
    const el = document.querySelector(".infoBlock")
    if (!el) return

    const rect = target ? target.getBoundingClientRect() : null
    const baseWidth = rect
      ? Math.max(rect.width - 160, 360)
      : Math.min(window.innerWidth - 40, 760)

    let leftPx = 0
    let widthPx = baseWidth
    let transformValue = "none"

    if (!openModalInformation) {
      widthPx = Math.min(baseWidth, window.innerWidth - 40)
      if (window.innerWidth < 1335) {
        if (window.innerWidth > 1000) {
          leftPx = "55%"
          transformValue = "translateX(-50%)"
        } else {
          leftPx = "58%"
          transformValue = "translateX(-50%)"
        }
      } else {
        leftPx = rect ? rect.left + (rect.width - widthPx) / 2 : 50
      }
    } else if (rect) {
      leftPx = rect.left + (rect.width - widthPx) / 2
    }

    setInfoBlockStyle({
      left: typeof leftPx === "number" ? `${leftPx}px` : leftPx,
      width: `${widthPx}px`,
      transform: transformValue,
    })
    setIsInfoBlockReady(true)
  }, [openModalInformation])

  useEffect(() => {
    if (!isAccountPage) return

    let frameId

    const handleResize = () => {
      if (frameId) cancelAnimationFrame(frameId)
      frameId = requestAnimationFrame(computeAndSetInfoBlock)
    }

    const timeout = setTimeout(computeAndSetInfoBlock, 0)
    window.addEventListener("resize", handleResize)

    return () => {
      clearTimeout(timeout)
      window.removeEventListener("resize", handleResize)
      if (frameId) cancelAnimationFrame(frameId)
    }
  }, [isAccountPage, computeAndSetInfoBlock])

  useEffect(() => {
    if (!isAccountPage) return

    const timeouts = [0, 120, 260, 500].map((t) =>
      setTimeout(() => computeAndSetInfoBlock(), t)
    )

    const target =
      document.querySelector(".blockAddFile") ||
      document.querySelector(".addFileTopCont")
    const ro = target ? new ResizeObserver(computeAndSetInfoBlock) : null
    const headerEl = document.querySelector(".header")
    const roHeader = headerEl
      ? new ResizeObserver(computeAndSetInfoBlock)
      : null
    if (ro && target) ro.observe(target)
    if (roHeader && headerEl) roHeader.observe(headerEl)

    const mo = new MutationObserver(computeAndSetInfoBlock)
    mo.observe(document.body, {
      attributes: true,
      childList: true,
      subtree: true,
    })

    const onScroll = () => computeAndSetInfoBlock()
    window.addEventListener("scroll", onScroll, { passive: true })

    return () => {
      timeouts.forEach(clearTimeout)
      if (ro) ro.disconnect()
      if (roHeader) roHeader.disconnect()
      mo.disconnect()
      window.removeEventListener("scroll", onScroll)
    }
  }, [isAccountPage, computeAndSetInfoBlock])

  useEffect(() => {
    if (!isAccountPage) return
    requestAnimationFrame(computeAndSetInfoBlock)
  }, [isAccountPage, computeAndSetInfoBlock])

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
            style={{ marginTop: "24px" }}
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

          {isAccountPage && (
            <div
              className={`infoBlock ${isInfoBlockReady ? "ready" : ""} ${
                openModalInformation ? "aligned" : ""
              } ${isInfoBlockExpanded ? "expanded" : "collapsed"}`}
              style={infoBlockStyle}
            >
              <button
                type="button"
                className="infoBlockContent"
                onClick={toggleInfoBlock}
                aria-expanded={isInfoBlockExpanded}
              >
                <div className="infoBlockText">
                  <p>
                    Обращаем ваше внимание: сервис работает с документами
                    формата PDF, размер которых не должен превышать 50 мегабайт.
                  </p>
                  <p className="infoBlockSecond">
                    При выборе мероприятия вы можете ознакомиться с
                    дополнительной информацией о каждом из них. Выбор
                    мероприятия является обязательным условием при отправке
                    запроса!
                  </p>
                  <p className="infoBlockThird">
                    В настоящее время сервис находится в разработке, поэтому
                    периодически могут возникать ошибки. В случае их появления,
                    пожалуйста, сообщите нам о них, заполнив форму в правом
                    нижнем углу и указав подробную информацию, чтобы мы могли
                    сделать наш инструмент лучше.
                  </p>
                </div>

                <svg
                  className={`infoBlockToggle ${
                    isInfoBlockExpanded ? "expanded" : ""
                  }`}
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path
                    d="M4 6L8 10L12 6"
                    stroke="#bebaba"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Header
