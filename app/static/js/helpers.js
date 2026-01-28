const yesterdayRatio = 1000 * 60 * 60 * 24

export const getMaxDateForCalehdar = () => {
  const currentDate = new Date()
  const yesterday = new Date(currentDate - yesterdayRatio)
  const year = yesterday.getFullYear()
  const day = yesterday.getDate() < 10 ? `0${yesterday.getDate()}` : yesterday.getDate()
  const month = yesterday.getMonth() < 9 ? `0${yesterday.getMonth() + 1}` : yesterday.getMonth() + 1
  return `${year}-${month}-${day}`
}


export function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${day}.${month}.${year}, ${hours}:${minutes}:${seconds}`
}
