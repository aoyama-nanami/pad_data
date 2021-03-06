import {LitElement, css, html} from '../util/external_lib.js';
import {icon} from '../common.js';

class IconCheckbox extends LitElement {
  static get properties() {
    return {
      icon: {type: String},
      checked: {type: Boolean},
      override: {type: Boolean},
      overrideChecked: {type: Boolean},
    };
  }

  static get styles() {
    return css`
      :host {
        display: inline-block;
      }

      .icon-checkbox > input {
        display: none;
      }

      label.icon-checkbox {
        display: inline-block;
      }

      .icon-checkbox > input:not(:checked) + div {
        filter: grayscale(95%);
      }

      .icon-checkbox > input:disabled + div {
        cursor: not-allowed;
      }
    `;
  }

  onChange_(ev) {
    this.checked = ev.target.checked;
    this.dispatchEvent(new CustomEvent('change'));
  }

  render() {
    const value = this.override ? this.overrideChecked : this.checked;
    return html`
      <link rel="stylesheet" type="text/css" href="css/base.css">
      <label class="icon-checkbox">
        <input type="checkbox"
               .checked="${value}"
               ?disabled="${this.override}"
               @change="${(ev) => this.onChange_(ev)}"
               >
        ${icon(this.icon)}
      </label>`;
  }
}
customElements.define('icon-checkbox', IconCheckbox);
