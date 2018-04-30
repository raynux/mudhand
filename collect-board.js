'use strict'
const _ = require('lodash')
const axios = require('axios')
const fs = require('fs-extra')
const moment = require('moment')

const FETCH_FREQUENCY = 5000
const HISTRICAL_DIR = './data'
const MAX_BOARD_COUNT = 500

const request = axios.create({
  baseURL: 'https://api.bitflyer.jp/v1',
  timeout: 5000,
  headers: {}
})

function ladderDiff(base, ladders, max) {
  return _(ladders)
    .take(max)
    .transform((r, l) => {
      r.push({
        // price: l.price,
        diff: _.round(l.price / base, 6),
        size: l.size
      })
      return r
    }, [])
    .value()
}

async function fetchBoard() {
  const resp = await request.get('/board', {product_code: 'FX_BTC_JPY'})
  const price = resp.data.mid_price

  return {
    price,
    ts: moment().valueOf(),
    bids: ladderDiff(price, resp.data.bids, MAX_BOARD_COUNT),
    asks: ladderDiff(price, resp.data.asks, MAX_BOARD_COUNT)
  }
}

async function main() {
  const BASE_DIR = `${HISTRICAL_DIR}/${moment().format('YYYYMMDD-HHmmss')}`
  await fs.mkdir(BASE_DIR)

  let seqNo = 0
  const timer = setInterval(async () => {
    try {
      const data = JSON.stringify(await fetchBoard())
      const seqStr = `00000${seqNo}`.slice(-6)
      await fs.writeFile(`${BASE_DIR}/${seqStr}.json`, data)

      console.log(`SEQ NO [ ${seqNo} ] : ${moment().format('YYYY-MM-DD HH:mm:ss')}`)
      seqNo += 1
    }
    catch(e) {
      console.error(`fetchBoard() failed at SEQ ${seqNo}`)
      clearInterval(timer)
      main() // restart
    }
  }, FETCH_FREQUENCY)
}
main()
