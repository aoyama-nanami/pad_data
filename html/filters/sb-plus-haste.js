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

  get multi() {
    const e = document.querySelector('atk-eval-config');
    return e.awakenings[Awakening.MULTI_BOOST];
  }

  apply(c) {
    let val = 0;
    val += c.awakenings.reduce((x, a) => x + this.countAwakening(a), 0);
    if (!this.multi) {
      val += c.super_awakenings.reduce((x, a) => x + this.countAwakening(a), 0);
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
