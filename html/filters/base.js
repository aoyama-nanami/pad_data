import {LitElement, html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {database} from '../database.js';

export class FilterBase extends LitElement {
  updated() {
    super.updated();
    database.sort();
  }

  triggerChange() {
    this.dispatchEvent(new CustomEvent('change'))
  }

  get commonCss() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      `;
  }

  get value() {
    let v = {};
    let properties = this.constructor.properties;
    Object.keys(properties).forEach(k => v[k] = this[k]);
    return v;
  }
}


