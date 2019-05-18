import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterOrbChange extends FilterBase {
  static get properties() {
    return {
      from_: {type: Array},
      to: {type: Array},
    };
  }

  constructor() {
    super();
    this.from_ = [];
    this.from_[9] = false;
    this.to = [];
    this.to[9] = false;
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
    })
  }

  render() {
    return html`
      ${this.commonCss}
      <orb-selection value="${bind(this, 'from_')}" mode="orb">
      </orb-selection>
      <span class="material-icons" style="font-size: 16px">keyboard_arrow_right</span>
      <orb-selection value="${bind(this, 'to')}" mode="orb">
      </orb-selection>
    `;
  }
}
customElements.define('filter-orb-change', FilterOrbChange);

