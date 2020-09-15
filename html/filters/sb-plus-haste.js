import {html} from '../util/external_lib.js';
import {bind} from '../util/bind.js';
import {Awakening} from '../util/awakening.js';
import {FilterBase} from './base.js';

export class FilterSBPlusHaste extends FilterBase {
  static get properties() {
    return {
      count: {type: Number},
    };
  }

  constructor() {
    super();
    this.count = 1;
  }

  countAwakening(a) {
    if (a == Awakening.SKILL_BOOST) {
      return 1;
    }
    if (a == Awakening.SKILL_BOOST_PLUS) {
      return 2;
    }
    return 0;
  }

  render() {
    return html`
      ${this.commonCss}
      &ge;
      <input type="number" min="1" step="1" .value="${bind(this, 'count')}"
             maxlength="2" style="width: 40px;">
    `;
  }

  apply(c, i) {
    let val = 0;
    val += c.awakenings.reduce((x, a) => x + this.countAwakening(a), 0);
    if (typeof i == 'number') {
      val += this.countAwakening(c.super_awakenings[i]);
    }
    for (const [type, effect] of c.skill.effects) {
      if (type == 'ReduceCooldown') {
        val += effect.turn[0];
      }
    }
    return val >= this.count;
  }
}
customElements.define('filter-sb-plus-haste', FilterSBPlusHaste);
