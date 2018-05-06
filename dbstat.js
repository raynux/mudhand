'use strict'
const {Sequelize, Board} = require('./libs/database')
const {Op} = Sequelize;

[0, 1, 2].forEach(async (ft) => {
  const c = await Board.count({
    where: {
      future: {
        [Op.eq]: ft
      }
    }
  })
  console.log(`${ft} : ${c}`)
})
