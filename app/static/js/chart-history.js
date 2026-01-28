// apexcharts https://apexcharts.com/docs/creating-first-javascript-chart/

import { getMaxDateForCalehdar } from "./helpers.js"

const formEl = document.querySelector('#history-form')
const startInput = document.querySelector('#start-date')
const endInput = document.querySelector('#end-date')
const errorSpan = document.querySelector('#form-error')
const buttonChangeEl = document.querySelector('#button-change')
const historyDialog = document.querySelector('#history-dialog')
const buttonHistory = document.querySelector('#history-button')
const resetHistoryButtons = document.querySelectorAll('button[type=reset]')

const params = [
  ['#chartT', 'temperature', 'температура', ['#1d531c', '#3ba639']],
  ['#chartH', 'humidity', 'влажность', ['#1b4a79', '#3392f1']],
  ['#chartP', 'pressure', 'давление', ['#6e3889', '#cc66ff']],
]
const charts = []

let newStart
let newEnd

buttonHistory.addEventListener('click', () => {
  historyDialog.showModal()
})

function setupForm() {
  const formattedDate = getMaxDateForCalehdar()
  startInput.setAttribute('max', formattedDate)
  endInput.setAttribute('max', formattedDate)
}

function validateForm() {
  if (formEl.start_date.value > formEl.end_date.value) {
    return {error: 'Дата начала периода больше даты конца периода'}
  } 
  if (formEl.start_date.value <= formEl.end_date.value) {
    return {params: `start=${formEl.start_date.value}&end=${formEl.end_date.value}`}
  }
}

function initForm() {
  setupForm()
  formEl.addEventListener('submit', (e) => {
      e.preventDefault()

      if (formEl.start_date.value && formEl.end_date.value) {
        const res = validateForm()

        if (res?.params) {
          getHistoryData(res.params)
          charts.forEach(chart => chart.updateSeries())
          historyDialog.close()
        }
        if (res?.error) {
          newStart = formEl.end_date.value
          newEnd = formEl.start_date.value
          errorSpan.textContent = res.error
        }
      }
  })

  buttonChangeEl.addEventListener('click', () => {
    if (formEl.start_date.value && formEl.end_date.value) {
      newStart = formEl.end_date.value
      newEnd = formEl.start_date.value

      formEl.end_date.value = newEnd
      formEl.start_date.value = newStart
      errorSpan.textContent = ''
    }
  })

  resetHistoryButtons.forEach((button) => {
    button.addEventListener('click', () => {
      if (formEl.start_date.value || formEl.end_date.value) {
        getHistoryData()
        historyDialog.close()
      }  
    })
  })
}

async function getHistoryData(params) {
  const url = params ? `/api/json_history?${params}` : '/api/json_history'
  const response = await fetch(url)
  const res = await response.json()
  updateCharts(res.toReversed())
}

function getChartDataFromDbData(arr, parameter, title) {
  const minValues = []
  const maxValues = []
  
  arr.map((item, idx) => {
    const date = new Date(item.date).toLocaleDateString('ru')
    minValues.push({x: date, y: item[`min_${parameter}`]})
    const edge = parameter !== 'pressure' ? 100 : 800
    const maxV = item[`max_${parameter}`] >= edge ? item[`min_${parameter}`] : item[`max_${parameter}`]
    maxValues.push({x: date, y: maxV})
  })
  const names = [`мин ${title}`, `макс ${title}`]

  return { minValues, maxValues, names }
}

function getSeriesData(dbData, param) {
  const [ _, parameter, title, colors ] = param
  const { minValues, maxValues, names } = getChartDataFromDbData(dbData, parameter, title)
  
  return [
    {
      name: names[0],
      data: minValues,
      color: colors[0],
    },
    {
      name: names[1],
      data: maxValues,
      color: colors[1],
    },
  ]
}

function getOptionsForChart(title, colors) {
  const titleText = title.toUpperCase()

  return {
    title: {
      text: titleText,
      align: 'center',
      style: {
        fontSize: '20px',
        fontFamily: 'system-ui, sans-serif',  
        color: colors[1],
      }
    },
    chart: {
      type: 'line',
      height: 350,
      toolbar: {
        tools: {
          download: false,
          selection: false,
          zoom: false,
          zoomin: false,
          zoomout: false,
          pan: false,
          reset: false,
        },
      },
      zoom: {
        enabled: false,
      },
    },
    series: [],
    stroke: {
      dashArray: [0, 4],
    },
    xaxis: {
      type: 'category',
    },
    legend: {
      labels: {
        colors: ['#b2b0b0', '#b2b0b0']
      },
      markers: {
        strokeWidth: 0,
        offsetX: '-2px',
      }
    },
  }
}

function renderChart(selector, _, title, colors) {
  const options = getOptionsForChart(title, colors)
  const chart = new ApexCharts(document.querySelector(selector), options)
  charts.push(chart)
  chart.render()
}

function initCharts() {
  params.forEach(param => renderChart(...param))
}

function updateCharts(res) {
  params.forEach((param, idx) => {
    const series = getSeriesData(res, param )
    charts[idx].updateSeries(series)
  })
}

async function initHistoryCharts() {
  initCharts()
  initForm()
  getHistoryData()
}

initHistoryCharts()

