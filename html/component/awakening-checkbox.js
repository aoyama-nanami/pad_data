import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {assetsToIconCss} from '../common.js';

class AwakeningCheckbox extends LitElement {
  static get properties() {
    return {
      awakeningId: {type: Number},
      checked: {type: Boolean},
      override: {type: Boolean},
      overrideChecked: {type: Boolean},
    };
  }

  static get styles() {
    return [
      assetsToIconCss(),
    ];
  }

  onChange_(ev) {
    this.checked = ev.target.checked;
    this.dispatchEvent(new CustomEvent('change'));
  }

  render() {
    let value = this.override ? this.overrideChecked : this.checked;
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <label class="icon-checkbox">
        <input type="checkbox"
               ?checked="${value}"
               ?disabled="${this.override}"
               @change="${(ev) => this.onChange_(ev)}"
               >
        <div class="awakening-${this.awakeningId}"></div>
      </label>`;
  }
}
customElements.define('awakening-checkbox', AwakeningCheckbox);
