const moment = require('moment')

module.exports = {
  FUTURE_TYPE: {
    STABLE: 0,
    RAISE: 1,
    DROP: 2
  },
  FUTURE_RANGE: moment.duration(10, 'minutes'),
  MARGIN_THRESHOLD: 0.003
}