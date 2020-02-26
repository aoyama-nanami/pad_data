import {html} from '../util/external_lib.js';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterBindRecovery extends FilterBase {
  static get properties() {
    return {
      turn: {type: Number},
      awoken_bind: {type: Boolean},
    };
  }

  constructor() {
    super();
    this.turn = 1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'Heal') {
        return false;
      }

      if (this.awoken_bind) {
        return effect.awoken_bind >= this.turn;
      } else {
        return effect.bind >= this.turn;
      }
    });
  }

  render() {
    return html`
      ${this.commonCss}
      &ge;
      <input type="number" min="1" style="width: 40px"
             .value="${bind(this, 'turn')}">
      回合
    `;
  }
}
customElements.define('filter-bind-recovery', FilterBindRecovery);
