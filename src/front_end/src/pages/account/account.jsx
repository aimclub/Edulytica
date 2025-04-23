import { useEffect, useState } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import { motion } from "framer-motion"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
import { ResultFile } from "../../components/resultFile/resultFile"
import { EditingProfile } from "../../components/editingProfile/editingProfile"
/**
 *  * Компонент страницы аккаунта пользователя.
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.accountModal - Флаг, определяющий, отображается ли модальное окно аккаунта
 * @param {function} props.setAccountModal - Функция для установки значения флага отображения модального окна аккаунта
 * @param {boolean} props.profileModal - Флаг, определяющий, отображается ли модальное окно профиля
 * @param {function} props.setProfileModal - Функция для установки значения флага отображения модального окна профиля
 * @param {function} props.setAuthorized - Функция для установки статуса авторизации пользователя
 * @param {string} props.accountSection - Текущая секция аккаунта ("main", "result" и т. д.).
 * @param {function} props.setAccountSection - Функция для обновления текущей секции аккаунта.
 * @returns {JSX.Element} Страница аккаунта пользователя
 */

export const Account = ({
  accountModal,
  setAccountModal,
  profileModal,
  setProfileModal,
  setAuthorized,
  accountSection,
  setAccountSection,
}) => {
  const [selectedParams, setSelectedParams] = useState([]) // массив для хранения файла и мероприятия
  const [fileResult, setFileResult] = useState("")
  const [editingProfileModal, setEditingProfileModal] = useState(false)
  const [editingProfileAnimation, setEditingProfileAnimation] = useState(false)
  const [infoProfile, setInfoProfile] = useState({
    name: "...",
    surname: "...",
    nick: "fedorova_m",
    birthday: "...",
  })
  const [key, setKey] = useState(0)
  useEffect(() => {
    setKey((prevKey) => prevKey + 1)
  }, [accountSection])
  useEffect(() => {
    if (editingProfileModal) {
      setTimeout(() => setEditingProfileAnimation(true), 10)
    } else {
      setEditingProfileAnimation(false)
    }
  }, [editingProfileModal])
  return (
    <div className="accPage">
      <Header
        authorized={true}
        setAuthorized={null}
        setAccountModal={setAccountModal}
        setProfileModal={setProfileModal}
      />
      <div className="containerAddFile">
        {accountModal ? (
          <AccountModal
            setAccountSection={setAccountSection}
            accountSection={accountSection}
            setFileResult={setFileResult}
          />
        ) : null}
        <div className="addFileAccPageAnimate">
          <motion.div
            key={key}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            {accountSection === "main" ? (
              <div className={`addFileAccPage ${accountModal ? "shift" : ""}`}>
                <AddFile
                  setAccountSection={setAccountSection}
                  selectedParams={selectedParams}
                  setSelectedParams={setSelectedParams}
                  setFileResult={setFileResult}
                />
              </div>
            ) : accountSection === "result" ? (
              <div className={`addFileAccPage ${accountModal ? "shift" : ""}`}>
                <ResultFile fileName={fileResult} />
              </div>
            ) : null}{" "}
          </motion.div>
        </div>
      </div>
      <div className={`profileModalAccPage ${profileModal ? "visible" : ""}`}>
        {profileModal && (
          <ProfileModal
            setAuthorized={setAuthorized}
            setProfileModal={setProfileModal}
            setEditingProfileModal={setEditingProfileModal}
            infoProfile={infoProfile}
          />
        )}
      </div>
      {editingProfileModal && (
        <>
          <div className="editingProfileOverlay" />
          <div
            className={`editingProfileModalWrapper ${
              editingProfileAnimation ? "show" : ""
            }`}
          >
            <EditingProfile
              setEditingProfileModal={() => setEditingProfileModal(false)}
              infoProfile={infoProfile}
              setInfoProfile={setInfoProfile}
            />
          </div>
        </>
      )}
    </div>
  )
}
