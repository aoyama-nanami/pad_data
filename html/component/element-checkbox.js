import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {icon} from '../common.js';

class ElementCheckbox extends LitElement {
  static get properties() {
    return {
      elementId: {type: Number},
      checked: {type: Boolean},
    };
  }

  static get styles() {
    return css`
      :host {
        font-size: 0;
        vertical-align: middle;
      }
    `;
  }

  onChange_(ev) {
    this.checked = ev.target.checked;
    this.dispatchEvent(new CustomEvent('change'));
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <label class="icon-checkbox pointer">
        <input type="checkbox"
               ?checked="${this.checked}"
               ?disabled="${this.override}"
               @change="${(ev) => this.onChange_(ev)}"
               >
        ${icon('orb', this.elementId)}
      </label>`;
  }
}
customElements.define('element-checkbox', ElementCheckbox);
