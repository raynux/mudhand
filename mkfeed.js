'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {Sequelize, sequelize, Ohlc, Board} = require('./libs/database')
const {Op} = Sequelize

const SEQ_RANGE = moment.duration(120, 'minutes')

const FEED_DIR = './feed'
const FEED_DATA = `${FEED_DIR}/data`
const FEED_COUNT = `${FEED_DIR}/count`

const stats = {
  total: 0,
  0: 0,
  1: 0,
  2: 0
}

const timer = setInterval(() => {
  console.log(stats)
}, 5000)

async function displayRecordCount() {
  const total = await Ohlc.count() 
  const stable = await Ohlc.count({where: {future: 0}})
  const raise = await Ohlc.count({where: {future: 1}})
  const drop = await Ohlc.count({where: {future: 2}})
  const inv = await Ohlc.count({where: {future: null}})

  console.log(`Total   : ${total}`)
  console.log(`Stable  : ${stable} [ ${_.round(stable / total, 2)} ]`)
  console.log(`Raise   : ${raise} [ ${_.round(raise / total, 2)} ]`)
  console.log(`Drop    : ${drop} [ ${_.round(drop / total, 2)} ]`)
  console.log(`Invalid : ${inv} [ ${_.round(inv / total, 2)} ]`)
}

async function main() {
  await displayRecordCount()
  const feedWS = fs.createWriteStream(FEED_DATA, {defaultEncoding: 'utf8'})

  const baseRecs = await Ohlc.findAll({
    // limit: 1,
    order: sequelize.random()
  })

  for(const base of baseRecs) {
    if(_.isNull(base.future)) { continue }

    const pastRecs = await Ohlc.findAll({
      where: {
        timestamp: {
          [Op.between]: [
            moment(base.timestamp).subtract(SEQ_RANGE).toDate(),
            moment(base.timestamp).subtract(1, 'seconds').toDate()
          ]
        }
      },
      order: [ ['timestamp', 'DESC'] ]
    })

    if(pastRecs.length < SEQ_RANGE.asMinutes()) { continue }

    const past = _(pastRecs)
      .map((r) => {
        return [
          r.open / base.open,
          r.high / base.high,
          r.low / base.low,
          r.close / base.close,
          // r.volume / 10000
        ]
      })
      .value()

    const data = {future: base.future, past}
    feedWS.write(`${JSON.stringify(data)}\n`)
    stats.total += 1
  }

  feedWS.end()
  await fs.writeFile(FEED_COUNT, stats.total)

  clearInterval(timer)
  process.exit(0)
}
main()
