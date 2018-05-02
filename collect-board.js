'use strict'
const _ = require('lodash')
const axios = require('axios')
const sts = require('string-to-stream')
const fs = require('fs-extra')
const moment = require('moment')

const storage = fs.pathExistsSync('./key.json') ?
  require('@google-cloud/storage')({ keyFilename: './key.json' }) :
  require('@google-cloud/storage')()

const FETCH_FREQUENCY = 5000
const ROOT_DIR = 'board'
const MAX_BOARD_COUNT = 500

const bucket = storage.bucket('mudhand')

const request = axios.create({
  baseURL: 'https://api.bitflyer.jp/v1',
  timeout: 5000,
  headers: {}
})

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
  const startAt = moment().format('YYYYMMDD-HHmmss')
  const BASE_DIR = `${ROOT_DIR}/${startAt}`
  // await fs.mkdir(BASE_DIR)

  let seqNo = 0
  const timer = setInterval(async () => {
    try {
      const boardData = await fetchBoard()
      Object.assign(boardData, {seqNo, startAt})

      const boardJSON = JSON.stringify(boardData)
      const seqStr = `00000${seqNo}`.slice(-6)

      // await bucket.file(`${BASE_DIR}/${seqStr}.json`).save(boardJSON)
      const file = bucket.file(`${BASE_DIR}/${seqStr}.json`)

      sts(boardJSON)
        .pipe(file.createWriteStream({ gzip: true }))
        .on('error', () => {
          console.error(`fetchBoard() failed at SEQ ${seqNo}`)
          clearInterval(timer)
          main() // restart
        })
        .on('finish', () => {
          console.log(`SEQ NO [ ${seqStr} ] : ${moment().format('YYYY-MM-DD HH:mm:ss')}`)
        })
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
