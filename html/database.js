import {statEval} from './common.js';

class Database {
  constructor() {
    this.loadDatabase();
    this.data = [];
  }

  loadDatabase() {
    fetch('data/jp_cards_merged.json')
        .then((r) => r.json())
        .then((obj) => {
          obj.forEach((c) => this.data[c.card_id] = c);
          this.sort();
          document.querySelector('#loading').style.display = 'none';
          document.querySelector('#main').style.removeProperty('display');
        });
  }

  card(i) {
    return this.data[i];
  }

  compareFunction_(sortBy) {
    switch (sortBy) {
      case 'hp':
      case 'atk':
      case 'rcv':
        return (row1, row2) => row2[1][sortBy] - row1[1][sortBy];
      case 'cd':
        return (row1, row2) => {
          if (row1[0].skill.turn_min == 0) {  // no skill
            return 1;
          }
          return row1[0].skill.turn_min - row2[0].skill.turn_min;
        };
    }
  }

  sort() {
    if (this.data.length == 0) return;
    const config = document.querySelector('atk-eval-config').generateConfig();
    const filter = document.querySelector('card-filter').filterFunc();
    const cmp = this.compareFunction_(config.sortBy);
    const a = this.data
        .filter(filter)
        .map((c) => [c, statEval(c, config)])
        .sort(cmp);

    const filterResult = document.querySelector('filter-result');
    filterResult.data = a;
  }
}

export const database = new Database();
