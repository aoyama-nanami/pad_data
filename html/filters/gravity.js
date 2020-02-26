import {html} from '../util/external_lib.js';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterGravity extends FilterBase {
  static get properties() {
    return {
      percentage: {type: Number},
      trueGravity: {type: Boolean},
    };
  }

  constructor() {
    super();
    this.percentage = 0;
    this.trueGravity = false;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (this.trueGravity) {
        if (type != 'TrueGravity') {
          return false;
        }
      } else {
        if (type != 'Gravity') {
          return false;
        }
      }
      return effect.percentage >= this.percentage;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      &ge;
      <input type="number" min="0" step="5" style="width: 50px"
             .value="${bind(this, 'percentage')}"> %
    `;
  }
}
customElements.define('filter-gravity', FilterGravity);
