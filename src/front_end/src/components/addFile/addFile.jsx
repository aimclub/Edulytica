import { useEffect, useRef, useState } from "react"
import "./addFile.scss"
import { EventModal } from "../eventModal/eventModal"
import { Link } from "react-router-dom"
/**
 *
 * @returns {JSX.Element} block for attaching and working with a file
 */
export const AddFile = ({
  setAccountSection,
  selectedParams,
  setSelectedParams,
  setFileResult,
}) => {
  const [eventModal, setEventModal] = useState(false)

  const fileInputRef = useRef(null)
  const openEventModal = () => {
    setEventModal((pr) => !pr)
  }
  useEffect(() => {
    console.log(selectedParams)
  }, [selectedParams])
  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file && file.type === "application/pdf") {
      const fileName = file.name
      console.log("Загруженный файл:", fileName) // Проверка файла
      setSelectedParams((prev) => [
        { type: "file", name: fileName },
        ...prev.filter((param) => param.type !== "file"),
      ])
      setFileResult(fileName)
    } else {
      alert("Пожалуйста, выберите .pdf файл")
    }
  }
  const truncateString = (str, maxLength) => {
    if (str.length > maxLength) {
      return str.substring(0, maxLength) + "..."
    }
    return str
  }
  const resetParams = () => {
    setSelectedParams([]) // Сброс параметров
    if (fileInputRef.current) {
      fileInputRef.current.value = null // Очищение значения инпута
    }
  }
  const handleHelpPage = () => {
    setAccountSection("help")
  }
  const handleAddFileSvg = () => {
    setAccountSection("result")
    resetParams()
  }
  return (
    <div className="addFile">
      <div className="addFileTopCont">
        <div className="titleAddFile">Начните работу над документом</div>
        <div className="blockAddFile">
          <div className="textBlockAddFile">
            {selectedParams.length > 0
              ? selectedParams
                  .sort((a, b) => (a.type === "file" ? -1 : 1))
                  .map((param) => (
                    <div className="paramBlockAddFile">
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
            <div className="rightparametersLineAddFile">
              <input
                type="file"
                accept=".pdf"
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
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                <span style={{ cursor: "pointer" }}>Прикрепить</span>
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
                    stroke-width="1.5"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                Мероприятие
              </div>
              <Link
                to="/account/help"
                onClick={handleHelpPage}
                style={{ textDecoration: "none" }}
              >
                <div className="parameterBtnAddFile">
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
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Справочник
                </div>
              </Link>
              {selectedParams.length > 0 ? (
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
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              ) : null}
            </div>
            {selectedParams.length === 2 ? (
              <Link to={"/account/result"}>
                {" "}
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
                    stroke-width="1.75"
                    stroke-miterlimit="10"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </Link>
            ) : (
              <svg
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
                  stroke-width="1.75"
                  stroke-miterlimit="10"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            )}
          </div>
        </div>
      </div>
      <div className="eventModalAddFile">
        {eventModal && (
          <EventModal
            setSelectedEvent={(event) =>
              setSelectedParams((prev) => [
                { type: "event", name: event },
                ...prev.filter((param) => param.type !== "event"),
              ])
            }
            closeModal={openEventModal}
          />
        )}
      </div>
    </div>
  )
}
