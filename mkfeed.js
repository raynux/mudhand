'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const {Sequelize, Board} = require('./database')
// const {Op} = Sequelize;

const FEED_DIR = './feed'
const FEED_Y = `${FEED_DIR}/future`
const FEED_X_BIDS = `${FEED_DIR}/bids`
const FEED_X_ASKS = `${FEED_DIR}/asks`
const FEED_COUNT = `${FEED_DIR}/count`

async function main() {
  const resp = await Board.findAll({
    attributes: ['future', 'bids', 'asks'],
    // limit: 1
  })

  const futureWS = fs.createWriteStream(FEED_Y, {defaultEncoding: 'utf8'})
  const bidsWS = fs.createWriteStream(FEED_X_BIDS, {defaultEncoding: 'utf8'})
  const asksWS = fs.createWriteStream(FEED_X_ASKS, {defaultEncoding: 'utf8'})

  const stats = {
    count: 1,
    0: 0,
    1: 0,
    2: 0
  }

  const timer = setInterval(() => {
    console.log(stats)
  }, 5000)

  for(const rec of _.shuffle(resp)) {
    const {future, bids, asks} = rec.dataValues

    // reduce num of STABLE result
    if((_.random(100) % 5 === 0) && future === 0) { continue }

    futureWS.write(`${future}\n`)
    bidsWS.write(`${JSON.stringify(bids)}\n`)
    asksWS.write(`${JSON.stringify(asks)}\n`)

    stats[future] += 1
    stats[count] += 1
  }

  [futureWS, bidsWS, asksWS].forEach((ws) => ws.end())
  await fs.writeFile(FEED_COUNT, stats.count)

  clearInterval(timer)
  console.log(`Finished ${stats}`)
}
main()
