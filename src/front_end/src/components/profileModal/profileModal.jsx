import { Link } from "react-router-dom"
import "./profileModal.scss"
export const ProfileModal = ({
  name,
  surname,
  nick,
  birthday,
  setAuthorized,
}) => {
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
          onClick={() => setAuthorized((pr) => !pr)}
        >
          Выйти из аккаунта
        </div>
      </Link>
    </div>
  )
}
