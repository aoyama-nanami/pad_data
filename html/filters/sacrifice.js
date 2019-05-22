import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterSacrifice extends FilterBase {
  static get properties() {
    return {
      hp_reduce: {type: Number},
    };
  }

  constructor() {
    super();
    this.hp_reduce = 0;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'AtkNuke' && type != 'Sacrifice') {
        return false;
      }
      if (effect.hp_remain == 100) {
        return false;
      }
      return effect.hp_remain <= 100 - this.hp_reduce;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      &ge;
      <input type="number" min="0" step="10" style="width: 40px"
             .value="${bind(this, 'hp_reduce')}"> %
    `;
  }
}
customElements.define('filter-sacrifice', FilterSacrifice);
