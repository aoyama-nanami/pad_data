import {LitElement, html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';

export class FilterBase extends LitElement {
  triggerChange() {
    this.dispatchEvent(new CustomEvent('change'));
  }

  get commonCss() {
    return html`
      <link rel="stylesheet" type="text/css" href="css/base.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      `;
  }

  firstUpdated() {
    super.firstUpdated();
    this.shadowRoot.querySelectorAll('input[type=number]').forEach(
        (e) => e.addEventListener('focus', (ev) => ev.target.select()));
  }

  get value() {
    const v = {};
    const properties = this.constructor.properties;
    Object.keys(properties).forEach((k) => v[k] = this[k]);
    return v;
  }
}

