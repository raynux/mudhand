'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {sequelize, Board} = require('./database')

const DATA_DIR = './data'

function getTargets() {
  const targets = {}
  for(const dir of fs.readdirSync(DATA_DIR)) {
    if(!fs.lstatSync(`${DATA_DIR}/${dir}`).isDirectory()) { continue }

    for(const file of fs.readdirSync(`${DATA_DIR}/${dir}`)) {
      if(!_.get(targets, dir)) { targets[dir] = [] }
      targets[dir].push(file)
    }
  }
  return targets
}

async function main() {
  const targets = getTargets()
  await sequelize.sync()

  for(const k of _.keys(targets)) {
    for(const fname of targets[k]) {
      const rec = require(`${DATA_DIR}/${k}/${fname}`)
      await Board.create({
        timestamp: rec.ts,
        price: rec.price,
        seqNo: rec.seqNo,
        seqStartAt: moment(k, 'YYYYMMDD-HHmmss').toDate(),
        bids: rec.bids,
        asks: rec.asks
      })
      .catch((e) => console.error(e) )
      console.log(`${DATA_DIR}/${k}/${fname}`)
    }
  }
}
main()
