import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {FilterBase} from './base.js';

export class FilterAssist extends FilterBase {
  static get properties() {
    return {};
  }

  render() {
    return '';
  }

  apply(c) {
    return c.inheritable;
  }
}
customElements.define('filter-assist', FilterAssist);

