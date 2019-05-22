import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterCombo extends FilterBase {
  static get properties() {
    return {
      duration: {type: Number},
      combo: {type: Number},
    };
  }

  constructor() {
    super();
    this.duration = 1;
    this.combo = 1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'ComboIncrease') {
        return false;
      }

      return effect.duration >= this.duration && effect.combo >= this.combo;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      <input type="number" min="1" style="width: 40px"
             .value="${bind(this, 'duration')}">
      回合內, 增加
      <input type="number" min="1" style="width: 40px"
             .value="${bind(this, 'combo')}">
      combo
    `;
  }
}
customElements.define('filter-combo', FilterCombo);
