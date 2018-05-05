'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const Queue = require('promise-queue')
const storage = fs.pathExistsSync('./key.json') ?
  require('@google-cloud/storage')({ keyFilename: './key.json' }) :
  require('@google-cloud/storage')()
const {sequelize, Board} = require('./database')

const ROOT_DIR = 'board'

async function main() {
  await sequelize.sync()

  const queue = new Queue(10, Infinity)
  const batch = []

  storage.bucket('mudhand')
    .getFilesStream({
      prefix: ROOT_DIR
    })
    .on('error', console.error)
    .on('data', (file) => {
      if(!file.name.match(/\.json$/)) { return }
      queue.add(async () => {
        try {
          // console.log(`QUEUE [ ${queue.getQueueLength()} ] : ${file.name}`)
          const [buf] = await file.download()
          const rec = JSON.parse(buf.toString())

          batch.push({
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

  const pCount = 0
  const timer = setInterval(async () => {
    pCount += batch.length
    await Board.bulkCreate(_.remove(batch))
    console.log(`Processed [ ${pCount} ] | Batch-Insert Size ${batch.length} | DL Queue [ ${queue.getQueueLength()} ]`)

    if(_.isEmpty(batch) && queue.getQueueLength() === 0) {
      console.log('end')
      clearInterval(timer)
    }
  }, 2000)
}
main()
