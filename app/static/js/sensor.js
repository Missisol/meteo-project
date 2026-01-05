const rpiT = document.querySelector('#rpi-temperature')
const bmeT = document.querySelector('#bme-temperature')
const dht1T = document.querySelector('#dht1-temperature')

const timer = 1000 * 60 * 5
const postfixBme = ['temperature', 'pressure', 'humidity', 'date']
const postfixDht = ['temperature', 'humidity', 'date']

var socket = io()
socket.on('connect', () => {
    // console.log(socket.id)
})
socket.on('dht_message', (data) => {
    const map = getElementMap(['dht1', 'dht2'], postfixDht)
    getTextContent(map, JSON.parse(data))
})
socket.on('bme_message', (data) => {
    const map = getElementMap('bme', postfixBme)
    getTextContent(map, JSON.parse(data))
})

function getElementMap(prefix, postfix) {
    const dynamicMap = new Map()
    if (typeof prefix === 'string') {
        postfix.forEach((p) => {
            dynamicMap.set(p, document.querySelector(`#${prefix}-${p}`))
        })
    } 
    if (typeof prefix === 'object') {
        prefix.forEach((pref, idx) => {
            postfix.forEach((p) => {
                dynamicMap.set(`${p}${idx + 1}`, document.querySelector(`#${pref}-${p}`))
            })   
        })
    }
    return dynamicMap
}

function getTextContent(map, data) {
    map.forEach((v, k) => {
        if (v && k.startsWith('date')) {
            v.textContent = data?.created_at ? new Date(data.created_at).toLocaleString('ru') : new Date().toLocaleString('ru')
        } 
        if (v && data[k] && !k.startsWith('date')) {
            v.textContent = data[k]
        }
    })
}

async function getSensorData(url, prefix, postfix) {
    const map = getElementMap(prefix, postfix)
    const response = await fetch(url)
    const res = await response.json()
    getTextContent(map, res)
    return res
}

async function checkContent() {
    if (dht1T && !dht1T.innerText) {
        const res = await getSensorData('/api/dht22_mqtt', ['dht1', 'dht2'], postfixDht)
        console.log('res', res)
        
        if (!res.created_at) {
             getSensorData('/api/dht22_db', ['dht1', 'dht2'], postfixDht)
        }
    }
    if (bmeT && !bmeT.innerText) {
        const res = await getSensorData('/api/bme280_mqtt', 'bme', postfixBme)
        if (!res.created_at) {
             getSensorData('/api/bme280_db', 'bme', postfixBme)
        }
    } 
}

function loop() {
    setTimeout(() => {
        getSensorData('/api/bme280_rpi', 'rpi', postfixBme)
        loop()
    }, timer)
  }
  
function init() {
    checkContent()
    if (rpiT) {
        getSensorData('/api/bme280_rpi', 'rpi', postfixBme)
        loop()
    }
}

window.onload = (e) => {
    init()
}
