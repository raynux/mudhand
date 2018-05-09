'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
// const moment = require('moment')
const {mergeLadders} = require('./libs/common')
const {Sequelize, sequelize, Board} = require('./libs/database')
const {Op} = Sequelize

const LADDER_PAST_BATCH = 10

const FEED_DIR = './feed'
const FEED_DATA = `${FEED_DIR}/data`
const FEED_DATA_COUNT = `${FEED_DIR}/count`
const FEED_NZ = `${FEED_DIR}/nz`
const FEED_NZ_COUNT = `${FEED_DIR}/nz_count`

const stats = {
  trainTotal: 0,
  nzTotal: 0,
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

async function main() {
  await displayRecordCount()

  const feedWS = fs.createWriteStream(FEED_DATA, {defaultEncoding: 'utf8'})
  const nzWS = fs.createWriteStream(FEED_NZ, {defaultEncoding: 'utf8'})

  const baseRecs = await Board.findAll({ 
    attributes: ['future', 'timestamp'],
    order: sequelize.random(),
    limit: 1000
  })


  for(const base of baseRecs) {
    const feed = {
      future: base.future,
      ladders: []
    }

    const resp = await Board.findAll({
      attributes: ['bids', 'asks'],
      where: {
        timestamp: {
          [Op.lte]: base.timestamp
        }
      },
      order: [
        ['timestamp', 'DESC']
      ],
      limit: LADDER_PAST_BATCH
    })
    if(resp.length != LADDER_PAST_BATCH) { continue }

    for(const rec of resp) {
      feed.ladders.push(mergeLadders(rec))
    }

    feedWS.write(`${JSON.stringify(feed)}\n`)
    stats[feed.future] += 1
    stats.trainTotal += 1

    if(feed.future != 0) {
      nzWS.write(`${JSON.stringify(feed)}\n`)
      stats.nzTotal += 1
    }
  }

  [feedWS, nzWS].forEach((ws) => ws.end())
  await fs.writeFile(FEED_DATA_COUNT, stats.trainTotal)
  await fs.writeFile(FEED_NZ_COUNT, stats.nzTotal)

  clearInterval(timer)
  process.exit(0)
}
main()
