import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {bind} from '../util/bind.js';
import {FilterBase} from './base.js';

export class FilterRarity extends FilterBase {
  static get properties() {
    return {
      op: {type: String},
      rarity: {type: Number},
    };
  }

  constructor() {
    super();
    this.op = '>=';
    this.rarity = 1;
  }

  render() {
    return html`
      ${this.commonCss}
      <select .value="${bind(this, 'op')}" data-type="string">
        <option value="<=">&le;</option>
        <option value=">=">&ge;</option>
      </select>
      <input style="width: 40px" type="number" min="1" step="1" max="10"
             .value="${bind(this, 'rarity')}"
             maxlength="2">
    `;
  }

  apply(c) {
    if (this.op == '<=') {
      return c.rarity <= this.rarity;
    } else if (this.op == '>=') {
      return c.rarity >= this.rarity;
    }
    throw new Error(`invalid op: ${this.op}`);
  }
}
customElements.define('filter-rarity', FilterRarity);
