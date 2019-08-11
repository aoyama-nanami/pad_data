import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {statAtMaxLv, icon} from './common.js';

const RESULTS_PER_PAGE = 30;

class FilterResult extends LitElement {
  static get properties() {
    return {
      data: {type: Array},
      page: {type: Number},
    };
  }

  set data(newValue) {
    const oldValue = this.data;
    this._data = newValue;
    this.page = 1;
    this.requestUpdate('data', oldValue);
  }

  get data() {
    return this._data;
  }

  get maxPage() {
    const data = this.data;
    return data ? Math.ceil(data.length / RESULTS_PER_PAGE) : 1;
  }

  set page(newValue) {
    const oldValue = this.page;
    const sanitizedValue = Math.min(this.maxPage, Math.max(newValue, 1));
    this._page = sanitizedValue;
    this.requestUpdate('page', oldValue);
  }

  get page() {
    return this._page;
  }

  static get styles() {
    return [
      css`
        :host {
          display: grid;
          grid-template-columns: var(--grid-columns);
          line-height: 24px;
        }

        .grid-row {
          display: contents;
        }

        .grid-row:hover .grid-cell {
          background-color: rgba(161, 194, 250, 0.2);
        }

        .grid-cell {
          padding: 3px 3px 0 3px;
          height: 54px;
          display: inline-block;
          vertical-align: baseline;
          border-bottom: 1px solid rgb(85, 85, 85);
          border-top: 1px solid rgb(85, 85, 85);
        }

        .grid-cell:first-child {
          padding-left: 9px;
        }

        .numeric-cell {
          font-family: Roboto;
          text-align: right;
          padding-left: 5px;
          padding-right: 5px;
        }

        .skill-desc {
          grid-column-end: span 8;
          padding-left: var(--skill-desc-padding-left, inherit);
          border-bottom: var(--skill-desc-border-bottom, inherit) !important;
        }

        .skill-desc > pre {
          font-family: inherit;
          font-size: inherit;
          display: inline;
          vertical-align: middle;
          padding-top: 3px;
        }

        .two-row-icons {
          display: flex;
          flex-direction: column;
        }

        .pagination {
          padding-top: 3px;
          padding-left: 9px;
          line-height: 24px;
          grid-column: 1 / -1;
        }

        .pagination > button {
          font-size: 1rem;
          padding: 0;
          border: none;
          background: none;
          vertical-align: middle;
        }
      `,
    ];
  }

  render() {
    if (this.data) {
      const page = this.page;
      const begin = (page - 1) * RESULTS_PER_PAGE;
      const data = this.data.slice(begin, begin + RESULTS_PER_PAGE);
      return html`
        <link rel="stylesheet" type="text/css" href="css/base.css">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
              rel="stylesheet">
        ${this._paginationSection()}
        ${data.map((x) => this._renderRow(x))}
      `;
    }
    return html``;
  }

  _paginationSection() {
    return html`
      <div class="pagination">
        <button @click="${() => this.page = 1}">
          <span class="material-icons">first_page</span>
        </button>
        <button @click="${() => this.page--}">
          <span class="material-icons">chevron_left</span>
        </button>
        ${this.page} / ${this.maxPage}
        <button @click="${() => this.page++}">
          <span class="material-icons">chevron_right</span>
        </button>
        <button @click="${() => this.page = 1000000}">
          <span class="material-icons">last_page</span>
        </button>
      </div>`
  }

  _renderRow(row) {
    const [card, result] = row;
    return html`
      <a class="grid-row" href="http://pad.skyozora.com/pets/${card.card_id}"
         target="_blank">
        <div class="grid-cell two-row-icons">
          <div class="icon-list" style="margin-bottom: 3px">
            ${icon('orb' + card.attr_id)}
            ${icon('orb' + card.sub_attr_id)}
            ${icon('')}
          </div>
          <div class="icon-list">
            ${card.type.map((i) => icon('t' + i))}
          </div>
        </div>
        <div class="grid-cell">${card.name}</div>
        <div class="grid-cell numeric-cell">${result.hp}</div>
        <div class="grid-cell numeric-cell">${result.atk}</div>
        <div class="grid-cell numeric-cell">${result.rcv}</div>
        <div class="grid-cell two-row-icons"">
          <div class="icon-list" style="margin-bottom: 3px">
            ${card.awakenings.map((a) => icon('a' + a))}
          </div>
          <div class="icon-list">
            ${card.super_awakenings.map(
              (a, i) => {
                const grayscale = (i == result.superAwakeningIndex) ? undefined : 'grayscale';
                return icon('a' + a, grayscale);
              })}
          </div>
        </div>
        <div class="grid-cell numeric-cell">${card.skill.turn_min}</div>
        <div class="grid-cell">
          <div class="material-icons"
            style="font-size: 1rem">
            ${card.inheritable ? 'check' : ''}
          </div>
        </div>
        <div class="grid-cell skill-desc">
          <pre>${card.skill.description}</pre>
        </div>
      </a>
    `;
  }
}
customElements.define('filter-result', FilterResult);

