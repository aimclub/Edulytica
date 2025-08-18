import { useEffect, useMemo, useRef, useState, useCallback } from "react"
import "./addFile.scss"
import { EventModal } from "../eventModal/eventModal"
import { ticketService } from "../../services/ticket.service"
import { useNavigate } from "react-router-dom"
import { useDispatch } from "react-redux"
import { createTicket } from "../../store/ticketSlice"

/**
 * Компонент для прикрепления и работы с файлом.
 * @param {Object} props - Свойства компонента.
 * @param {Function} props.setAccountSection - Функция для установки активного раздела аккаунта.
 * @param {Array} props.selectedParams - Массив выбранных параметров (файл и мероприятие).
 * @param {Function} props.setSelectedParams - Функция для обновления массива выбранных параметров.
 * @param {Function} props.setFileResult - Функция для установки имени загруженного файла.
 * @param {Function} props.fetchTicketHistory - Функция для получения истории тикетов.
 * @param {Function} props.onTicketCreated - Функция для обработки создания тикета.
 * @returns {JSX.Element} - Элемент интерфейса для работы с файлом.
 */

export const AddFile = ({
  setAccountSection,
  selectedParams,
  setSelectedParams,
  setAddEventModal,
  addEventModal, // Добавляем для отслеживания состояния
  fetchTicketHistory,
  onTicketCreated,
}) => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [eventModal, setEventModal] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0) // Для перерендеринга EventModal
  const fileInputRef = useRef(null)
  const [mode, setMode] = useState("рецензирование")
  const [, setError] = useState(null)

  const openEventModal = () => {
    setEventModal((pr) => !pr)
  }

  const changeMode = () => {
    const newMode = mode === "рецензирование" ? "анализ" : "рецензирование"
    setMode(newMode)
    setSelectedParams((prev) => [
      { type: "mode", name: newMode },
      ...prev.filter((param) => param.type !== "mode"),
    ])
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (
      file &&
      (file.type === "application/pdf" ||
        file.type ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    ) {
      const fileName = file.name
      console.log("Загруженный файл:", fileName)
      setSelectedParams((prev) => [
        { type: "file", name: fileName },
        ...prev.filter((param) => param.type !== "file"),
      ])
    } else {
      setError("Пожалуйста, выберите .pdf или .docx файл")
    }
  }

  const truncateString = (str, maxLength) => {
    if (str.length > maxLength) {
      return str.substring(0, maxLength) + "..."
    }
    return str
  }

  const resetParams = useCallback(() => {
    setSelectedParams([{ type: "mode", name: "рецензирование" }])
    if (fileInputRef.current) {
      fileInputRef.current.value = null
    }
  }, [setSelectedParams])

  const handleHelpPage = useCallback(() => {
    setAccountSection("help")
  }, [setAccountSection])

  const handleAddFileSvg = useCallback(async () => {
    try {
      const fileParam = selectedParams.find((param) => param.type === "file")
      const eventParam = selectedParams.find((param) => param.type === "event")

      if (!fileParam || !eventParam) {
        throw new Error("Необходимо выбрать файл и мероприятие")
      }

      const file = fileInputRef.current.files[0]
      if (!file) {
        throw new Error("Файл не найден")
      }

      const { event_id } = await ticketService.getEventId(eventParam.name)
      const mega_task_id = mode === "рецензирование" ? "1" : "2"
      console.log("mode:", mode, "mega_task_id:", mega_task_id)

      // Создаем тикет через Redux Thunk
      await dispatch(createTicket(file, event_id, mega_task_id))

      await fetchTicketHistory()

      setAccountSection("result")
      // Переход на страницу результата
      navigate(`/account/result`)
      resetParams()
    } catch (error) {
      console.error(error.message || "Произошла ошибка при создании тикета")
      setError(error.message)
    }
  }, [
    setAccountSection,
    resetParams,
    selectedParams,
    fetchTicketHistory,
    mode,
    navigate,
    dispatch,
  ])

  const sortedParams = useMemo(
    () => [...selectedParams].sort((a, b) => (a.type === "file" ? -1 : 1)),
    [selectedParams]
  )

  // Проверяем наличие файла и мероприятия
  const hasRequiredParams = useMemo(() => {
    return (
      selectedParams.some((param) => param.type === "file") &&
      selectedParams.some((param) => param.type === "event")
    )
  }, [selectedParams])

  const refreshEventModal = () => {
    setRefreshKey((prev) => prev + 1)
  }

  // Отслеживаем изменения addEventModal для обновления списка мероприятий
  useEffect(() => {
    if (!addEventModal) {
      // Если модалка добавления мероприятия закрылась, обновляем список
      refreshEventModal()
    }
  }, [addEventModal])

  return (
    <div className="addFile">
      <div className="addFileTopCont">
        <div className="titleAddFile">Начните работу над документом</div>
        <div className="blockAddFile">
          <div className="textBlockAddFile">
            {sortedParams.filter((param) => param.type !== "mode").length > 0
              ? sortedParams
                  .filter((param) => param.type !== "mode")
                  .map((param) => (
                    <div className="paramBlockAddFile" key={param.name}>
                      <svg
                        width="6"
                        height="6"
                        viewBox="0 0 7 7"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <circle
                          cx="3"
                          cy="3"
                          r="3"
                          transform="matrix(-1 0 0 1 6 0)"
                          fill="#89AAFF"
                        />
                      </svg>{" "}
                      {truncateString(param.name, 40)}
                    </div>
                  ))
              : "Выберите параметры работы над документом..."}
          </div>
          <div className="parametersLineAddFile">
            <div className="rightparametersLineAddFileCont">
              <div className="rightparametersLineAddFile">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  style={{ display: "none" }}
                  id="fileUpload"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                />
                <label className="parameterBtnAddFile" htmlFor="fileUpload">
                  <svg
                    width="17"
                    height="17"
                    viewBox="0 0 17 17"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M8.5013 3.54102V13.4577M3.54297 8.49935H13.4596"
                      stroke="#89AAFF"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </label>
                <div className="parameterBtnAddFile" onClick={openEventModal}>
                  <svg
                    width="12"
                    height="11"
                    viewBox="0 0 12 11"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M5.83791 2.3144C6.04905 3.5794 7.14895 4.54648 8.51402 4.67481M1.47266 10.0831H10.3112M6.51062 1.64981L2.47927 5.63273C2.32705 5.78398 2.17974 6.0819 2.15028 6.28815L1.9686 7.77315C1.90476 8.3094 2.31723 8.67607 2.88682 8.5844L4.46793 8.33232C4.6889 8.29565 4.99825 8.1444 5.15047 7.98857L9.18182 4.00565C9.87908 3.31815 10.1933 2.5344 9.10816 1.57648C8.0279 0.627731 7.20788 0.962314 6.51062 1.64981Z"
                      stroke="#89AAFF"
                      strokeWidth="1.5"
                      strokeMiterlimit="10"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  Мероприятие
                </div>
                <div className="parameterBtnAddFile" onClick={handleHelpPage}>
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 18 18"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M16.5 7.5V11.25C16.5 15 15 16.5 11.25 16.5H6.75C3 16.5 1.5 15 1.5 11.25V6.75C1.5 3 3 1.5 6.75 1.5H10.5M16.5 7.5H13.5C11.25 7.5 10.5 6.75 10.5 4.5V1.5M16.5 7.5L10.5 1.5M5.25 9.75H9.75M5.25 12.75H8.25"
                      stroke="#89AAFF"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  Справочник
                </div>
                <div className="parameterBtnAddFile" onClick={changeMode}>
                  <svg
                    width="13"
                    height="13"
                    viewBox="0 0 13 13"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <g clip-path="url(#clip0_514_658)">
                      <path
                        d="M9.75138 4.90977C9.75146 4.69189 9.70843 4.47615 9.62476 4.27498C9.54109 4.0738 9.41844 3.89117 9.26388 3.73761C8.94761 3.43582 8.52725 3.26744 8.09009 3.26744C7.65293 3.26744 7.23257 3.43582 6.9163 3.73761L0.488883 10.1666C0.195527 10.4812 0.0357473 10.8974 0.0432195 11.3274C0.0506917 11.7575 0.224832 12.1678 0.528939 12.472C0.833046 12.7762 1.24337 12.9504 1.67342 12.958C2.10348 12.9656 2.51967 12.8059 2.8343 12.5126L9.26388 6.08356C9.41869 5.92984 9.54148 5.74695 9.62515 5.54548C9.70883 5.344 9.75173 5.12793 9.75138 4.90977ZM2.06838 11.7478C1.95888 11.8521 1.81341 11.9104 1.66213 11.9104C1.51086 11.9104 1.36538 11.8521 1.25588 11.7478C1.14832 11.6399 1.08791 11.4938 1.08791 11.3415C1.08791 11.1892 1.14832 11.0431 1.25588 10.9353L5.46409 6.72652L6.2793 7.54173L2.06838 11.7478ZM8.49905 5.31711L7.04305 6.77365L6.23055 5.95844L7.68709 4.50244C7.73901 4.44312 7.80256 4.3951 7.8738 4.36135C7.94504 4.3276 8.02245 4.30883 8.10124 4.30622C8.18003 4.3036 8.25851 4.31719 8.33183 4.34615C8.40515 4.3751 8.47174 4.4188 8.52749 4.47454C8.58323 4.53029 8.62693 4.59688 8.65588 4.6702C8.68484 4.74352 8.69843 4.82201 8.69581 4.90079C8.6932 4.97958 8.67443 5.05699 8.64068 5.12823C8.60693 5.19947 8.55891 5.26302 8.49959 5.31494L8.49905 5.31711ZM2.63551 1.54656L3.47509 1.30715L3.71451 0.467564C3.75308 0.332843 3.83446 0.214344 3.94636 0.129987C4.05826 0.0456288 4.19458 0 4.33472 0C4.47485 0 4.61117 0.0456288 4.72307 0.129987C4.83497 0.214344 4.91636 0.332843 4.95492 0.467564L5.19434 1.30715L6.03392 1.54656C6.16865 1.58513 6.28714 1.66652 6.3715 1.77842C6.45586 1.89032 6.50149 2.02664 6.50149 2.16677C6.50149 2.30691 6.45586 2.44323 6.3715 2.55513C6.28714 2.66702 6.16865 2.74841 6.03392 2.78698L5.19434 3.0264L4.95492 3.86598C4.91636 4.0007 4.83497 4.1192 4.72307 4.20356C4.61117 4.28792 4.47485 4.33355 4.33472 4.33355C4.19458 4.33355 4.05826 4.28792 3.94636 4.20356C3.83446 4.1192 3.75308 4.0007 3.71451 3.86598L3.47509 3.0264L2.63551 2.78698C2.50079 2.74841 2.38229 2.66702 2.29793 2.55513C2.21357 2.44323 2.16794 2.30691 2.16794 2.16677C2.16794 2.02664 2.21357 1.89032 2.29793 1.77842C2.38229 1.66652 2.50079 1.58513 2.63551 1.54656ZM12.5339 9.28698L11.6943 9.5264L11.4549 10.366C11.4164 10.5007 11.335 10.6192 11.2231 10.7036C11.1112 10.7879 10.9748 10.8335 10.8347 10.8335C10.6946 10.8335 10.5583 10.7879 10.4464 10.7036C10.3345 10.6192 10.2531 10.5007 10.2145 10.366L9.97509 9.5264L9.13551 9.28698C9.00079 9.24841 8.88229 9.16702 8.79793 9.05513C8.71357 8.94323 8.66794 8.80691 8.66794 8.66677C8.66794 8.52664 8.71357 8.39032 8.79793 8.27842C8.88229 8.16652 9.00079 8.08513 9.13551 8.04656L9.97509 7.80715L10.2145 6.96756C10.2531 6.83284 10.3345 6.71434 10.4464 6.62999C10.5583 6.54563 10.6946 6.5 10.8347 6.5C10.9748 6.5 11.1112 6.54563 11.2231 6.62999C11.335 6.71434 11.4164 6.83284 11.4549 6.96756L11.6943 7.80715L12.5339 8.04656C12.6686 8.08513 12.7871 8.16652 12.8715 8.27842C12.9559 8.39032 13.0015 8.52664 13.0015 8.66677C13.0015 8.80691 12.9559 8.94323 12.8715 9.05513C12.7871 9.16702 12.6686 9.24841 12.5339 9.28698ZM9.61867 1.35427L10.3532 1.14465L10.5639 0.409064C10.5982 0.291965 10.6695 0.189132 10.7671 0.115975C10.8648 0.0428183 10.9835 0.00327713 11.1055 0.00327713C11.2276 0.00327713 11.3463 0.0428183 11.444 0.115975C11.5416 0.189132 11.6129 0.291965 11.6472 0.409064L11.8568 1.14356L12.5913 1.35319C12.7084 1.38748 12.8113 1.4588 12.8844 1.55645C12.9576 1.65411 12.9971 1.77284 12.9971 1.89486C12.9971 2.01687 12.9576 2.1356 12.8844 2.23326C12.8113 2.33091 12.7084 2.40223 12.5913 2.43652L11.8568 2.64615L11.6472 3.38227C11.6129 3.49937 11.5416 3.6022 11.444 3.67536C11.3463 3.74852 11.2276 3.78806 11.1055 3.78806C10.9835 3.78806 10.8648 3.74852 10.7671 3.67536C10.6695 3.6022 10.5982 3.49937 10.5639 3.38227L10.3543 2.64831L9.61867 2.43761C9.50157 2.40331 9.39874 2.332 9.32559 2.23434C9.25243 2.13669 9.21289 2.01796 9.21289 1.89594C9.21289 1.77392 9.25243 1.65519 9.32559 1.55754C9.39874 1.45988 9.50157 1.38857 9.61867 1.35427Z"
                        fill="#89AAFF"
                      />
                    </g>
                    <defs>
                      <clipPath id="clip0_514_658">
                        <rect width="13" height="13" fill="white" />
                      </clipPath>
                    </defs>
                  </svg>
                  Режим: {mode}
                </div>
                {selectedParams.some((param) => param.type === "file") &&
                selectedParams.some((param) => param.type === "event") ? (
                  <svg
                    onClick={resetParams}
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M22 12C22 17.52 17.52 22 12 22C6.48 22 3.11 16.44 3.11 16.44M3.11 16.44H7.63M3.11 16.44V21.44M2 12C2 6.48 6.44 2 12 2C18.67 2 22 7.56 22 7.56M22 7.56V2.56M22 7.56H17.56"
                      stroke="#676767"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                ) : null}
              </div>
            </div>
            {hasRequiredParams ? (
              <svg
                onClick={handleAddFileSvg}
                className="svgParameterBtnAddFile2"
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M13.5542 7.1775L9.00172 2.625L4.44922 7.1775M9.00172 15.375V2.7525"
                  stroke="#303030"
                  strokeWidth="1.75"
                  strokeMiterlimit="10"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            ) : (
              <svg
                onClick={handleAddFileSvg}
                width="18"
                className="svgParameterBtnAddFile"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M13.5542 7.1775L9.00172 2.625L4.44922 7.1775M9.00172 15.375V2.7525"
                  stroke="#303030"
                  strokeWidth="1.75"
                  strokeMiterlimit="10"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>
        </div>
      </div>
      <div className="eventModalAddFile">
        {eventModal && (
          <EventModal
            key={refreshKey} // Принудительный перерендер при изменении ключа
            setSelectedEvent={(event) =>
              setSelectedParams((prev) => [
                { type: "event", name: event.name, info: event.info },
                ...prev.filter((param) => param.type !== "event"),
              ])
            }
            closeModal={openEventModal}
            setAddEventModal={setAddEventModal}
          />
        )}
      </div>
    </div>
  )
}
