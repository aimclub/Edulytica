import { useEffect, useRef, useState } from "react"
import "./resultFile.scss"
import { motion } from "framer-motion"
import { useDispatch } from "react-redux"
import { fetchTicketFiles } from "../../store/ticketSlice"
/**
 * Компонент отображает результат работы над файлом,содержимое файла и позволяет переключаться между его разделами(суммаризация, рецензирование).
 *
 * @param {Object} props - Свойства компонента.
 * @param {string} props.fileName - Имя файла, данные которого отображаются.
 * @param {Object} props.ticketData - Данные о тикете, включая статус.
 */

export const ResultFile = ({ fileName, ticketData }) => {
  const dispatch = useDispatch()
  /** Состояние активного раздела */
  const [activeSectionResult, setActiveSectionResult] = useState(1)

  /** Состояние, указывающее, есть ли прокрутка */
  const [isScrollable, setIsScrollable] = useState(true)
  const scrollRef = useRef(null)
  // Состояние для ключа анимации, чтобы при изменении registrationPage происходила анимация
  const [key, setKey] = useState(0)

  const files = ticketData?.files || {}

  useEffect(() => {
    setKey((prevKey) => prevKey + 1)
  }, [fileName])

  // Эффект для загрузки файлов, если тикет уже выполнен
  useEffect(() => {
    if (
      ticketData?.status === "Completed" &&
      ticketData?.ticketId &&
      !ticketData.files
    ) {
      dispatch(fetchTicketFiles(ticketData.ticketId))
    }
  }, [ticketData?.status, ticketData?.ticketId, ticketData?.files, dispatch])

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
    // Если тикет в процессе обработки, всегда показывать статус
    if (
      ticketData &&
      (ticketData.status === "Created" || ticketData.status === "In progress")
    ) {
      return `Статус: ${ticketData.status}`
    }

    // Если статус 'Completed', но файлы еще не загружены
    if (!files) {
      if (ticketData?.status === "Completed") {
        return `Статус: ${ticketData.status}`
      }
      return "Загрузка..."
    }

    // Если файлы загружены (статус 'Completed')
    // if (activeSectionResult === 3) return files.result || ""
    // if (activeSectionResult === 2) return files.summary || ""
    if (activeSectionResult === 2) return files.result || ""
    return files.file || ""
  }

  return (
    <motion.div
      key={key}
      initial={{ opacity: 0.3 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0.3 }}
      transition={{ duration: 0.5 }}
    >
      {
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
                {/* <div
                  className={
                    activeSectionResult === 2
                      ? "sectionHeaderContainerResultFileActive"
                      : "sectionHeaderContainerResultFile"
                  }
                  onClick={() => setActiveSectionResult(2)}
                >
                  Суммаризация
                </div> */}
                <div
                  className={
                    activeSectionResult === 2
                      ? "sectionHeaderContainerResultFileActive"
                      : "sectionHeaderContainerResultFile"
                  }
                  onClick={() => setActiveSectionResult(2)}
                >
                  {/* Рецензирование */}
                  Результат
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
            {activeSectionResult === 2 && (
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
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Скачать
              </div>
            )}
          </div>
        </div>
      }
    </motion.div>
  )
}
