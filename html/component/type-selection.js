import {html, LitElement} from '../util/external_lib.js';
import {bind} from '../util/bind.js';
import {Type} from '../util/type.js';

const _TYPE_IDS = Object.keys(Type)
  .map((k) => Type[k])
  .filter((k) => k != Type.EVOLVE_MATERIAL && k < Type.AWAKEN_MATERIAL)
  .sort();

class TypeSelection extends LitElement {
  static get properties() {
    return {
      value: {type: Array},
    };
  }

  constructor() {
    super();
    this.value = [];
  }

  typeCheckbox_(i) {
    return html`
      <icon-checkbox icon="t${i}"
        ?checked="${bind(this, 'value', i)}">
      </icon-checkbox>`;
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="css/base.css">
      <div class="icon-list">
        ${_TYPE_IDS.map((i) => this.typeCheckbox_(i))}
      </div>`;
  }

  triggerChange() {
    this.dispatchEvent(new CustomEvent('change'));
  }
};
customElements.define('type-selection', TypeSelection);
