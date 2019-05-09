import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {bind} from '../util/bind.js';
import {FilterBase} from '../card-filter.js';

class FilterSkillCd extends FilterBase {
  static get properties() {
    return {
      op: {type: Number},
      cd: {type: Number},
    };
  }

  constructor() {
    super();
    this.op = '<=';
    this.cd = 99;
  }

  render() {
    return html`
      ${this.commonCss}
      <select .value="${bind(this, 'op')}" data-type="string">
        <option value="<=">&le;</option>
        <option value=">=">&ge;</option>
      </select>
      <input style="width: 40px" type="number" min="1" step="1"
             .value="${bind(this, 'cd')}"
             @click="${(e) => e.target.select()}"
             maxlength="2">
    `;
  }

  apply(c) {
    if (this.op == '<=') {
      return c.skill.turn_min <= this.cd;
    } else if (this.op == '>=') {
      return c.skill.turn_min >= this.cd;
    }
    throw new Error(`invalid op: ${this.op}`);
  }
}
customElements.define('filter-skill-cd', FilterSkillCd);

