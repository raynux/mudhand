'use strict'
const _ = require('lodash')
const {Sequelize, Ohlc} = require('./libs/database')
const {Op} = Sequelize

async function main() {
  const total = await Ohlc.count()

  for(const ft of [0, 1, 2, null]) {
    const c = await Ohlc.count({
      where: {
        future: {
          [Op.eq]: ft
        }
      }
    })
    console.log(`${ft} : ${c} (${_.round(c / total, 4)})`)
  }
  process.exit()
}
main()