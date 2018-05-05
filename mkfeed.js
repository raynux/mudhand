'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {mergeLadders} = require('./libs/common')
const {Sequelize, Board} = require('./libs/database')
const {Op} = Sequelize

const FEED_DIR = './feed'
const FEED_PATH = `${FEED_DIR}/data`
const FEED_COUNT = `${FEED_DIR}/count`

const stats = {
  total: 1,
  0: 0,
  1: 0,
  2: 0
}

const timer = setInterval(() => {
  console.log(stats)
}, 5000)

async function displayRecordCount() {
  const total = await Board.count() 
  const stable = await Board.count({where: {future: 0}})
  const raise = await Board.count({where: {future: 1}})
  const drop = await Board.count({where: {future: 2}})

  console.log(`Total  : ${total}`)
  console.log(`Stable : ${stable} [ ${_.round(stable / total, 2)} ]`)
  console.log(`Raise  : ${raise} [ ${_.round(raise / total, 2)} ]`)
  console.log(`Drop   : ${drop} [ ${_.round(drop / total, 2)} ]`)
}

async function getTimestampRange() {
  const results = []
  const min = moment(await Board.min('timestamp'))
  const max = moment(await Board.max('timestamp'))
  const cursor = min.clone()

  while(cursor.isBefore(max)) {

    results.push([
      cursor.clone().toDate(),
      cursor.add(1, 'hours').toDate()
    ])
  }
  return results
}

async function main() {
  await displayRecordCount()
  const ranges = await getTimestampRange()

  const feedWS = fs.createWriteStream(FEED_PATH, {defaultEncoding: 'utf8'})

  for(const range of ranges) {
    const resp = await Board.findAll({
      attributes: ['future', 'bids', 'asks'],
      where: {
        timestamp: {
          [Op.between]: range
        }
      }
    })

    for(const rec of resp) {
      const data = mergeLadders(rec.dataValues)
      feedWS.write(`${JSON.stringify(data)}\n`)

      stats[data.future] += 1
      stats.total += 1
    }
  }

  [feedWS].forEach((ws) => ws.end())
  await fs.writeFile(FEED_COUNT, stats.total)

  clearInterval(timer)
  process.exit(0)
}
main()
