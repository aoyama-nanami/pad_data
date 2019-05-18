import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterNuke extends FilterBase {
  static get properties() {
    return {
      percentage: {type: Number},
      element: {type: Number},
      target: {type: Number},
      selfDamage: {type: Number},
      leech: {type: Number},
    };
  }

  constructor() {
    super();
    this.percentage = 0;
    this.element = -2;
    this.target = -1;
    this.leech = 0;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'AtkNuke') {
        return false;
      }
      if (effect.value > 0) { // 固傷
        return false;
      }

      if (effect.percentage[0] < this.percentage * 100) {
        return false;
      }
      if (this.element >= -1 && effect.element != this.element) {
        return false;
      }
      if (this.target >= 0 && effect.target != this.target) {
        return false;
      }
      if (effect.leech < this.leech) {
        return false;
      }
      return true;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      &ge;
      <input type="number" min="0" step="5" style="width: 40px"
             .value="${bind(this, 'percentage')}"> 倍,
      屬性:
      <select .value="${bind(this, 'element')}">
        <option value="-2">不限</option>
        <option value="-1">無</option>
        <option value="0">火</option>
        <option value="1">水</option>
        <option value="2">木</option>
        <option value="3">光</option>
        <option value="4">暗</option>
      </select>,
      單/全體:
      <select .value="${bind(this, 'target')}">
        <option value="-1">不限</option>
        <option value="0">全體</option>
        <option value="1">單體</option>
      </select>,
      吸血:
      <input type="number" min="0" step="5" style="width: 40px"
             .value="${bind(this, 'leech')}"> %
    `;
  }
}
customElements.define('filter-nuke', FilterNuke);
