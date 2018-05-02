'use strict'
const _ = require('lodash')
const fs = require('fs-extra')
const moment = require('moment')
const {Board} = require('./database')

async function main() {
  // await sequelize.sync()

  const resp = await Board.findAll({limit: 10})
  console.log(resp)
}
main()
