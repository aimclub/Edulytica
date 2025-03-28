import { useEffect, useState } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"

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
  const [infoProfile, setInfoProfile] = useState({
    name: "...",
    surname: "...",
    nick: "fedorova_m",
    birthday: "...",
  })
  useEffect(() => {}, [accountSection])
  return (
    <div className="accPage">
      <Header
        authorized={true}
        setAuthorized={null}
        setAccountModal={setAccountModal}
        setProfileModal={setProfileModal}
      />
      <div className="containerAddFile">
        {" "}
        {accountModal ? (
          <AccountModal
            setAccountSection={setAccountSection}
            accountSection={accountSection}
            setFileResult={setFileResult}
          />
        ) : null}
        {accountSection === "main" ? (
          <div className="addFileAccPage">
            <AddFile
              setAccountSection={setAccountSection}
              selectedParams={selectedParams}
              setSelectedParams={setSelectedParams}
              setFileResult={setFileResult}
            />
          </div>
        ) : accountSection === "result" ? (
          <div className="addFileAccPage">
            {" "}
            <ResultFile fileName={fileResult} />
          </div>
        ) : null}
      </div>
      {profileModal && (
        <ProfileModal
          setAuthorized={setAuthorized}
          setProfileModal={setProfileModal}
          setEditingProfileModal={setEditingProfileModal}
          infoProfile={infoProfile}
        />
      )}
      {editingProfileModal && (
        <div
          className=""
          style={{
            width: "100vw",
            height: "100vh ",
            marginTop: "-8px",
            zIndex: 20,
            background: "rgba(30, 30, 30, 0.89)",
            position: "fixed",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <EditingProfile
            setEditingProfileModal={setEditingProfileModal}
            infoProfile={infoProfile}
            setInfoProfile={setInfoProfile}
          />
        </div>
      )}
    </div>
  )
}
