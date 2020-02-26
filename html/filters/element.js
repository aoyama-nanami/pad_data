import {html} from '../util/external_lib.js';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';

export class FilterElement extends FilterBase {
  static get properties() {
    return {
      elements: {type: Array},
      main: {type: Boolean},
      sub: {type: Boolean},
    };
  }

  constructor() {
    super();
    this.elements = [];
    this.elements[4] = false;
  }

  apply(c) {
    if (this.elements.every((x) => !x)) {
      return true;
    }
    if (this.main && this.elements[c.attr_id]) {
      return true;
    }
    if (this.sub && this.elements[c.sub_attr_id]) {
      return true;
    }
    return false;
  }

  render() {
    return html`
      ${this.commonCss}
      <orb-selection value="${bind(this, 'elements')}" multi></orb-selection>
    `;
  }
}
customElements.define('filter-element', FilterElement);

