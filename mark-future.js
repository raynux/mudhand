'use strict'
const _ = require('lodash')
const moment = require('moment')
const Queue = require('promise-queue')
const {Sequelize, sequelize, Ohlc} = require('./libs/database')
const {Op} = Sequelize
const {FUTURE_TYPE, FUTURE_RANGE, MARGIN_THRESHOLD} = require('./libs/common')

async function getFutureType(base) {
  const futureRecs = await Ohlc.findAll({
    where: {
      timestamp: {
        [Op.between]: [
          moment(base.timestamp).add(1, 'second').toDate(),
          moment(base.timestamp).add(FUTURE_RANGE).toDate()
        ]
      }
    },
    order: ['timestamp']
  })

  // Does not have enough future data
  if(futureRecs.length < FUTURE_RANGE.asMinutes()) {
    return null
  }

  const futureCloseSeq = _(futureRecs)
    .map((r) => r.close)
    .map((r) => (r / base.close - 1))
    .map((r) => _.round(r, 4))
    .value()

  let futureType = FUTURE_TYPE.STABLE
  futureCloseSeq.forEach((d) => {
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
  
  // if(_.includes([1,2], futureType)) {
  //   console.log(`${futureType} : ${futureCloseSeq}`)
  // }
  return futureType
}

async function main() {
  await sequelize.sync()

  const queue = new Queue(2, Infinity)

  const resp = await Ohlc.findAll({
    // limit: 2,
    order: ['timestamp']
  })

  resp.forEach((rec) => {
    queue.add(async () => {
      const futureType = await getFutureType(rec)
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
