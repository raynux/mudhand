'use strict'
const _ = require('lodash')
const moment = require('moment')
const Queue = require('promise-queue')
const {Sequelize, Board} = require('./libs/database')
const {Op} = Sequelize
const {FUTURE_TYPE, FUTURE_RANGE, MARGIN_THRESHOLD} = require('./libs/common')

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
