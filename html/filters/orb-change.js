import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';
import {Orb} from '../util/orb.js';

export class FilterOrbChange extends FilterBase {
  static get properties() {
    return {
      from_: {type: Array},
      to: {type: Array},
    };
  }

  constructor() {
    super();
    this.from_ = new Array(Orb.BOMB + 1);
    this.to = new Array(Orb.BOMB + 1);
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'OrbChange') {
        return false;
      }

      if (this.from_.some((x) => x)) {
        if (effect.from_.some((x) => !this.from_[x])) {
          return false;
        }
      }

      if (this.to.some((x) => x)) {
        if (effect.to.some((x) => !this.to[x])) {
          return false;
        }
      }

      return true;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      <orb-selection value="${bind(this, 'from_')}" mode="orb"></orb-selection>
      <span class="material-icons" style="font-size: 1rem">
        keyboard_arrow_right
      </span>
      <orb-selection value="${bind(this, 'to')}" mode="orb"></orb-selection>
    `;
  }
}
customElements.define('filter-orb-change', FilterOrbChange);

