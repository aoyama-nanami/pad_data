import {html} from '../util/external_lib.js';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterRandomOrbSpawn extends FilterBase {
  static get properties() {
    return {
      orbs: {type: Array},
      count: {type: Number},
    };
  }

  constructor() {
    super();
    this.orbs = [];
    this.orbs[9] = false;
    this.count = 1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'RandomOrbSpawn') {
        return false;
      }

      if (this.orbs.some((o, i) => o && !effect.orb.includes(i))) {
        return false;
      }

      return effect.count >= this.count;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      包含
      <orb-selection value="${bind(this, 'orbs')}" mode="orb">
      </orb-selection>
      , &ge;
      <input style="width: 40px" type="number" min="1" max="842" step="1"
             .value="${bind(this, 'count')}"
             maxlength="2">
      顆
    `;
  }
}
customElements.define('filter-random-orb-spawn', FilterRandomOrbSpawn);

