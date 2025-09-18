import { Link } from "react-router-dom"
import "./profileModal.scss"
import { useEffect } from "react"
import { authService } from "../../services/auth.service"

/**
 * @param {object} props - Объект с пропсами компонента.
 * @param {function} props.setProfileModal - Функция для закрытия модального окна профиля.
 * @param {function} props.setEditingProfileModal - Функция для открытия модального окна редактирования профиля.
 * @param {object} props.infoProfile - Информация о профиле пользователя.
 * @returns {JSX.Element} Модальное окно профиля.
 */

export const ProfileModal = ({
  setProfileModal,
  setEditingProfileModal,
  infoProfile,
}) => {
  //Выход из аккаунта
  const logoutHandler = async () => {
    try {
      await authService.logout()
      setProfileModal(false)
    } catch (error) {
      console.error("Logout failed:", error)
    }
  }

  //Открытие модального окна редактирования профиля
  const openEditingProfileModal = () => {
    setEditingProfileModal(true)
    setProfileModal(false)
  }

  useEffect(() => {}, [infoProfile])

  return (
    <div className="profileModal">
      <div className="titleProfileModal">Мой аккаунт</div>
      <div className="containerProfileModal">
        <div className="infoSectionProfileModal">
          <div className="infoItemProfileModal">
            <span className="infoLabelProfileModal">Имя:</span>
            <span className="infoValueProfileModal">{infoProfile.name}</span>
          </div>
          <div className="infoItemProfileModal">
            <span className="infoLabelProfileModal">Фамилия:</span>
            <span className="infoValueProfileModal">{infoProfile.surname}</span>
          </div>
          <div className="infoItemProfileModal">
            <span className="infoLabelProfileModal">Имя пользователя:</span>
            <span className="infoValueProfileModal">{infoProfile.login}</span>
          </div>
          <div className="infoItemProfileModal">
            <span className="infoLabelProfileModal">Дата рождения:</span>
            <span className="infoValueProfileModal">
              {infoProfile.birthDate || "23.09.2006"}
            </span>
          </div>
        </div>
        <div className="actionsSectionProfileModal">
          <div
            className="actionItemProfileModal"
            onClick={openEditingProfileModal}
          >
            <span>Редактировать профиль</span>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M9 18L15 12L9 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <Link to="/" style={{ textDecoration: "none" }}>
            <div
              className="actionItemProfileModal logoutActionProfileModal"
              onClick={logoutHandler}
            >
              Выйти из аккаунта
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
