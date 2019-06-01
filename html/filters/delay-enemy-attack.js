import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterDelayEnemyAttack extends FilterBase {
  static get properties() {
    return {
      duration: {type: Number},
    };
  }

  constructor() {
    super();
    this.duration = 1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      return type == 'DelayEnemyAttack' && effect.duration >= this.duration;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      <input type="number" min="1" step="1" max="5" style="width: 40px"
             .value="${bind(this, 'duration')}"> 回合
    `;
  }
}
customElements.define('filter-delay-enemy-attack', FilterDelayEnemyAttack);
