import { useEffect, useRef, useState } from "react"
import "./resultFile.scss"
import { motion } from "framer-motion"
import { useDispatch } from "react-redux"
import {
  fetchResultText,
  startPollingForDocument,
} from "../../store/ticketSlice"
import { ticketService } from "../../services/ticket.service"

/**
 * Компонент отображает результат работы над файлом,содержимое файла и позволяет переключаться между его разделами(суммаризация, рецензирование).
 *
 * @param {Object} props - Свойства компонента.
 * @param {string} props.fileName - Имя файла, данные которого отображаются.
 * @param {Object} props.ticketData - Данные о тикете, включая статус.
 * @param {number} props.resetSection - Ключ для сброса активной секции.
 */

export const ResultFile = ({ fileName, ticketData, resetSection }) => {
  const dispatch = useDispatch()
  /** Состояние активного раздела */
  const [activeSectionResult, setActiveSectionResult] = useState(1)

  /** Состояние, указывающее, есть ли прокрутка */
  const [isScrollable, setIsScrollable] = useState(true)
  const scrollRef = useRef(null)
  // Состояние для ключа анимации, чтобы при изменении registrationPage происходила анимация
  const [key, setKey] = useState(0)
  const [error, setError] = useState("") // Новое состояние для ошибки
  const [isDownloading, setIsDownloading] = useState(false) // Состояние для индикации скачивания

  const files = ticketData?.files || {}

  // Сбрасываем активную секцию при смене тикета
  useEffect(() => {
    setActiveSectionResult(1) // Всегда открываем "Исходный документ"
  }, [resetSection])

  // Обработчик клика на кнопку скачать результат
  const handleDownloadResult = async () => {
    if (!ticketData?.ticketId || isDownloading) return

    try {
      setIsDownloading(true)
      await ticketService.downloadResult(ticketData.ticketId)
    } catch (error) {
      console.error("Ошибка при скачивании результата:", error)
      let errorMessage = "Ошибка при скачивании файла"

      if (error?.response?.data?.detail) {
        if (error.response.data.detail.includes("not found")) {
          errorMessage = "Результат ещё не готов. Попробуйте позже."
        } else {
          errorMessage = error.response.data.detail
        }
      }

      setError(errorMessage)
    } finally {
      setIsDownloading(false)
    }
  }

  // Обработчик клика на кнопку скачать исходный документ
  const handleDownloadDocument = async () => {
    if (!ticketData?.ticketId || isDownloading) return

    try {
      setIsDownloading(true)
      await ticketService.downloadDocument(ticketData.ticketId)
    } catch (error) {
      console.error("Ошибка при скачивании документа:", error)
      let errorMessage = "Ошибка при скачивании файла"

      if (error?.response?.data?.detail) {
        if (error.response.data.detail.includes("not found")) {
          errorMessage = "Документ не найден."
        } else {
          errorMessage = error.response.data.detail
        }
      }

      setError(errorMessage)
    } finally {
      setIsDownloading(false)
    }
  }

  useEffect(() => {
    setKey((prevKey) => prevKey + 1)
  }, [fileName])

  // Эффект для загрузки исходного документа, если его нет
  useEffect(() => {
    const fetchDocument = async () => {
      if (ticketData?.ticketId && !ticketData.files?.file) {
        try {
          setError("")
          // Пытаемся загрузить исходный документ
          // Если не получится, опрос запустится автоматически в fetchTicket
        } catch (err) {
          console.error("Ошибка при загрузке исходного документа:", err)
          // Запускаем опрос при ошибке
          dispatch(startPollingForDocument(ticketData.ticketId))
        }
      }
    }
    fetchDocument()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticketData?.ticketId, ticketData?.files?.file, dispatch])

  // Эффект для загрузки результата, если тикет уже выполнен
  useEffect(() => {
    const fetchResult = async () => {
      if (
        ticketData?.status === "Completed" &&
        ticketData?.ticketId &&
        !ticketData.files?.result
      ) {
        try {
          setError("")
          await dispatch(fetchResultText(ticketData.ticketId))
        } catch (err) {
          let msg = "Ошибка при получении результата."
          if (err?.response?.data?.detail) {
            if (err.response.data.detail === "Ticket result not found") {
              msg = "Результат ещё не готов. Попробуйте позже."
            } else {
              msg = err.response.data.detail
            }
          } else if (err?.response?.status === 400) {
            msg = "Результат ещё не готов. Попробуйте позже."
          } else if (err?.message) {
            msg = err.message
          }
          setError(msg)
        }
      }
    }
    fetchResult()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    ticketData?.status,
    ticketData?.ticketId,
    ticketData?.files?.result,
    dispatch,
  ])

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
    // Раздел Исходного документа: показываем сразу, как только загружен
    if (activeSectionResult === 1) {
      if (typeof files.file === "string") {
        return files.file.split("\n")
      }
      if (files.file) {
        return files.file
      }
      return "Загрузка исходного документа..."
    }

    // Раздел Результата: показываем статус или результат
    if (activeSectionResult === 2) {
      // Если тикет в процессе обработки
      if (
        ticketData &&
        (ticketData.status === "Created" || ticketData.status === "In progress")
      ) {
        return `Документ в обработке...`
      }

      // Если статус Completed и есть ошибка
      if (ticketData?.status === "Completed" && error) {
        return "Ошибка при загрузке результата."
      }

      if (error) {
        return error
      }

      // Если статус Completed, но результата еще нет — загружаем
      if (!files.result) {
        return "Загрузка результата..."
      }

      // Если результат есть — выводим его
      if (typeof files.result === "string") {
        return files.result.split("\n")
      }
      return files.result || ""
    }

    // fallback
    return ""
  }

  const textContent = getTextContent()

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
                  {Array.isArray(textContent)
                    ? textContent.map((line, idx) => (
                        <p
                          key={idx}
                          style={{ margin: 0, whiteSpace: "pre-wrap" }}
                        >
                          {line}
                        </p>
                      ))
                    : textContent}
                </div>
              </div>
            </div>
            {activeSectionResult === 1 && files.file && (
              <div
                className={`btnBottomResultFile ${
                  isDownloading ? "downloading" : ""
                }`}
                onClick={handleDownloadDocument}
                style={{ cursor: isDownloading ? "not-allowed" : "pointer" }}
              >
                {isDownloading ? (
                  <svg
                    width="25"
                    height="25"
                    viewBox="0 0 25 25"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className="spinner"
                  >
                    <circle
                      cx="12.5"
                      cy="12.5"
                      r="10"
                      stroke="#89AAFF"
                      strokeWidth="2"
                      fill="none"
                      strokeDasharray="31.416"
                      strokeDashoffset="31.416"
                    />
                  </svg>
                ) : (
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
                )}
                {isDownloading ? "Скачивание..." : "Скачать"}
              </div>
            )}
            {activeSectionResult === 2 &&
              ticketData?.status === "Completed" && (
                <div
                  className={`btnBottomResultFile ${
                    isDownloading ? "downloading" : ""
                  }`}
                  onClick={handleDownloadResult}
                  style={{ cursor: isDownloading ? "not-allowed" : "pointer" }}
                >
                  {isDownloading ? (
                    <svg
                      width="25"
                      height="25"
                      viewBox="0 0 25 25"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      className="spinner"
                    >
                      <circle
                        cx="12.5"
                        cy="12.5"
                        r="10"
                        stroke="#89AAFF"
                        strokeWidth="2"
                        fill="none"
                        strokeDasharray="31.416"
                        strokeDashoffset="31.416"
                      />
                    </svg>
                  ) : (
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
                  )}
                  {isDownloading ? "Скачивание..." : "Скачать"}
                </div>
              )}
          </div>
        </div>
      }
    </motion.div>
  )
}
