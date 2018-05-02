const Sequelize = require('sequelize')

const sequelize = new Sequelize('database', 'username', 'password', {
  dialect: 'sqlite',
  storage: './db/db.sqlite',
  operatorsAliases: Sequelize.Op,
  logging: false
})

const Board = sequelize.define('board', {
  timestamp: Sequelize.DATE,
  price: Sequelize.INTEGER,
  seqNo: Sequelize.INTEGER,
  seqStartAt: Sequelize.DATE,
  bids: Sequelize.JSON,
  asks: Sequelize.JSON,
}, {
  timestamps: false
})

module.exports = {
  Sequelize,
  sequelize,
  Board
}
