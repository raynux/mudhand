'use strict'
const sts = require('string-to-stream')
const fs = require('fs-extra')
const moment = require('moment')
const {fetchBoard} = require('./libs/common')
const argv = require('yargs')
  // .usage('Usage: $0 --appid N')
  .options('f', {
    alias: 'frequency',
    nargs: 1,
    default: 5000,
  })
  // .demandOption([''])
  .argv

const storage = fs.pathExistsSync('./key.json') ?
  require('@google-cloud/storage')({ keyFilename: './key.json' }) :
  require('@google-cloud/storage')()

const ROOT_DIR = 'board'
const bucket = storage.bucket('mudhand')

function saveToGCS(boardData) {
  const BASE_DIR = `${ROOT_DIR}/${boardData.startAt}`
  const boardJSON = JSON.stringify(boardData)
  const seqStr = `00000${boardData.seqNo}`.slice(-6)

  const file = bucket.file(`${BASE_DIR}/${seqStr}.json`)

  sts(boardJSON)
    .pipe(file.createWriteStream({ gzip: true }))
    .on('error', () => {
      console.error(`writing error at SEQ ${boardData.seqNo}`)
    })
    .on('finish', () => {
      console.log(`SEQ NO [ ${seqStr} ] : ${moment().format('YYYY-MM-DD HH:mm:ss')}`)
    })
}

async function main() {
  const startAt = moment().format('YYYYMMDD-HHmmss')

  let seqNo = 0
  const timer = setInterval(async () => {
    try {
      const boardData = await fetchBoard()
      Object.assign(boardData, {seqNo, startAt})
      saveToGCS(boardData)
      seqNo += 1
    }
    catch(e) {
      console.error(e)
      console.error(`something went wrong at SEQ ${seqNo}`)
      clearInterval(timer)
      main() // restart
    }
  }, argv.f)
}
main()
