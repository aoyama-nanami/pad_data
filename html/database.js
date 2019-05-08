import { atkEval } from './common.js'

class Database {
  constructor() {
    this.loadDatabase()
    this.data = []
  }

  loadDatabase() {
    fetch('data/jp_cards_merged.json')
      .then(r => r.json())
      .then(obj => {
        let a = []
        obj.forEach(c => a[c.card_id] = c)
        this.data = a
        this.sort()
        document.querySelector('#loading').style.display = 'none'
        document.querySelector('#main').style.display = 'grid'
        console.log(this.card(999))
      })
  }

  card(i) {
    return this.data[i]
  }

  compareFunction_(sortBy) {
    if (sortBy == 'atk') {
      return (row1, row2) => row2[1] - row1[1]
    } else if (sortBy == 'cd') {
      return (row1, row2) => row1[0].skill.turn_min - row2[0].skill.turn_min
    }
  }

  sort() {
    if (this.data.length == 0) return
    let config = document.querySelector('atk-eval-config').generateConfig()
    let filter = document.querySelector('card-filter').filterFunc()
    let cmp = this.compareFunction_(config.sortBy)
    let a = this.data
      .filter(filter)
      .map(c => [c, atkEval(c, config)])
      .sort(cmp)
      .slice(0, config.maxResult)

    let filter_result = document.querySelector('filter-result')
    filter_result.data = a
  }
}

export const database = new Database();
