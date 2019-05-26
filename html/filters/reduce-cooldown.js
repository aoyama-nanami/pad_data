import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterReduceCooldown extends FilterBase {
  static get properties() {
    return {
      turn: {type: Number},
    };
  }

  constructor() {
    super();
    this.turn = 1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      return type == 'ReduceCooldown' && effect.turn[0] >= this.turn;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      <input type="number" min="1" step="1" style="width: 40px"
             .value="${bind(this, 'turn')}"> 回合
    `;
  }
}
customElements.define('filter-reduce-cooldown', FilterReduceCooldown);
