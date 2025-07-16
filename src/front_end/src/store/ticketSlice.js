import { createSlice } from "@reduxjs/toolkit"
import { ticketService } from "../services/ticket.service"

// Глобальный объект для хранения активных интервалов опроса
const activePolls = {}

// Получаем начальное состояние из localStorage или используем дефолтное
const getInitialState = () => {
  const savedState = localStorage.getItem("ticketState")
  if (savedState) {
    try {
      return JSON.parse(savedState)
    } catch (e) {
      console.error("Ошибка при парсинге сохраненного состояния тикета:", e)
    }
  }
  return {
    currentTicket: null,
    tickets: [],
    loading: false,
    error: null,
  }
}

const ticketSlice = createSlice({
  name: "ticket",
  initialState: getInitialState(),
  reducers: {
    setCurrentTicket: (state, action) => {
      state.currentTicket = action.payload
      // Сохраняем состояние в localStorage
      localStorage.setItem("ticketState", JSON.stringify(state))
    },
    setTickets: (state, action) => {
      state.tickets = action.payload
      localStorage.setItem("ticketState", JSON.stringify(state))
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
    clearTicketState: (state) => {
      state.currentTicket = null
      state.tickets = []
      state.loading = false
      state.error = null
      localStorage.removeItem("ticketState")
      // Останавливаем все активные опросы при выходе
      Object.keys(activePolls).forEach((ticketId) => {
        clearInterval(activePolls[ticketId])
        delete activePolls[ticketId]
      })
    },
  },
})

// Thunk для получения истории тикетов
export const fetchTicketHistory = () => async (dispatch) => {
  try {
    dispatch(setLoading(true))
    const ticketHistory = await ticketService.getTicketHistory()
    dispatch(setTickets(ticketHistory))
    return ticketHistory
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// Thunk для получения данных конкретного тикета
export const fetchTicket = (ticketId) => async (dispatch) => {
  try {
    dispatch(setLoading(true))
    const ticketInfo = await ticketService.getTicket(ticketId)
    const ticketStatus = await ticketService.getTicketStatus(ticketId)
    const ticketData = {
      ticketId: ticketInfo.ticket.id,
      ticketInfo: ticketInfo.ticket,
      status: ticketStatus.status,
    }
    dispatch(setCurrentTicket(ticketData))

    // Если тикет в обработке, запускаем опрос
    if (
      ticketData.status === "In progress" ||
      ticketData.status === "Created"
    ) {
      dispatch(startPollingForTicket(ticketId))
    }

    return ticketData
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// Thunk для создания нового тикета
export const createTicket =
  (file, eventId, mega_task_id) => async (dispatch) => {
    try {
      dispatch(setLoading(true))
      const data = await ticketService.createNewTicket(
        file,
        eventId,
        mega_task_id
      )
      // После создания тикета, загружаем его данные и запускаем опрос
      await dispatch(fetchTicket(data.ticket_id))
      return data.ticket_id
    } catch (error) {
      dispatch(setError(error.message))
      throw error
    } finally {
      dispatch(setLoading(false))
    }
  }

export const fetchTicketFiles = (ticketId) => async (dispatch, getState) => {
  try {
    dispatch(setLoading(true))

    // Получаем Blobs
    const [fileBlob, resultBlob] = await Promise.all([
      ticketService.getTicketFile(ticketId),
      ticketService.getTicketResult(ticketId),
    ])

    // Вспомогательная функция для гарантии PDF/DOCX
    async function ensurePdfOrDocxFile(blob, filename) {
      // Если это PDF или DOCX — просто обернуть в File
      if (blob.type === "application/pdf") {
        return new File([blob], filename, { type: "application/pdf" })
      }
      if (
        blob.type ===
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
      ) {
        return new File([blob], filename, {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        })
      }
      // Если это текст — конвертировать в PDF
      if (blob.type === "text/plain") {
        const text = await blob.text()
        // Используем jsPDF для конвертации текста в PDF
        const jsPDF = (await import("jspdf")).jsPDF
        const doc = new jsPDF()
        doc.text(text, 10, 10)
        const pdfBlob = doc.output("blob")
        return new File([pdfBlob], filename, { type: "application/pdf" })
      }
      // Для других типов — можно добавить обработку
      // По умолчанию — пробуем как PDF
      return new File([blob], filename, { type: "application/pdf" })
    }

    // Оборачиваем Blobs в File (PDF или DOCX)
    const fileFile = await ensurePdfOrDocxFile(fileBlob, "file.pdf")
    const resultFile = await ensurePdfOrDocxFile(resultBlob, "result.txt")

    // Парсим файлы через бэкенд
    const [file, result] = await Promise.all([
      ticketService.parseFileText(fileFile),
      ticketService.parseFileText(resultFile),
    ])

    // Обновляем текущий тикет с загруженными строками
    const prev = getState().ticket.currentTicket
    dispatch(
      setCurrentTicket({
        ...prev,
        files: {
          file,
          result,
        },
      })
    )

    return { file, result }
  } catch (error) {
    dispatch(setError(error.message))
    throw error
  } finally {
    dispatch(setLoading(false))
  }
}

// --- Логика опроса ---

const pollTicketStatus = (ticketId) => async (dispatch, getState) => {
  try {
    const ticketStatus = await ticketService.getTicketStatus(ticketId)
    const { currentTicket } = getState().ticket

    // Обновляем статус в текущем тикете, если он открыт
    if (currentTicket && currentTicket.ticketId === ticketId) {
      dispatch(
        setCurrentTicket({ ...currentTicket, status: ticketStatus.status })
      )
    }

    // Если обработка завершена, останавливаем опрос и загружаем файлы
    if (ticketStatus.status === "Completed") {
      dispatch(stopPollingForTicket(ticketId))
      dispatch(fetchTicketFiles(ticketId))
    }
  } catch (error) {
    console.error(`Ошибка опроса для тикета ${ticketId}:`, error)
    dispatch(stopPollingForTicket(ticketId)) // Останавливаем при ошибке
  }
}

export const startPollingForTicket = (ticketId) => (dispatch) => {
  if (activePolls[ticketId]) {
    return // Уже опрашивается
  }
  const intervalId = setInterval(() => {
    dispatch(pollTicketStatus(ticketId))
  }, 2000)
  activePolls[ticketId] = intervalId
}

export const stopPollingForTicket = (ticketId) => () => {
  if (activePolls[ticketId]) {
    clearInterval(activePolls[ticketId])
    delete activePolls[ticketId]
  }
}

export const {
  setCurrentTicket,
  setTickets,
  setLoading,
  setError,
  clearTicketState,
} = ticketSlice.actions

export default ticketSlice.reducer
