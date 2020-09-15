import {html} from '../util/external_lib.js';
import {bind} from '../util/bind.js';
import {Awakening} from '../util/awakening.js';
import {FilterBase} from './base.js';

export class FilterAwakening extends FilterBase {
  static get properties() {
    return {
      awakenings: {type: Array},
      count: {type: Number},
      canEdit: {type: Boolean},
    };
  }

  constructor() {
    super();
    this.count = 1;
  }

  countAwakening(a) {
    for (const [awakening, value] of this.awakenings) {
      if (a == awakening) {
        return value;
      }
    }
    return 0;
  }

  render() {
    return html`
      ${this.commonCss}
      <span style="${this.canEdit ? '' : 'display: none'}">
        &ge;
        <input type="number" min="1" step="1" .value="${bind(this, 'count')}"
               maxlength="2" style="width: 40px;">
      </span>
    `;
  }

  apply(c, i) {
    let val = 0;
    val += c.awakenings.reduce((x, a) => x + this.countAwakening(a), 0);
    if (typeof i == 'number') {
      val += this.countAwakening(c.super_awakenings[i]);
    }
    return val >= this.count;
  }
}
customElements.define('filter-awakening', FilterAwakening);

