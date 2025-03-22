import { useEffect, useRef, useState } from "react"
import "./resultFile.scss"
import texts from "./text.js"
export const ResultFile = ({ fileName }) => {
  const [activeSectionResult, setActiveSectionResult] = useState(1)
  const [loading, setLoading] = useState(true) // Добавляем состояние загрузки
  const [isScrollable, setIsScrollable] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (texts[fileName] && texts[fileName].text1) {
      // Если данные есть, устанавливаем загрузку в false
      setLoading(false)
    } else {
      // Если данных нет, начинаем ждать
      const intervalId = setInterval(() => {
        // Проверяем, появились ли данные в `texts`
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

  return loading ? (
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
              {activeSectionResult === 3
                ? texts[fileName].text3
                : activeSectionResult === 2
                ? texts[fileName].text2
                : texts[fileName].text1}
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
  )
}
