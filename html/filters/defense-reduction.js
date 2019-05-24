import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterDefenseReduction extends FilterBase {
  static get properties() {
    return {
      duration: {type: Number},
      percentage: {type: Number},
    };
  }

  constructor() {
    super();
    this.duration = 1;
    this.percentage = 25;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'DefenseReduction') {
        return false;
      }
      return (effect.duration >= this.duration &&
        effect.percentage >= this.percentage);
    });
  }

  render() {
    return html`
      ${this.commonCss}
      <input type="number" min="1" style="width: 40px"
             .value="${bind(this, 'duration')}">
      回合內, 減少
      <input type="number" min="25" max="100" step="25" style="width: 40px"
             .value="${bind(this, 'percentage')}">
      % 防禦
    `;
  }
}
customElements.define('filter-defense-reduction', FilterDefenseReduction);
