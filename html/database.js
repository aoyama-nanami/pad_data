import {atkEval} from './common.js';

class Database {
  constructor() {
    this.loadDatabase();
    this.data = [];
  }

  loadDatabase() {
    fetch('data/jp_cards_merged.json')
        .then((r) => r.json())
        .then((obj) => {
          const a = [];
          obj.forEach((c) => a[c.card_id] = c);
          this.data = a;
          this.sort();
          document.querySelector('#loading').style.display = 'none';
          document.querySelector('#main').style.display = 'grid';
        });
  }

  card(i) {
    return this.data[i];
  }

  compareFunction_(sortBy) {
    if (sortBy == 'atk') {
      return (row1, row2) => row2[1].atk - row1[1].atk;
    } else if (sortBy == 'cd') {
      return (row1, row2) => row1[0].skill.turn_min - row2[0].skill.turn_min;
    }
  }

  sort() {
    if (this.data.length == 0) return;
    const config = document.querySelector('atk-eval-config').generateConfig();
    const filter = document.querySelector('card-filter').filterFunc();
    const cmp = this.compareFunction_(config.sortBy);
    const a = this.data
        .filter(filter)
        .map((c) => [c, atkEval(c, config)])
        .sort(cmp)
        .slice(0, config.maxResult);

    const filterResult = document.querySelector('filter-result');
    filterResult.data = a;
  }
}

export const database = new Database();
