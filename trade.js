'use strict'
const _ = require('lodash')
const axios = require('axios')
const crypto = require('crypto')
const moment = require('moment')
const {
  FUTURE_TYPE, MARGIN_THRESHOLD, PRODUCT_CODE,
  bfReq, fetchBoard
} = require('./libs/common')
const argv = require('yargs')
  // .usage('Usage: $0 --appid N')
  .options('d', {
    alias: 'dry-run',
    nargs: 0,
    default: false
  })
  .options('f', {
    alias: 'frequency',
    nargs: 1,
    default: 10000,
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

const {BF_APIKEY, BF_SECRET} = process.env
const pdReq = axios.create({ baseURL: argv.p })

async function isReadyToOrder() {
  const timestamp = Date.now().toString()
  const bfReqPath = `/v1/me/getpositions?product_code=${PRODUCT_CODE}`
  const text = `${timestamp}GET${bfReqPath}`
  const sign = crypto.createHmac('sha256', BF_SECRET).update(text).digest('hex')

  const {data} = await bfReq.get(bfReqPath, {
    headers: {
      'ACCESS-KEY': BF_APIKEY,
      'ACCESS-TIMESTAMP': timestamp,
      'ACCESS-SIGN': sign
    }
  })

  return _.isEmpty(data)
}

function mkOrderBody(prediction, boardData) {
  const priceDiff = _.round(boardData.price * MARGIN_THRESHOLD)
  const lowerPrice = boardData.price - priceDiff 
  const higherPrice = boardData.price + priceDiff

  let parentParam, firstParam, secondParam
  if(prediction === FUTURE_TYPE.RAISE) {
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
    time_in_force: 'GTC',
    parameters: [parentParam, firstParam, secondParam]
  }
}

async function trade(boardData, prediction) {
  const timestamp = Date.now().toString()
  const bfReqPath = '/v1/me/sendparentorder'
  const body = mkOrderBody(prediction, boardData)
  const text = `${timestamp}POST${bfReqPath}${JSON.stringify(body)}`
  const sign = crypto.createHmac('sha256', BF_SECRET).update(text).digest('hex')

  console.log(`====== PLACING AN ORDER [ ${prediction} ] =======`)
  console.log(`Current Price : ${boardData.price}`)
  console.log(body)

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

async function main() {
  const timer = setInterval(async () => {
    try {
      const boardData = await fetchBoard()
      const {data} = await pdReq.post('/predict', boardData)
      const {prediction} = data

      if(argv.d) {
        console.log(`[ ${prediction} ] ${moment().format()} }`)
        return
      }

      if(prediction != FUTURE_TYPE.STABLE) {
        if(! await isReadyToOrder()) { return }
        trade(boardData, prediction)
      }
    }
    catch(e) {
      console.error(e.response.data)
      console.error('something went wrong')
      clearInterval(timer)
      main() // restart
    }
  }, argv.f)
}
main()
