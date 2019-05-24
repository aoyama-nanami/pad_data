import {html, LitElement} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {bind} from '../util/bind.js';
import {Type} from '../util/type.js';

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
    return html`<icon-checkbox
        icon="t${i}"
        ?checked="${bind(this, 'value', i)}"
        >
      </icon-checkbox>`;
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <div class="icon-list">
        ${[...Array(Type.MACHINE + 1).keys()]
            .filter((i) => i != Type.EVOLVE_MATERIAL)
            .map((i) => this.typeCheckbox_(i))}
      </div>`;
  }

  triggerChange() {
    this.dispatchEvent(new CustomEvent('change'));
  }
};
customElements.define('type-selection', TypeSelection);
