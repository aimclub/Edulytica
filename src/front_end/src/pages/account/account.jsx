import { useEffect, useState, useCallback, useRef } from "react"
import { AccountModal } from "../../components/accountModal/accountModal"
import { AddFile } from "../../components/addFile/addFile"
import { motion } from "framer-motion"
import Header from "../../components/header/header"
import { ProfileModal } from "../../components/profileModal/profileModal"
import "./account.scss"
import { ResultFile } from "../../components/resultFile/resultFile"
import { EditingProfile } from "../../components/editingProfile/editingProfile"
import { AddEvent } from "../../components/addEvent/addEvent"
import { NotificationModal } from "../../components/notificationModal/notificationModal"
import { useSelector, useDispatch } from "react-redux"
import store from "../../store/store"
import { fetchUserData } from "../../store/authSlice"
import {
  fetchTicket,
  fetchTicketHistory,
  setCurrentTicket,
  startPollingForTicket,
  stopPollingForTicket,
  fetchDocumentText,
  startPollingForDocument,
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
  const [selectedParams, setSelectedParams] = useState([
    { type: "mode", name: "рецензирование" },
  ]) // массив для хранения параметров при отправки документа
  const [editingProfileModal, setEditingProfileModal] = useState(false)
  const [editingProfileAnimation, setEditingProfileAnimation] = useState(false)
  const [addEventModal, setAddEventModal] = useState(false)
  const [notificationModal, setNotificationModal] = useState({
    visible: false,
    text: "",
    eta: "",
  })
  const [resultReadyModal, setResultReadyModal] = useState({
    visible: false,
    text: "",
  })
  const [previousTicketId, setPreviousTicketId] = useState(null)
  const [previousUrl, setPreviousUrl] = useState(null)
  const [shownNotifications, setShownNotifications] = useState(new Set())
  const notificationTimeoutRef = useRef(null)

  const userData = useSelector((state) => state.auth.currentUser)
  const { currentTicket, tickets } = useSelector((state) => state.ticket)

  useEffect(() => {
    dispatch(fetchUserData())
  }, [dispatch])

  // Обновляем секцию аккаунта на основе URL
  useEffect(() => {
    const path = location.pathname

    // Закрываем уведомления только при переходе на страницы, отличные от /account/result
    if (path !== "/account/result") {
      // Очищаем таймер уведомлений
      if (notificationTimeoutRef.current) {
        clearTimeout(notificationTimeoutRef.current)
        notificationTimeoutRef.current = null
      }
      setNotificationModal({ visible: false, text: "", eta: "" })
      setResultReadyModal({ visible: false, text: "" })
    }

    if (path === "/account/result") {
      setAccountSection("result")
      // Получаем documentId из параметров URL
      const searchParams = new URLSearchParams(location.search)
      const documentId = searchParams.get("documentId")
      const currentUrl = `${path}?${searchParams.toString()}`

      // Закрываем уведомления при переходе между разными результатами
      if (
        previousUrl &&
        previousUrl !== currentUrl &&
        previousUrl.includes("/account/result")
      ) {
        // Очищаем таймер уведомлений
        if (notificationTimeoutRef.current) {
          clearTimeout(notificationTimeoutRef.current)
          notificationTimeoutRef.current = null
        }
        setNotificationModal({ visible: false, text: "", eta: "" })
        setResultReadyModal({ visible: false, text: "" })
      }

      setPreviousUrl(currentUrl)

      if (documentId) {
        // Получаем актуальные данные из store
        const state = store.getState()
        const { tickets: currentTickets, currentTicket: currentTicketState } =
          state.ticket

        if (currentTickets.length > 0) {
          const foundTicket = currentTickets.find(
            (t) => t.document_id === documentId
          )
          // Диспатчим только если currentTicket не тот же самый
          if (
            foundTicket &&
            (!currentTicketState ||
              currentTicketState.ticketId !== foundTicket.id)
          ) {
            dispatch(fetchTicket(foundTicket.id))
          }
        } else if (!currentTicketState) {
          dispatch(fetchTicketHistory()).then((ticketHistory) => {
            if (ticketHistory && ticketHistory.length > 0) {
              dispatch(fetchTicket(ticketHistory[0].id))
            }
          })
        }
      }
    } else if (path === "/account/help") {
      setAccountSection("help")
    } else if (path === "/account/info") {
      setAccountSection("info")
    } else if (path === "/account") {
      setAccountSection("main")
    }
  }, [
    location.pathname,
    location.search,
    setAccountSection,
    dispatch,
    previousUrl,
  ])

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

  // Отслеживаем переходы между тикетами для показа соответствующих уведомлений
  useEffect(() => {
    // Закрываем уведомления при уходе с тикета
    if (
      previousTicketId &&
      currentTicket &&
      previousTicketId !== currentTicket.ticketId
    ) {
      setNotificationModal({ visible: false, text: "", eta: "" })
      setResultReadyModal({ visible: false, text: "" })
    }

    if (
      location.pathname === "/account/result" &&
      accountSection === "result" &&
      currentTicket &&
      previousTicketId !== currentTicket.ticketId
    ) {
      const ticketId = currentTicket.ticketId
      const notificationKey = `ticket-${ticketId}`

      if (currentTicket.status === "Completed" && currentTicket.files?.result) {
        if (!shownNotifications.has(notificationKey)) {
          setTimeout(() => {
            if (
              location.pathname === "/account/result" &&
              accountSection === "result" &&
              currentTicket?.ticketId === ticketId
            ) {
              setResultReadyModal({
                visible: true,
                text: "Тикет готов",
              })
            }
          }, 250)
          setShownNotifications((prev) => new Set([...prev, notificationKey]))
        }
      } else if (
        currentTicket.status === "Created" ||
        currentTicket.status === "In progress"
      ) {
        // Тикет не готов - показываем уведомление каждый раз с задержкой
        setTimeout(() => {
          if (
            location.pathname === "/account/result" &&
            accountSection === "result" &&
            currentTicket?.ticketId === ticketId
          ) {
            setResultReadyModal({
              visible: true,
              text: "Результат еще не готов, ожидайте",
            })
          }
        }, 250)
      }
    }

    if (currentTicket?.ticketId) {
      setPreviousTicketId(currentTicket.ticketId)
    }
  }, [
    location.pathname,
    accountSection,
    currentTicket,
    previousTicketId,
    shownNotifications,
  ])

  // Закрываем уведомления при уходе со страницы результата
  useEffect(() => {
    // Если мы уходим со страницы результата, закрываем уведомления
    if (
      accountSection !== "result" &&
      (notificationModal.visible || resultReadyModal.visible)
    ) {
      setNotificationModal({ visible: false, text: "", eta: "" })
      setResultReadyModal({ visible: false, text: "" })
    }
  }, [accountSection, notificationModal.visible, resultReadyModal.visible])

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
    async (ticketData) => {
      console.log("Создан тикет:", ticketData)
      dispatch(setCurrentTicket(ticketData))

      // Принудительно загружаем исходный документ для нового тикета
      try {
        await dispatch(fetchDocumentText(ticketData.ticketId))
      } catch (error) {
        console.error("Ошибка при загрузке исходного документа:", error)
        // Если не удалось загрузить сразу, запускаем опрос
        dispatch(startPollingForDocument(ticketData.ticketId))
      }

      const searchParams = new URLSearchParams(window.location.search)
      searchParams.delete("ticketId")
      searchParams.set("documentId", ticketData.ticketInfo.document_id)
      window.history.replaceState(null, "", `?${searchParams.toString()}`)

      const modeItem = selectedParams?.find((p) => p.type === "mode")
      const modeName = (modeItem?.name || "").toLowerCase()
      const eta = modeName.includes("анализ")
        ? "≈ 2 мин"
        : modeName.includes("реценз")
        ? "≈ 5 мин"
        : ""
      setTimeout(() => {
        setNotificationModal({
          visible: true,
          text: "Ваш запрос принят в обработку",
          eta,
        })
      }, 500)
    },
    [dispatch, selectedParams]
  )

  const handleFetchTicketHistory = useCallback(() => {
    dispatch(fetchTicketHistory())
  }, [dispatch])

  const handleCloseNotification = useCallback(() => {
    setNotificationModal({ visible: false, text: "", eta: "" })
  }, [])

  const handleCloseResultReady = useCallback(() => {
    setResultReadyModal({ visible: false, text: "" })
  }, [])

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
                  resetSection={currentTicket?.ticketId}
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
      <NotificationModal
        visible={notificationModal.visible}
        text={notificationModal.text}
        eta={notificationModal.eta}
        onClose={handleCloseNotification}
      />
      <NotificationModal
        visible={resultReadyModal.visible}
        text={resultReadyModal.text}
        eta=""
        onClose={handleCloseResultReady}
        centered={resultReadyModal.text === "Результат еще не готов, ожидайте"}
      />
    </div>
  )
}
