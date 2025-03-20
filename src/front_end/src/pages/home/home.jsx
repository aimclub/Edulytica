import Header from "../../components/header/header"
import "./home.scss"
/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.authorized - Флаг, указывающий, авторизован ли пользователь
 * @param {function} props.setAuthorized - Функция для установки значения авторизации пользователя
 * @returns {JSX.Element} Главная страница в неавторизированном состоянии
 */

export const Home = ({ authorized, setAuthorized }) => {
  return (
    <div className="homePage">
      <Header authorized={authorized} setAuthorized={setAuthorized} />
      <div className="blockHome">Edulytica</div>
    </div>
  )
}
