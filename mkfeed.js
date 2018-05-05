'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {mergeLadders} = require('./libs/common')
const {Sequelize, Board} = require('./libs/database')
const {Op} = Sequelize

const TEST_RATIO = 4 // 25%

const FEED_DIR = './feed'
const FEED_TRAIN = `${FEED_DIR}/train`
const FEED_TRAIN_COUNT = `${FEED_DIR}/train_count`
const FEED_TEST = `${FEED_DIR}/test`
const FEED_TEST_COUNT = `${FEED_DIR}/test_count`

const stats = {
  trainTotal: 0,
  testTotal: 0,
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

  const trainWS = fs.createWriteStream(FEED_TRAIN, {defaultEncoding: 'utf8'})
  const testWS = fs.createWriteStream(FEED_TEST, {defaultEncoding: 'utf8'})

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

      if(_.random(1000) % TEST_RATIO === 0) {
        testWS.write(`${JSON.stringify(data)}\n`)
        stats.testTotal += 1
      }
      else {
        trainWS.write(`${JSON.stringify(data)}\n`)
        stats[data.future] += 1
        stats.trainTotal += 1
      }
    }
  }

  [trainWS, testWS].forEach((ws) => ws.end())
  await fs.writeFile(FEED_TRAIN_COUNT, stats.trainTotal)
  await fs.writeFile(FEED_TEST_COUNT, stats.testTotal)

  clearInterval(timer)
  process.exit(0)
}
main()
