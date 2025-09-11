import { useState, useCallback } from "react"

/**
 * Custom hook to handle errors in event handlers
 * Since ErrorBoundary doesn't catch errors in event handlers,
 * this hook provides a way to catch and display them
 */
export const useErrorHandler = () => {
  const [error, setError] = useState(null)
  const [showNotification, setShowNotification] = useState(false)

  const handleError = useCallback((error) => {
    console.error("Error caught by useErrorHandler:", error)

    setError(error)
    setShowNotification(true)

    // Auto-hide notification after 10 seconds
    setTimeout(() => {
      setShowNotification(false)
    }, 10000)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
    setShowNotification(false)
  }, [])

  const safeHandler = useCallback(
    (handler) => {
      return (...args) => {
        try {
          return handler(...args)
        } catch (err) {
          handleError(err)
        }
      }
    },
    [handleError]
  )

  return {
    error,
    showNotification,
    handleError,
    clearError,
    safeHandler,
  }
}
