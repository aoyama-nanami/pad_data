import {html} from '../util/external_lib.js';
import {bind} from '../util/bind.js';
import {FilterBase} from './base.js';

export class FilterSkillCd extends FilterBase {
  static get properties() {
    return {
      op: {type: String},
      cd: {type: Number},
    };
  }

  constructor() {
    super();
    this.op = '>=';
    this.cd = 1;
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

