'use strict'
const _ = require('lodash')
const axios = require('axios')
const crypto = require('crypto')
const moment = require('moment')
const {
  FUTURE_TYPE, MARGIN_THRESHOLD, PRODUCT_CODE, LADDER_PAST_BATCH,
  bfReq, fetchBoard, mergeLadders
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
    default: 5000,
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

const BACK_OFF_PERIOD = 60000 * 3
const {BF_APIKEY, BF_SECRET, SLACK_POST_URL} = process.env
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
  const priceDiff = _.round(boardData.price * (MARGIN_THRESHOLD / 2))
  const lowerPrice = boardData.price - priceDiff 
  const higherPrice = boardData.price + priceDiff

  let parentParam, firstParam, secondParam
  if(prediction === FUTURE_TYPE.RAISE) {
    parentParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'MARKET',
      side: 'BUY',
      size: _.toNumber(argv.b)
    }
    firstParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'LIMIT',
      side: 'SELL',
      price: higherPrice,
      size: _.toNumber(argv.b)
    }
    secondParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'STOP_LIMIT',
      side: 'SELL',
      price: lowerPrice,
      trigger_price: lowerPrice,
      size: _.toNumber(argv.b)
    }
  }
  else if(prediction === FUTURE_TYPE.DROP) {
    parentParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'MARKET',
      side: 'SELL',
      size: _.toNumber(argv.b)
    }
    firstParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'LIMIT',
      side: 'BUY',
      price: lowerPrice,
      size: _.toNumber(argv.b)
    }
    secondParam = {
      product_code: PRODUCT_CODE,
      condition_type: 'STOP_LIMIT',
      side: 'BUY',
      price: higherPrice,
      trigger_price: higherPrice,
      size: _.toNumber(argv.b)
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

async function notifySlack(price, body) {
  const side = _.get(body, 'parameters[0].side')
  const text = `${side} : ${price}`
  axios.post(SLACK_POST_URL, { text })
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

  notifySlack(boardData.price, body)
}

async function main() {
  const seqBuf = []

  const timer = setInterval(async () => {
    try {
      const boardData = await fetchBoard()

      seqBuf.push(mergeLadders(boardData))
      if(seqBuf.length < LADDER_PAST_BATCH) {
        console.log(`SEQ LEN ${seqBuf.length}`)
        return
      }
      // if(seqBuf.length < LADDER_PAST_BATCH) {
      //   _.times(10, () => {
      //     seqBuf.push(mergeLadders(boardData))
      //   })
      // }
      const ladders = _.take(_.reverse(seqBuf), LADDER_PAST_BATCH)
      seqBuf.shift()

      const {data} = await pdReq.post('/predict', {ladders})
      const {prediction} = data

      if(argv.d) {
        console.log(`[ ${prediction} ] ${moment().format()} }`)
        return
      }

      if(prediction != FUTURE_TYPE.STABLE) {
        if(! await isReadyToOrder()) { return }
        clearInterval(timer)
        trade(boardData, prediction)
        setTimeout(main, BACK_OFF_PERIOD)   // 
      }
    }
    catch(e) {
      console.error(e)
      console.error('something went wrong')
      clearInterval(timer)
      main() // restart
    }
  }, _.toInteger(argv.f))
}
main()
