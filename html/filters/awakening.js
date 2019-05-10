import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {bind} from '../util/bind.js';
import {Awakening} from '../awakening.js';
import {FilterBase} from '../card-filter.js';

class FilterAwakening extends FilterBase {
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
               @click="${(e) => e.target.select()}"
               maxlength="2" style="width: 40px;">
      </span>
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
    return val >= this.count;
  }
}
customElements.define('filter-awakening', FilterAwakening);

