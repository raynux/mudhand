'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {Sequelize, sequelize, Ohlc} = require('./libs/database')
const {Op} = Sequelize

const SEQ_RANGE = moment.duration(60, 'minutes')

const FEED_DIR = './feed'
const FEED_DATA = `${FEED_DIR}/data`
const FEED_COUNT = `${FEED_DIR}/count`
const FEED_SEQ = `${FEED_DIR}/seq`
const ROUND_DIGITS = 5
const NORMALIZE_MAX = 1.13832

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
    limit: 100000,
    order: sequelize.random()
  })


  for(const base of baseRecs) {
    if(base.future === 0) {
      if(_.sample([true, false])) { continue }
    }

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
          // _.round(r.open / base.open / 1, ROUND_DIGITS),
          _.round(r.high / r.open / NORMALIZE_MAX, ROUND_DIGITS),
          _.round(r.low / r.open / NORMALIZE_MAX, ROUND_DIGITS),
          _.round(r.close / base.close / NORMALIZE_MAX, ROUND_DIGITS),
        ]
      })
      .value()

    const data = {future: base.future, past}
    feedWS.write(`${JSON.stringify(data)}\n`)

    stats[base.future] += 1
    stats.total += 1
  }

  feedWS.end()
  await fs.writeFile(FEED_COUNT, stats.total)
  await fs.writeFile(FEED_SEQ, SEQ_RANGE.asMinutes())

  clearInterval(timer)
  process.exit(0)
}
main()
