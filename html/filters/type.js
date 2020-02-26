import {html} from '../util/external_lib.js';
import {FilterBase} from './base.js';
import {bind} from '../util/bind.js';
import {Type} from '../util/type.js';

export class FilterType extends FilterBase {
  static get properties() {
    return {
      types: {type: Array},
    };
  }

  constructor() {
    super();
    this.types = [];
    Object.keys(Type).forEach((k) => this.types[Type[k]] = false);
  }

  apply(c) {
    if (this.types.every((x) => !x)) {
      return true;
    }

    return this.types.some((v, i) => v && c.type.includes(i));
  }

  render() {
    return html`
      ${this.commonCss}
      <div class="icon-list">
        ${this.types.map((v, i) =>
          html`
            <icon-checkbox icon="t${i}" ?checked="${bind(this, 'types', i)}">
            </icon-checkbox>`
        )}
      </div>`;
  }
}
customElements.define('filter-type', FilterType);

