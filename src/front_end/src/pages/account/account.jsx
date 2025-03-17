import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
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
}) => {
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
        {accountModal ? <AccountModal /> : null}
        <div className="addFileAccPage">
          <AddFile />
        </div>
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
