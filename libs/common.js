const _ = require('lodash')
const axios = require('axios')
const moment = require('moment')

const MAX_BOARD_COUNT = 500
const PRODUCT_CODE = 'FX_BTC_JPY'
const LADDER_PAST_BATCH = 10

const FUTURE_TYPE = {
  STABLE: 0,
  RAISE: 1,
  DROP: 2
}
const FUTURE_RANGE = moment.duration(2, 'minutes') 
const MARGIN_THRESHOLD = 0.002

const bfReq = axios.create({ baseURL: 'https://api.bitflyer.jp' })

function mergeLadders(record) {
  return _.concat(_.reverse(record.bids), record.asks) 
}

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

module.exports = {
  PRODUCT_CODE,
  FUTURE_TYPE,
  FUTURE_RANGE,
  LADDER_PAST_BATCH,
  MARGIN_THRESHOLD,
  fetchBoard,
  mergeLadders,
  bfReq
}