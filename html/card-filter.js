import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {Awakening} from './util/awakening.js';
import {bind} from './util/bind.js';
import {database} from './database.js';
import {toggleCheckbox} from './component/checkbox.js';

import {FilterById} from './component/filter-dropdown.js';

class CardFilter extends LitElement {
  static get properties() {
    return {
      filters: {type: Array},
      /* Force enabled filter of void damage piercer.
       * TODO: redesign this */
      overrideFilter: {type: Boolean},
    };
  }

  static get styles() {
    return [
      css`
        .grid {
          display: grid;
          grid-template-columns: 22px 30px max-content auto;
          grid-auto-rows: 28px;
          line-height: 24px;
        }

        .grid-cell {
          padding: 3px 3px 0 3px;
          display: inline-block;
          vertical-align: baseline;
          border-bottom: 1px solid rgb(85, 85, 85);
        }

        .remove-btn {
          font-size: 0.8rem;
        }

        option[disabled] {
          background-color: #333333;
        }
      `,
    ];
  }

  constructor() {
    super();
    this.filters = [];
    this.newFilter_();
    this.overrideFilter = false;
  }

  filterFunc() {
    const elems = Array.from(
        this.shadowRoot.querySelectorAll('.filter.enabled'));
    return (card) => elems.every((e) => e.apply(card));
  }

  createFilter(id, args, i, enabled) {
    const spec = FilterById(id);
    const Cls = spec.cls
    if (!Cls) {
      return html``;
    }

    args = args || spec.init || {};
    const filter = new Cls();
    Object.keys(args).forEach((k) => filter[k] = args[k]);
    filter.classList.add('filter');
    filter.classList.add(enabled ? 'enabled' : 'disabled');
    filter.addEventListener('change', (ev) => this.updateFilter_(ev, i));
    return filter;
  }

  newFilter_() {
    this.filters.push({});
    this.requestUpdate();
  }

  deleteFilter_(i) {
    this.filters.splice(i, 1);
    this.requestUpdate();
  }

  changeFilterId_(i, ev) {
    const id = ev.target.value;
    if (this.filters[i].id == id) {
      return;
    }
    this.filters[i] = {id: id, enabled: !!id};
    if (i == this.filters.length - 1 && id) {
      this.newFilter_();
    }
    this.requestUpdate();
  }

  updateFilter_(ev, i) {
    this.filters[i].args = ev.target.value;
    this.requestUpdate();
  }

  renderFilterRow_(row, i) {
    let {id, args, enabled} = row;

    return html`
      <div class="grid-cell">
        <span @click="${() => this.deleteFilter_(i)}"
              class="material-icons pointer remove-btn"
              style="${id ? '' : 'display: none'}"
              title="remove">
          remove_circle_outline
        </span>
      </div>
      <div class="grid-cell">
        ${id ? toggleCheckbox('', bind(this, 'filters', i, 'enabled')) : ''}
      </div>
      <div class="grid-cell">
        <filter-dropdown
          .value="${id}"
          @change="${(ev) => this.changeFilterId_(i, ev)}">
        </filter-dropdown>
      </div>
      <div class="grid-cell">
        ${this.createFilter(id, args, i, enabled)}
      </div>
    `;
  }

  renderForcedFilter_() {
    if (!this.overrideFilter) {
      return '';
    }

    const v = '無效貫通';
    return html`
      <div class="grid-cell">
      </div>
      <div class="grid-cell">
      </div>
      <div class="grid-cell">
        無效貫通
      </div>
      <div class="grid-cell">
        ${this.createFilter(v, FilterById(v).init, -1, true)}
      </div>
    `;
  }

  updated() {
    super.updated();
    database.sort();
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="css/base.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      <div class="card-title">Filter</div>
      <div class="card-body">
        <div class="grid">
          ${this.filters.map((row, i) => this.renderFilterRow_(row, i))}
          ${this.renderForcedFilter_()}
        </div>
      </div>
    `;
  }
}
customElements.define('card-filter', CardFilter);

