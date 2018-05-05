const {sequelize} = require('./libs/database')

async function main() {
  try {
    await sequelize.authenticate()
    console.log('auth ok')
    await sequelize.sync()
    console.log('sync ok')
  }
  catch(e) {
    console.error(e)
  }
}
main()