import {html} from '../util/external_lib.js';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterFixedValueNuke extends FilterBase {
  static get properties() {
    return {
      val: {type: Number},
      element: {type: Number},
      target: {type: Number},
      ignoreDef: {type: Number},
    };
  }

  constructor() {
    super();
    /* this.value is used by FilterBase, use this.val here */
    this.val = 0;
    this.element = -2;
    this.target = -1;
    this.ignoreDef = -1;
  }

  apply(c) {
    return c.skill.effects.some(([type, effect]) => {
      if (type != 'AtkNuke' && type != 'AtkNukeType2') {
        return false;
      }
      if (effect.percentage[0] > 0) {
        return false;
      }

      if (effect.value * effect.repeat < this.val) {
        return false;
      }
      if (this.element >= -1 && effect.element != this.element) {
        return false;
      }
      if (this.target >= 0 && effect.target != this.target) {
        return false;
      }
      if (this.ignoreDef >= 0) {
        return this.ignoreDef == 0 ? !effect.ignore_def : effect.ignore_def;
      }
      return true;
    });
  }

  render() {
    return html`
      ${this.commonCss}
      &ge;
      <input type="number" min="0" style="width: 60px"
             .value="${bind(this, 'val')}"> 點傷害,
      屬性:
      <select .value="${bind(this, 'element')}">
        <option value="-2">不限</option>
        <option value="-1">無</option>
        <option value="0">火</option>
        <option value="1">水</option>
        <option value="2">木</option>
        <option value="3">光</option>
        <option value="4">暗</option>
      </select>,
      單/全體:
      <select .value="${bind(this, 'target')}">
        <option value="-1">不限</option>
        <option value="0">全體</option>
        <option value="1">單體</option>
      </select>,
      無視防禦:
      <select .value="${bind(this, 'ignoreDef')}">
        <option value="-1">不限</option>
        <option value="0">否</option>
        <option value="1">是</option>
      </select>,
    `;
  }
}
customElements.define('filter-fixed-value-nuke', FilterFixedValueNuke);
