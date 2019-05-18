import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterAllOrbChange extends FilterBase {
  static get properties() {
    return {
      orbs: {type: Array},
      op: {type: String},
      num_colors: {type: Number},
    };
  }

  constructor() {
    super();
    this.orbs = [];
    this.orbs[9] = false;
    this.op = '>=';
    this.num_colors = 1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      let orbs;
      if (type == 'AllOrbChange') {
        orbs = effect.orbs;
      } else if (type == 'OrbChange') {
        /*
         * This is a special case for
         * No. 4389 & 4390 双子の看守・ジュスティーヌ＆カロリーヌ,
         * Their skill is classified as orb change from 10 colors to 9 colors.
         */
        if (effect.from_.length != 10) {
          return false;
        }
        orbs = effect.to;
      } else {
        return false;
      }

      if (this.orbs.some((o, i) => o && !orbs.includes(i))) {
        return false;
      }

      switch (this.op) {
      case '<=':
        return orbs.length <= this.num_colors;
      case '==':
        return orbs.length == this.num_colors;
      case '>=':
        return orbs.length >= this.num_colors;
      }

      /* should not happen */
      return false;
    })
  }

  render() {
    return html`
      ${this.commonCss}
      <select .value="${bind(this, 'op')}" data-type="string">
        <option value="<=">&le;</option>
        <option value="==">==</option>
        <option value=">=">&ge;</option>
      </select>
      <input style="width: 40px" type="number" min="1" max="10" step="1"
             .value="${bind(this, 'num_colors')}"
             maxlength="2">
      色, 包含:
      <orb-selection value="${bind(this, 'orbs')}" mode="orb">
      </orb-selection>
    `;
  }
}
customElements.define('filter-all-orb-change', FilterAllOrbChange);

