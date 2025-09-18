import { useEffect } from "react"
import Header from "../../components/header/header"
import "./home.scss"
import { motion } from "framer-motion"
import { FeedbackFab } from "../../components/feedback/feedbackFab"
/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.isAuth - Флаг, указывающий, авторизован ли пользователь
 * @returns {JSX.Element} Главная страница в неавторизированном состоянии
 */

export const Home = ({ isAuth }) => {
  useEffect(() => {}, [isAuth])
  return (
    <div className="homePage">
      <Header isAuth={isAuth} />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="blockHome">Edulytica</div>{" "}
      </motion.div>
      <FeedbackFab />
    </div>
  )
}
