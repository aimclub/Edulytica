import { useEffect, useState, useCallback } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import { motion } from "framer-motion"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
import { ResultFile } from "../../components/resultFile/resultFile"
import { EditingProfile } from "../../components/editingProfile/editingProfile"
import { AddEvent } from "../../components/addEvent/addEvent"
import { useSelector, useDispatch } from "react-redux"
import { fetchUserData } from "../../store/authSlice"
import {
  fetchTicket,
  fetchTicketHistory,
  setCurrentTicket,
  startPollingForTicket,
  stopPollingForTicket,
} from "../../store/ticketSlice"
import { useLocation } from "react-router-dom"

/**
 *  * Компонент страницы аккаунта пользователя.
 * @param {object} props - Объект с пропсами компонента
 * @param {boolean} props.accountModal - Флаг, определяющий, отображается ли модальное окно аккаунта
 * @param {function} props.setAccountModal - Функция для установки значения флага отображения модального окна аккаунта
 * @param {boolean} props.profileModal - Флаг, определяющий, отображается ли модальное окно профиля
 * @param {function} props.setProfileModal - Функция для установки значения флага отображения модального окна профиля
 * @param {string} props.accountSection - Текущая секция аккаунта ("main", "result" и т. д.).
 * @param {function} props.setAccountSection - Функция для обновления текущей секции аккаунта.
 * @returns {JSX.Element} Страница аккаунта пользователя
 */

export const Account = ({
  accountModal,
  setAccountModal,
  profileModal,
  setProfileModal,
  accountSection,
  setAccountSection,
  isAuth,
}) => {
  const location = useLocation()
  const dispatch = useDispatch()
  const [selectedParams, setSelectedParams] = useState([]) // массив для хранения параметров при отправки документа
  const [editingProfileModal, setEditingProfileModal] = useState(false)
  const [editingProfileAnimation, setEditingProfileAnimation] = useState(false)
  const [addEventModal, setAddEventModal] = useState(false)

  // Получаем данные из Redux store
  const userData = useSelector((state) => state.auth.currentUser)
  const { currentTicket, tickets } = useSelector((state) => state.ticket)

  useEffect(() => {
    dispatch(fetchUserData())
  }, [dispatch])

  // Обновляем секцию аккаунта на основе URL
  useEffect(() => {
    const path = location.pathname
    if (path === "/account/result") {
      setAccountSection("result")
      // Получаем documentId из параметров URL
      const searchParams = new URLSearchParams(location.search)
      const documentId = searchParams.get("documentId")

      if (documentId && tickets.length > 0) {
        const foundTicket = tickets.find((t) => t.document_id === documentId)
        // Диспатчим только если currentTicket не тот же самый
        if (
          foundTicket &&
          (!currentTicket || currentTicket.ticketId !== foundTicket.id)
        ) {
          dispatch(fetchTicket(foundTicket.id))
        }
      } else if (!currentTicket) {
        dispatch(fetchTicketHistory()).then((ticketHistory) => {
          if (ticketHistory && ticketHistory.length > 0) {
            dispatch(fetchTicket(ticketHistory[0].id))
          }
        })
      }
    } else if (path === "/account/help") {
      setAccountSection("help")
    } else if (path === "/account/info") {
      setAccountSection("info")
    } else if (path === "/account") {
      setAccountSection("main")
    }
  }, [location.pathname, location.search, setAccountSection, dispatch]) // eslint-disable-line react-hooks/exhaustive-deps

  // Опрос статуса тикета только если открыт result и статус In progress/Created
  useEffect(() => {
    if (
      accountSection === "result" &&
      currentTicket &&
      (currentTicket.status === "In progress" ||
        currentTicket.status === "Created")
    ) {
      dispatch(startPollingForTicket(currentTicket.ticketId))
      return () => {
        dispatch(stopPollingForTicket(currentTicket.ticketId))
      }
    } else if (currentTicket) {
      // Если уходим с result — останавливаем polling
      dispatch(stopPollingForTicket(currentTicket.ticketId))
    }
  }, [accountSection, currentTicket, dispatch])

  const [infoProfile, setInfoProfile] = useState({
    name: userData?.name || "...",
    surname: userData?.surname || "...",
    login: userData?.login || "...",
    organization: userData?.organization || "...",
  })

  // Обновляем infoProfile при изменении данных пользователя
  useEffect(() => {
    console.log("User data changed, updating infoProfile:", userData)
    if (userData) {
      setInfoProfile({
        name: userData.name || "...",
        surname: userData.surname || "...",
        login: userData.login || "...",
        organization: userData.organization || "...",
      })
    }
  }, [userData])

  const [key, setKey] = useState(0)

  useEffect(() => {
    setKey((prevKey) => prevKey + 1)
  }, [accountSection])

  useEffect(() => {
    if (addEventModal) {
      setTimeout(() => setEditingProfileAnimation(true), 10)
    } else {
      setEditingProfileAnimation(false)
    }
  }, [addEventModal])

  useEffect(() => {
    if (editingProfileModal) {
      setTimeout(() => setEditingProfileAnimation(true), 10)
    } else {
      setEditingProfileAnimation(false)
    }
  }, [editingProfileModal])

  const handleTicketCreated = useCallback(
    (ticketData) => {
      console.log("Создан тикет:", ticketData)
      dispatch(setCurrentTicket(ticketData))
      // Обновляем URL с ID нового тикета
      const searchParams = new URLSearchParams(window.location.search)
      searchParams.delete("ticketId")
      searchParams.set("documentId", ticketData.ticketInfo.document_id)
      window.history.replaceState(null, "", `?${searchParams.toString()}`)
    },
    [dispatch]
  )

  const handleFetchTicketHistory = useCallback(() => {
    dispatch(fetchTicketHistory())
  }, [dispatch])

  return (
    <div className="accPage">
      <Header
        isAuth={isAuth}
        setAccountModal={setAccountModal}
        setProfileModal={setProfileModal}
      />
      <div className="containerAddFile">
        {accountModal ? (
          <AccountModal
            setAccountSection={setAccountSection}
            accountSection={accountSection}
            tickets={tickets}
            fetchTicketHistory={handleFetchTicketHistory}
            currentTicket={currentTicket}
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
                  setAddEventModal={setAddEventModal}
                  addEventModal={addEventModal}
                  fetchTicketHistory={handleFetchTicketHistory}
                  onTicketCreated={handleTicketCreated}
                />
              </div>
            ) : accountSection === "result" ? (
              <div className={`addFileAccPage ${accountModal ? "shift" : ""}`}>
                <ResultFile
                  fileName={currentTicket?.ticketInfo?.document_id || ""}
                  ticketData={currentTicket}
                />
              </div>
            ) : null}
          </motion.div>
        </div>
      </div>
      <div className={`profileModalAccPage ${profileModal ? "visible" : ""}`}>
        {profileModal && (
          <ProfileModal
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
      {addEventModal && (
        <>
          <div className="editingProfileOverlay" />
          <div
            className={`editingProfileModalWrapper ${
              editingProfileAnimation ? "show" : ""
            }`}
          >
            <AddEvent
              setAddEventModal={setAddEventModal}
              fetchTicketHistory={handleFetchTicketHistory}
            />
          </div>
        </>
      )}
    </div>
  )
}
