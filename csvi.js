'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const readline = require('readline')
const {Ohlc} = require('./libs/database')

async function main() {
  await Ohlc.sync()

  const buf = []

  const inputStream = fs.createReadStream('./data/bf.csv')
  readline.createInterface({ input: inputStream, 'output': {} })
    .on('line', (line) => {
      line = line.split(',')
      const data = {
        timestamp: moment.unix(_.toInteger(line[0])).toDate(),
        open: _.toInteger(line[1]),
        high: _.toInteger(line[2]),
        low: _.toInteger(line[3]),
        close: _.toInteger(line[4])
      }
      // console.log(data)
      buf.push(data)
    })
    .on('close', () => {
      console.log('done')
    })

  const time = setInterval(() => {
    if(buf.length === 0) {
      console.log('ok')
      clearInterval(time)
      return
    }
    Ohlc.bulkCreate(buf.splice(0, buf.length))
  }, 1000)
}
main()
