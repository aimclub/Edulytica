import { Link } from "react-router-dom"
import "./profileModal.scss"
/**
 * @param {object} props - Объект с пропсами компонента.
 * @param {string} props.name - Имя пользователя.
 * @param {string} props.surname - Фамилия пользователя.
 * @param {string} props.nick - Никнейм пользователя.
 * @param {string} props.birthday - Дата рождения пользователя.
 * @param {function} props.setAuthorized - Функция для установки статуса авторизации пользователя.
 * @returns {JSX.Element} Модальное окно профиля.
 */

export const ProfileModal = ({
  name,
  surname,
  nick,
  birthday,
  setAuthorized,
  setProfileModal,
  setEditingProfileModal,
}) => {
  const handleLogOut = () => {
    setAuthorized((pr) => !pr)
    setProfileModal(false)
  }
  const openEditingProfileModal = () => {
    setEditingProfileModal(true)
    setProfileModal(false)
  }
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
        <div className="infProfileModal">Имя: {name}</div>
        <div className="infProfileModal">Фамилия: {surname}</div>
        <div className="infProfileModal">Имя пользователя: {nick}</div>
        <div className="infProfileModal">Дата рождения: {birthday}</div>
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
