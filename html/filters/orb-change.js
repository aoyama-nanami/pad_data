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

    if (this.elements.every((x) => !x)) {
      return true;
    }
    if (this.main && this.elements[c.attr_id]) {
      return true;
    }
    if (this.sub && this.elements[c.sub_attr_id]) {
      return true;
    }
    return false;
  }

  render() {
    return html`
      ${this.commonCss}
      <orb-selection value="${bind(this, 'from_')}" multi mode="orb"></orb-selection>
      <span class="material-icons">keyboard_arrow_right</span>
      <orb-selection value="${bind(this, 'to')}" multi mode="orb"></orb-selection>
    `;
  }
}
customElements.define('filter-orb-change', FilterOrbChange);

