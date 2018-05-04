'use strict'
const fs = require('fs-extra')
const moment = require('moment')
const Queue = require('promise-queue')
const storage = fs.pathExistsSync('./key.json') ?
  require('@google-cloud/storage')({ keyFilename: './key.json' }) :
  require('@google-cloud/storage')()
const {sequelize, Board} = require('./database')

const ROOT_DIR = 'board'

async function main() {
  const queue = new Queue(5, Infinity)
  await sequelize.sync()

  storage.bucket('mudhand')
    .getFilesStream({
      prefix: ROOT_DIR
    })
    .on('error', console.error)
    .on('data', (file) => {
      if(!file.name.match(/\.json$/)) { return }
      queue.add(async () => {
        try {
          console.log(`QUEUE [ ${queue.getQueueLength()} ] : ${file.name}`)

          const [buf] = await file.download()
          const rec = JSON.parse(buf.toString())

          return Board.create({
            timestamp: rec.ts,
            price: rec.price,
            seqNo: rec.seqNo,
            seqStartAt: moment(rec.startAt, 'YYYYMMDD-HHmmss').toDate(),
            bids: rec.bids,
            asks: rec.asks
          })
        }
        catch(e) {
          console.error(e)
          console.error(file.name)
        }
      })
    })
}
main()
