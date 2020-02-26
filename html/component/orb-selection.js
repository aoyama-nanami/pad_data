import {html, LitElement} from '../util/external_lib.js';
import {bind} from '../util/bind.js';
import {Orb} from '../util/orb.js';

class OrbSelection extends LitElement {
  static get properties() {
    return {
      value: {type: Array},
      mode: {type: String}, // "element" (default) or "orb"
    };
  }

  constructor() {
    super();
    this.mode = 'element';
    if (this.mode == 'orb') {
      this.value = new Array(Orb.BOMB + 1);
    } else {
      this.value = new Array(Orb.DARK + 1);
    }
  }

  orbCheckbox_(i) {
    return html`
      <icon-checkbox
        icon="orb${i}" ?checked="${bind(this, 'value', i)}">
      </icon-checkbox>`;
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="css/base.css">
      <div class="icon-list">
        ${this.value.map((_, i) => this.orbCheckbox_(i))}
      </div>`;
  }

  triggerChange() {
    this.dispatchEvent(new CustomEvent('change'));
  }
};
customElements.define('orb-selection', OrbSelection);
