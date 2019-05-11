import {html, LitElement} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {bind} from '../util/bind.js';

class OrbSelection extends LitElement {
  static get properties() {
    return {
      value: {type: Array},
      mode: {type: String}, // "element" (default) or "orb"
    }
  }

  constructor() {
    super();
    this.mode = 'element';
    this.value = [];
    if (this.mode == 'orb') {
      this.value[9] = false;
    } else {
      this.value[4] = false;
    }
  }

  orbCheckbox_(i) {
    return html`<element-checkbox
        elementId="${i}"
        ?checked="${bind(this, 'value', i)}"
        >
      </element-checkbox>`
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      ${this.value.map((_, i) => this.orbCheckbox_(i))}`;
  }

  triggerChange() {
    this.dispatchEvent(new CustomEvent('change'))
  }
};
customElements.define('orb-selection', OrbSelection);
