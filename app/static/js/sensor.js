const rpiT = document.querySelector('#rpi-temperature')
const bmeT = document.querySelector('#bme-temperature')
const dht1T = document.querySelector('#dht1-temperature')

const timer = 1000 * 60 * 5
const postfixBme = ['temperature', 'pressure', 'humidity', 'date']
const postfixDht = ['temperature', 'humidity', 'date']

let MQTT_CONFIG = {
    mqtt_broker_url: 'localhost',
    ws_broker_port: 9001,
    mqtt_topic_esp8266: '/esp8266/#',
    mqtt_topic_bme280: '/esp8266/bme280',
    mqtt_topic_dht22: '/esp8266/dht22',
}

// MQTT подключение через WebSockets (порт 9001)
let MQTT_URL = ''
let mqttClient = null

async function loadConfig() {
    try {
        const res = await fetch('/api/config')
        if (!res.ok) throw new Error('Config fetch failed')
        MQTT_CONFIG = await res.json()
        MQTT_URL = `ws://${MQTT_CONFIG.mqtt_broker_url}:${MQTT_CONFIG.ws_broker_port}`
    } catch (e) {
        console.warn('Using default config:', e)
    }
}

function connectMQTT() {
    mqttClient = mqtt.connect(MQTT_URL, {
        clientId: 'sensor_frontend_' + Math.random().toString(16).substr(2, 8),
        clean: true,
        connectTimeout: 4000,
        reconnectPeriod: 1000,
    })

    mqttClient.on('connect', () => {
        console.log('MQTT connected to', MQTT_URL)
        // Подписка на топики
        mqttClient.subscribe(MQTT_CONFIG.mqtt_topic_esp8266, { qos: 1 })
    })

    mqttClient.on('message', (topic, message) => {
        const data = JSON.parse(message.toString())
        if (topic === MQTT_CONFIG.mqtt_topic_dht22) {
            const map = getElementMap(['dht1', 'dht2'], postfixDht)
            getTextContent(map, data)
        } else if (topic === MQTT_CONFIG.mqtt_topic_bme280) {
            const map = getElementMap('bme', postfixBme)
            getTextContent(map, data)
        }
    })

    mqttClient.on('error', (err) => {
        console.error('MQTT error:', err)
    })

    mqttClient.on('offline', () => {
        console.log('MQTT offline')
    })
}

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
        // if (v && data[k] && !k.startsWith('date')) {
        //     v.textContent = data[k]
        // }
        if (v && !k.startsWith('date')) {
            v.textContent = data[k] === 0 ? 'Нет данных' : data[k]
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
    // Подключение к MQTT через WebSocket
    connectMQTT()
    if (rpiT) {
    getSensorData('/api/bme280_rpi', 'rpi', postfixBme)
    loop()
    }
}

window.onload = async (e) => {
    await loadConfig()
    init()
}
