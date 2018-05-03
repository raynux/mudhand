'use strict'
const fs = require('fs-extra')
const {Sequelize, Board} = require('./database')
const {Op} = Sequelize;

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

  let count = 0
  const futureWS = fs.createWriteStream(FEED_Y, {defaultEncoding: 'utf8'})
  const bidsWS = fs.createWriteStream(FEED_X_BIDS, {defaultEncoding: 'utf8'})
  const asksWS = fs.createWriteStream(FEED_X_ASKS, {defaultEncoding: 'utf8'})

  for(const rec of resp) {
    const {future, bids, asks} = rec.dataValues
    futureWS.write(`${future}\n`)
    bidsWS.write(`${JSON.stringify(bids)}\n`)
    asksWS.write(`${JSON.stringify(asks)}\n`)
    count += 1
  }

  [futureWS, bidsWS, asksWS].forEach((ws) => ws.end())
  await fs.writeFile(FEED_COUNT, count)
  console.log(`${count} batches are populated`)
}
main()
