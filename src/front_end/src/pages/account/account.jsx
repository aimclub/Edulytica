import { useEffect, useState } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"

import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
import { ResultFile } from "../../components/resultFile/resultFile"
/**
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.accountModal - Флаг, определяющий, отображается ли модальное окно аккаунта
 * @param {function} props.setAccountModal - Функция для установки значения флага отображения модального окна аккаунта
 * @param {boolean} props.profileModal - Флаг, определяющий, отображается ли модальное окно профиля
 * @param {function} props.setProfileModal - Функция для установки значения флага отображения модального окна профиля
 * @param {function} props.setAuthorized - Функция для установки статуса авторизации пользователя
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
            <ResultFile fileName={fileResult} />
          </div>
        ) : null}
      </div>
      {profileModal && (
        <ProfileModal
          name="Мария"
          surname="Федорова"
          nick="fedorova_m"
          birthday="23.09.2006"
          setAuthorized={setAuthorized}
          setProfileModal={setProfileModal}
        />
      )}
    </div>
  )
}
