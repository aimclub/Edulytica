import { Link } from "react-router-dom"
import "./profileModal.scss"
import { useEffect } from "react"
/**
 * @param {object} props - Объект с пропсами компонента.
 * @param {function} props.setAuthorized - Функция для установки статуса авторизации пользователя.
 * @returns {JSX.Element} Модальное окно профиля.
 */

export const ProfileModal = ({
  setAuthorized,
  setProfileModal,
  setEditingProfileModal,
  infoProfile,
}) => {
  const handleLogOut = () => {
    setAuthorized(false)
    setProfileModal(false)
  }
  const openEditingProfileModal = () => {
    setEditingProfileModal(true)
    setProfileModal(false)
  }
  useEffect(() => {}, [infoProfile])
  return (
    <div className="profileModal">
      <div
        className="infProfileModal"
        style={{
          borderBottom: "1px solid #cbd5e1",
          paddingBlock: "15px 14px",
          lineHeight: "143%",
          paddingLeft: "13px",
          fontSize: "16px",
        }}
      >
        Мой аккаунт
      </div>
      <div className="blockInfProfileModal">
        <div className="infProfileModal">Имя: {infoProfile.name}</div>
        <div className="infProfileModal">Фамилия: {infoProfile.surname}</div>
        <div className="infProfileModal">
          Имя пользователя: {infoProfile.nick}
        </div>
        <div className="infProfileModal">
          Дата рождения: {infoProfile.birthday}
        </div>
      </div>
      <div
        className="infProfileModal"
        style={{
          paddingBlock: "14px 4px",
          lineHeight: "143%",
          paddingLeft: "13px",
          cursor: "pointer",
        }}
        onClick={openEditingProfileModal}
      >
        Редактировать информацию
      </div>
      <Link to="/" style={{ textDecoration: "none" }}>
        <div
          className="infProfileModal"
          style={{
            paddingBlock: "11px 15px",
            lineHeight: "143%",
            color: "rgba(239, 68, 68, 1)",
            paddingLeft: "13px",
            cursor: "pointer",
          }}
          onClick={handleLogOut}
        >
          Выйти из аккаунта
        </div>
      </Link>
    </div>
  )
}
