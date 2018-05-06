'use strict'
const _ = require('lodash')
const {Sequelize, Board} = require('./libs/database')
const {Op} = Sequelize

async function main() {
  const total = await Board.count()

  for(const ft of [0, 1, 2]) {
    const c = await Board.count({
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