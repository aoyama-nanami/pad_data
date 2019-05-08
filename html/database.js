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
      })
  }

  card(i) {
    return this.data[i]
  }

  sort() {
    let config = document.querySelector('atk-eval-config').generateConfig()
    let filter = document.querySelector('card-filter')
    let a = this.data
      .filter(c => filter.apply(c))
      .map(c => [c, atkEval(c, config)])
      .sort((a1, a2) => a2[1] - a1[1])
      .slice(0, 30)

    let filter_result = document.querySelector('filter-result')
    filter_result.data = a
  }
}

export const database = new Database();
