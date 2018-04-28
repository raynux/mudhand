'use strict'
const _ = require('lodash')
const axios = require('axios')
const fs = require('fs-extra')
const moment = require('moment')

const FETCH_FREQUENCY = 10000
const {QUOINEX_USER, QUOINEX_TOKEN} = process.env
const HISTRICAL_DIR = './historical'
const CURRENCY_PAIR = {
  BTCUSD: 1,
  // BTCEUR: 3,
  BTCJPY: 5,
  ETHBTC: 37,
}

const request = axios.create({
  baseURL: 'https://api.quoine.com',
  timeout: 5000,
  headers: {
    'Authorization': `APIAuth ${QUOINEX_USER}:${QUOINEX_TOKEN}`
  }
})

async function fetchCurrentMarket(productId) {
  const [summaryResp, priceLevelResp] = await Promise.all([
    request.get(`/products/${productId}`),
    request.get(`/products/${productId}/price_levels`)
  ])

  const summary = _.pick(summaryResp.data, [
    'market_ask', 'market_bid', 'low_market_bid', 'high_market_ask',
    'volume_24h', 'last_price_24h'
  ])
  Object.assign(summary, priceLevelResp.data, {ts: moment().unix()})

  return summary
}

async function fetchAndWrite(baseDir, seqNo) {
  _.each(CURRENCY_PAIR, async (productId, pair) => {
    const PAIR_DIR = `${baseDir}/${pair}`

    try {
      const summary = await fetchCurrentMarket(productId)
      Object.assign(summary, {seqNo})
      const data = JSON.stringify(summary)
      const seqStr = `00000${seqNo}`.slice(-6)
      await fs.writeFile(`${PAIR_DIR}/${seqStr}.json`, data)
    }
    catch(e) {
      console.error(`fetchCurrentMarket() failed at SEQ ${seqNo} on ${pair}`)
      process.exit()
    }
  })
}

async function main() {
  const BASE_DIR = `${HISTRICAL_DIR}/${moment().format('YYYYMMDD-HHmmSS')}`
  await fs.mkdir(BASE_DIR)
  for(const pair of _.keys(CURRENCY_PAIR)) {
    await fs.mkdir(`${BASE_DIR}/${pair}`)
  }

  let seqNo = 0
  setInterval(() => {
    fetchAndWrite(BASE_DIR, seqNo)
    console.log(`SEQ NO [ ${seqNo} ] : ${moment().format('YYYY-MM-DD HH:mm:ss')}`)
    seqNo += 1
  }, FETCH_FREQUENCY)
}
main()
