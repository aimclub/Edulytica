import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
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
        />
      )}
    </div>
  )
}
