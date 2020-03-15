import {html} from '../util/external_lib.js';
import {bind} from '../util/bind.js';
import {FilterBase} from './base.js';

export class FilterCost extends FilterBase {
  static get properties() {
    return {
      op: {type: String},
      cost: {type: Number},
    };
  }

  constructor() {
    super();
    this.op = '<=';
    this.cost = 1000;
  }

  render() {
    return html`
      ${this.commonCss}
      <select .value="${bind(this, 'op')}" data-type="string">
        <option value="<=">&le;</option>
        <option value=">=">&ge;</option>
      </select>
      <input style="width: 80px" type="number" min="1"
             .value="${bind(this, 'cost')}" maxlength="5">
    `;
  }

  apply(c) {
    if (this.op == '<=') {
      return c.cost <= this.cost;
    } else if (this.op == '>=') {
      return c.cost >= this.cost;
    }
    throw new Error(`invalid op: ${this.op}`);
  }
}
customElements.define('filter-cost', FilterCost);
