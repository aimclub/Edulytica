import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import Header from "../../components/header/header"
import "./home.scss"
import { motion } from "framer-motion"
import { FeedbackFab } from "../../components/feedback/feedbackFab"
import macbook from "../../assets/images/macbook.png"
/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.isAuth - Флаг, указывающий, авторизован ли пользователь
 * @returns {JSX.Element} Главная страница в неавторизированном состоянии
 */

export const Home = ({ isAuth }) => {
  const navigate = useNavigate()

  useEffect(() => {}, [isAuth])

  const handleTryNowClick = () => {
    navigate("/registration")
  }

  return (
    <div className="homePage">
      <Header isAuth={isAuth} />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="heroSection"
      >
        <div className="heroContent">
          <motion.h1
            className="heroTitle"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Система для автоматизации проверки и оценки текстовых результатов
            деятельности обучающихся
          </motion.h1>

          <motion.div
            className="heroSubtitle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            на основе больших языковых моделей
          </motion.div>

          <motion.p
            className="heroDescription"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            Автоматизируйте процесс рецензирования дипломов, курсовых работ и
            статей.
          </motion.p>

          <motion.button
            className="ctaButton"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleTryNowClick}
            type="button"
          >
            Попробовать
          </motion.button>
        </div>

        <div className="macbookContainer">
          <img src={macbook} alt="MacBook" className="macbookImage" />
        </div>
      </motion.div>

      <FeedbackFab />
    </div>
  )
}
