'use strict'
const _ = require('lodash')
// const fs = require('fs-extra')
const moment = require('moment')
const axios = require('axios')
const {Ohlc} = require('./libs/database')

// const storage = fs.pathExistsSync('./key.json') ?
//   require('@google-cloud/storage')({ keyFilename: './key.json' }) :
//   require('@google-cloud/storage')()

// const ROOT_DIR = 'ohlc'
// const bucket = storage.bucket('mudhand')


async function main() {
  await Ohlc.sync()

  const cursor = moment()
  const origin = moment().subtract(100, 'days')

  while(cursor.isAfter(origin)) {
    try {
      const resp = await axios.get('https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc', {
        params: {
          periods: 60,
          before: cursor.unix(),
          after: cursor.subtract(1, 'days').unix(),
        }
      })

      const stat = _.get(resp, 'data.allowance')
      stat.cursor = cursor.clone().format('YYYY-MM-DD')

      const recs = _.get(resp, 'data.result[60]')
      if(!recs) { break }

      stat.line = recs.length
      console.log(stat)

      for(const rec of recs) {
        const data = {
          timestamp: moment.unix(rec[0]).toDate(),
          open: rec[1],
          high: rec[2],
          low: rec[3],
          close: rec[4],
          volume: rec[5],
        }

        await Ohlc.upsert(data)
      }
    }
    catch(e) {
      console.error(e)
    }
  }


  process.exit()
}
main()
