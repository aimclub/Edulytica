import { useEffect, useRef, useState } from "react"
import "./resultFile.scss"
import texts from "./text.js"
import { motion } from "framer-motion"
/**
 * Компонент отображает результат работы над файлом,содержимое файла и позволяет переключаться между его разделами(суммаризация, рецензирование).
 *
 * @param {Object} props - Свойства компонента.
 * @param {string} props.fileName - Имя файла, данные которого отображаются.
 */

export const ResultFile = ({ fileName }) => {
  /** Состояние активного раздела */
  const [activeSectionResult, setActiveSectionResult] = useState(1)

  /**  Состояние загрузки */
  const [loading, setLoading] = useState(true)

  /** Состояние, указывающее, есть ли прокрутка */
  const [isScrollable, setIsScrollable] = useState(true)
  const scrollRef = useRef(null)
  // Состояние для ключа анимации, чтобы при изменении registrationPage происходила анимация
  const [key, setKey] = useState(0)
  useEffect(() => {
    setKey((prevKey) => prevKey + 1)
  }, [fileName])

  useEffect(() => {
    if (texts[fileName] && texts[fileName].text1) {
      // Если данные есть, устанавливаем загрузку в false
      setLoading(false)
    } else {
      // Если данных нет, начинаем ждать
      const intervalId = setInterval(() => {
        if (texts[fileName] && texts[fileName].text1) {
          // Если данные появились, устанавливаем загрузку в false и очищаем интервал
          setLoading(false)
          clearInterval(intervalId)
        }
      }, 500)

      // Очищаем интервал при размонтировании компонента
      return () => clearInterval(intervalId)
    }
  }, [fileName])

  useEffect(() => {
    const checkScrollable = () => {
      if (scrollRef.current) {
        setIsScrollable(
          scrollRef.current.scrollHeight > scrollRef.current.clientHeight
        )
      }
    }

    checkScrollable()
    window.addEventListener("resize", checkScrollable)

    return () => window.removeEventListener("resize", checkScrollable)
  }, [activeSectionResult])

  // Функция для получения контента на основе активной секции
  const getTextContent = () => {
    if (!texts[fileName]) return "Данные не найдены..."
    if (activeSectionResult === 3) return texts[fileName].text3
    if (activeSectionResult === 2) return texts[fileName].text2
    return texts[fileName].text1
  }
  return (
    <motion.div
      key={key}
      initial={{ opacity: 0.3 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0.3 }}
      transition={{ duration: 0.5 }}
    >
      {loading ? (
        <div className="resultFile">
          <div className="textLoadingResultFile">Загрузка...</div>
        </div>
      ) : (
        <div className="resultFile">
          <div className="titleResultFile">{fileName}</div>
          <div className="blockResultFile">
            <div className="containerResultFile">
              <div className="headerContainerResultFile">
                <div
                  className={
                    activeSectionResult === 1
                      ? "sectionHeaderContainerResultFileActive"
                      : "sectionHeaderContainerResultFile"
                  }
                  onClick={() => setActiveSectionResult(1)}
                >
                  Исходный документ
                </div>
                <div
                  className={
                    activeSectionResult === 2
                      ? "sectionHeaderContainerResultFileActive"
                      : "sectionHeaderContainerResultFile"
                  }
                  onClick={() => setActiveSectionResult(2)}
                >
                  Суммаризация
                </div>
                <div
                  className={
                    activeSectionResult === 3
                      ? "sectionHeaderContainerResultFileActive"
                      : "sectionHeaderContainerResultFile"
                  }
                  onClick={() => setActiveSectionResult(3)}
                >
                  Рецензирование
                </div>
              </div>
              <div className="textContResultFile">
                <div
                  className={`textContScrollResultFile`}
                  style={{
                    paddingRight: isScrollable ? "20px" : "0",
                    marginRight: isScrollable ? "35px" : "44px",
                  }}
                  ref={scrollRef}
                >
                  {getTextContent()}
                </div>
              </div>
            </div>
            <div className="btnBottomResultFile">
              <svg
                width="25"
                height="25"
                viewBox="0 0 25 25"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M12.5 9V15M9.5 13L12.5 16L15.5 13M22.5 12.5C22.5 18.0228 18.0228 22.5 12.5 22.5C6.97715 22.5 2.5 18.0228 2.5 12.5C2.5 6.97715 6.97715 2.5 12.5 2.5C18.0228 2.5 22.5 6.97715 22.5 12.5Z"
                  stroke="#89AAFF"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              Скачать
            </div>
          </div>
        </div>
      )}
    </motion.div>
  )
}
