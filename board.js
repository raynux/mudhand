'use strict'
const _ = require('lodash')
const axios = require('axios')
const crypto = require('crypto')
const sts = require('string-to-stream')
const fs = require('fs-extra')
const moment = require('moment')
const {FUTURE_TYPE, FUTURE_RANGE, MARGIN_THRESHOLD} = require('./libs/common')
const argv = require('yargs')
  // .usage('Usage: $0 --appid N')
  .options('f', {
    alias: 'frequency',
    nargs: 1,
    default: 5000,
  })
  .options('s', {
    alias: 'save-to-gcs',
    nargs: 0,
    default: false,
  })
  .options('t', {
    alias: 'trade',
    nargs: 0,
    default: false,
  })
  .options('p', {
    alias: 'prediction-server',
    nargs: 1,
    default: 'http://localhost:5000',
  })
  .options('b', {
    alias: 'bet',
    nargs: 1,
    default: 0.01
  })
  // .demandOption([''])
  .argv

const storage = fs.pathExistsSync('./key.json') ?
  require('@google-cloud/storage')({ keyFilename: './key.json' }) :
  require('@google-cloud/storage')()

const ROOT_DIR = 'board'
const MAX_BOARD_COUNT = 500
const PRODUCT_CODE = 'FX_BTC_JPY'
const {BF_APIKEY, BF_SECRET} = process.env

const bfReq = axios.create({ baseURL: 'https://api.bitflyer.jp' })
const pdReq = axios.create({ baseURL: argv.p })

const bucket = storage.bucket('mudhand')

function ladderDiff(base, ladders, max) {
  return _(ladders)
    .take(max)
    .transform((r, l) => {
      // [diff, size]
      r.push([_.round(l.price / base, 6), l.size])
      return r
    }, [])
    .value()
}

async function fetchBoard() {
  const resp = await bfReq.get('/v1/board', {
    params: {
      product_code: PRODUCT_CODE
    }
  })
  const price = resp.data.mid_price

  return {
    price,
    ts: moment().valueOf(),
    bids: ladderDiff(price, resp.data.bids, MAX_BOARD_COUNT),
    asks: ladderDiff(price, resp.data.asks, MAX_BOARD_COUNT)
  }
}

function saveToGCS(boardData) {
  const BASE_DIR = `${ROOT_DIR}/${boardData.startAt}`
  const boardJSON = JSON.stringify(boardData)
  const seqStr = `00000${boardData.seqNo}`.slice(-6)

  const file = bucket.file(`${BASE_DIR}/${seqStr}.json`)

  sts(boardJSON)
    .pipe(file.createWriteStream({ gzip: true }))
    .on('error', () => {
      console.error(`writing error at SEQ ${boardData.seqNo}`)
    })
    .on('finish', () => {
      console.log(`SEQ NO [ ${seqStr} ] : ${moment().format('YYYY-MM-DD HH:mm:ss')}`)
    })
}

function mkOrderBody(prediction, boardData) {
  const priceDiff = _.round(boardData.price * MARGIN_THRESHOLD)
  const lowerPrice = boardData.price - priceDiff 
  const higherPrice = boardData.price + priceDiff

  let parentParam, firstParam, secondParam
  if(prediction === FUTURE_TYPE.RAISE) {
    // parentParam = {
    //   product_code: PRODUCT_CODE,
    //   condition_type: 'LIMIT',
    //   price: boardData.price,
    //   side: 'BUY',
    //   size: argv.b
    // }
    parentParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'MARKET',
      side: 'BUY',
      size: argv.b
    }
    firstParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'LIMIT',
      side: 'SELL',
      price: higherPrice,
      size: argv.b
    }
    secondParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'STOP_LIMIT',
      side: 'SELL',
      price: lowerPrice,
      trigger_price: lowerPrice,
      size: argv.b
    }
  }
  else if(prediction === FUTURE_TYPE.DROP) {
    parentParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'MARKET',
      side: 'SELL',
      size: argv.b
    }
    firstParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'LIMIT',
      side: 'BUY',
      price: lowerPrice,
      size: argv.b
    }
    secondParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'STOP_LIMIT',
      side: 'BUY',
      price: higherPrice,
      trigger_price: higherPrice,
      size: argv.b
    }
  }
  else {
    console.error('WTF?')
    process.exit(1)
  }

  return {
    order_method: 'IFDOCO',
    minute_to_expire: FUTURE_RANGE.asMinutes(),
    time_in_force: 'GTC',
    parameters: [parentParam, firstParam, secondParam]
  }
}

async function trade(boardData) {
  const {data} = await pdReq.post('/predict', boardData)
  const {prediction} = data

  if(prediction != FUTURE_TYPE.STABLE) {
    const timestamp = Date.now().toString()
    const bfReqPath = '/v1/me/sendparentorder'
    const body = mkOrderBody(prediction, boardData)
    const text = `${timestamp}POST${bfReqPath}${JSON.stringify(body)}`
    const sign = crypto.createHmac('sha256', BF_SECRET).update(text).digest('hex')

    console.log(`Current Price : ${boardData.price}`)
    console.log(body)

    try {
      const resp = await bfReq.post(bfReqPath, body, {
        headers: {
          'ACCESS-KEY': BF_APIKEY,
          'ACCESS-TIMESTAMP': timestamp,
          'ACCESS-SIGN': sign
        }
      })
      console.log('====== DONE =======')
      console.log(resp.data)
    }
    catch(e) {
      console.log('====== ERROR =======')
      console.error(e.response.data)
    }
  }
}

async function main() {
  const startAt = moment().format('YYYYMMDD-HHmmss')

  let seqNo = 0
  const timer = setInterval(async () => {
    try {
      const boardData = await fetchBoard()
      Object.assign(boardData, {seqNo, startAt})

      if(argv.s) { saveToGCS(boardData) }
      // if(argv.t) { trade(boardData) }
      if(argv.t) { trade(boardData) ; clearInterval(timer)}
      seqNo += 1
    }
    catch(e) {
      console.error(`something went wrong at SEQ ${seqNo}`)
      clearInterval(timer)
      main() // restart
    }
  }, argv.f)
}
main()
