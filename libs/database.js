const Sequelize = require('sequelize')

const sequelize = new Sequelize('mudhand', 'root', 'qwerTY123', {
  dialect: 'mysql',
  operatorsAliases: Sequelize.Op,
  logging: false,
  pool: {
    max: 1,
    min: 0
  }
})

const Board = sequelize.define('board', {
  timestamp: {
    type: Sequelize.DATE,
    allowNull: false,
  },
  price: {
    type: Sequelize.INTEGER,
    allowNull: false,
  },
  seqNo: {
    type: Sequelize.INTEGER,
    allowNull: false,
  },
  seqStartAt: {
    type: Sequelize.DATE,
    allowNull: false,
  },
  bids: {
    type: Sequelize.JSON,
    allowNull: false,
  },
  asks: {
    type: Sequelize.JSON,
    allowNull: false,
  },
  future: {
    type: Sequelize.INTEGER,
  },
}, {
  timestamps: false,
  indexes: [
    {
      fields: ['timestamp']
    }
  ]
})

module.exports = {
  Sequelize,
  sequelize,
  Board
}