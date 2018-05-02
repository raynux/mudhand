'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {Sequelize, Board} = require('./database')
const {Op} = Sequelize

const FUTURE_TYPE = {
  STABLE: 0,
  RAISE: 1,
  DROP: -1
}

const FUTURE_RANGE = moment.duration(30, 'minutes')
const THRESHOLD = 0.005

async function main() {
  // await sequelize.sync()

  const resp = await Board.findAll({
    attributes: ['id', 'price', 'timestamp'],
    // limit: 10,
    order: ['timestamp']
  })
  resp.forEach(async (rec) => {
    const {price, timestamp} = rec.dataValues
    const from = moment(timestamp).add(1, 'second').toDate()
    const to = moment(timestamp).add(FUTURE_RANGE).toDate()

    const futureRecs = await Board.findAll({
      attributes: ['id', 'price', 'timestamp'],
      where: {
        timestamp: {
          [Op.between]: [from, to]
        }
      },
      order: ['timestamp']
    })

    const priceSeq = _.map(futureRecs, (r) => r.price)
    const priceDiffSeq = _.map(priceSeq, (p) => (p / price - 1))

    let futureType = FUTURE_TYPE.STABLE
    priceDiffSeq.forEach((d) => {
      if(d >= THRESHOLD) {
        // console.log('RAISE', _.round(d, 6))
        futureType = FUTURE_TYPE.RAISE
        return
      }
      if(d <= -THRESHOLD) {
        // console.log('DROP', _.round(d, 6))
        futureType = FUTURE_TYPE.DROP
        return
      }
    })

    await rec.update({future: futureType})
  })
}
main()
