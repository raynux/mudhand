'use strict'
const _ = require('lodash')
const moment = require('moment')
const Queue = require('promise-queue')
const {Sequelize, Board} = require('./libs/database')
const {Op} = Sequelize
const {FUTURE_TYPE, FUTURE_RANGE, MARGIN_THRESHOLD} = require('./libs/common')

async function getFutureType(price, timestamp) {
  const futureRecs = await Board.findAll({
    attributes: ['id', 'price', 'timestamp'],
    where: {
      timestamp: {
        [Op.between]: [
          moment(timestamp).add(1, 'second').toDate(),
          moment(timestamp).add(FUTURE_RANGE).toDate()
        ]
      }
    },
    order: ['timestamp']
  })

  const futurePriceSeq = _.map(futureRecs, (r) => r.price)
  const futurePriceDiffSeq = _.map(futurePriceSeq, (p) => (p / price - 1))

  let futureType = FUTURE_TYPE.STABLE
  futurePriceDiffSeq.forEach((d) => {
    if(d >= MARGIN_THRESHOLD) {
      // console.log('RAISE', _.round(d, 6))
      futureType = FUTURE_TYPE.RAISE
      return
    }
    if(d <= -MARGIN_THRESHOLD) {
      // console.log('DROP', _.round(d, 6))
      futureType = FUTURE_TYPE.DROP
      return
    }
  })

  return futureType
}

async function main() {
  // await sequelize.sync()

  const queue = new Queue(2, Infinity)

  const resp = await Board.findAll({
    attributes: ['id', 'price', 'timestamp'],
    // limit: 10,
    order: ['timestamp']
  })

  resp.forEach((rec) => {
    queue.add(async () => {
      const {price, timestamp} = rec.dataValues
      const futureType = await getFutureType(price, timestamp)

      await rec.update({future: futureType})
    })
  })

  const timer = setInterval(async () => {
    console.log(`QUEUE [ ${queue.getQueueLength()} ]`)
    if(queue.getQueueLength() === 0) {
      clearInterval(timer)
      process.exit(0)
    }
  }, 2000)
}
main()
