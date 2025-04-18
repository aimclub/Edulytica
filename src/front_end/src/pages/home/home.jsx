import { useEffect } from "react"
import Header from "../../components/header/header"
import "./home.scss"
import { motion } from "framer-motion"
/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.authorized - Флаг, указывающий, авторизован ли пользователь
 * @param {function} props.setAuthorized - Функция для установки значения авторизации пользователя
 * @returns {JSX.Element} Главная страница в неавторизированном состоянии
 */

export const Home = ({ authorized, setAuthorized }) => {
  useEffect(() => {}, [authorized])
  return (
    <div className="homePage">
      <Header authorized={authorized} setAuthorized={setAuthorized} />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="blockHome">Edulytica</div>{" "}
      </motion.div>
    </div>
  )
}
