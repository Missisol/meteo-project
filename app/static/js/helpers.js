const yesterdayRatio = 1000 * 60 * 60 * 24

export const getMaxDateForCalehdar = () => {
  const currentDate = new Date()
  const yesterday = new Date(currentDate - yesterdayRatio)
  const year = yesterday.getFullYear()
  const day = yesterday.getDate() < 10 ? `0${yesterday.getDate()}` : yesterday.getDate()
  const month = yesterday.getMonth() < 9 ? `0${yesterday.getMonth() + 1}` : yesterday.getMonth() + 1
  return `${year}-${month}-${day}`
}
