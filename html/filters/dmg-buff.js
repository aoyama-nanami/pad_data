import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';
import {Type} from '../util/type.js';
import {Orb} from '../util/orb.js';

export class FilterDmgBuff extends FilterBase {
  static get properties() {
    return {
      duration: {type: Number},
      condElement: {type: Array},
      condType: {type: Array},
      percentage: {type: Number},
    };
  }

  constructor() {
    super();
    this.duration = 1;
    this.condElement = [];
    this.condElement[Orb.DARK] = false;
    this.condType = [];
    this.percentage = 100;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'ElementDamageBuff' && type != 'TypeDamageBuff') {
        return false;
      }

      if (effect.duration < this.duration ||
          effect.percentage < this.percentage) {
        return false;
      }

      if (type == 'ElementDamageBuff') {
        if (effect.cond.every((o) => o >= Orb.HEART)) {
          return false;
        }
      }

      if (this.condElement.every((x) => !x) && this.condType.every((x) => !x)) {
        return true;
      }

      if (type == 'ElementDamageBuff') {
        return effect.cond.every((x) => this.condElement[x]);
      } else {
        return effect.cond.every((x) => this.condType[x]);
      }

      return true;
    })
  }

  render() {
    return html`
      ${this.commonCss}
      <input type="number" min="1" step="1" style="width: 50px"
             .value="${bind(this, 'duration')}"
             @click="${(e) => e.target.select()}">
      回合,
      <orb-selection value="${bind(this, 'condElement')}" mode="element">
      </orb-selection>
      <type-selection value="${bind(this, 'condType')}">
      </type-selection>
      <input type="number" min="100" step="50" style="width: 50px"
             .value="${bind(this, 'percentage')}"
             @click="${(e) => e.target.select()}">
      %增傷
    `;
  }
}
customElements.define('filter-dmg-buff', FilterDmgBuff);

