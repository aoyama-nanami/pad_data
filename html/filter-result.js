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
        .grid {
          display: grid;
          min-width: 100%;
          width: max-content;
          grid-template-columns: var(--grid-columns);
          grid-template-rows: var(--grid-rows);
          grid-template-areas: var(--grid-areas);
          border-bottom: 1px solid rgb(85, 85, 85);
        }

        .result-row {
          display: contents;
        }

        .result-row:hover > .grid {
          background-color: rgba(161, 194, 250, 0.2);
        }

        .grid-cell {
          padding: 3px 3px 0 3px;
          display: inline-block;
          vertical-align: baseline;
        }

        .numeric-cell {
          font-family: Roboto;
          text-align: right;
          padding-left: 5px;
          padding-right: 5px;
        }

        .grid-cell#elem {
          grid-area: elem;
          padding-left: 9px;
        }

        .grid-cell#type {
          grid-area: type;
          padding-left: 9px;
        }

        .grid-cell#hp {
          grid-area: hp;
        }

        .grid-cell#atk {
          grid-area: atk;
        }

        .grid-cell#rcv{
          grid-area: rcv;
        }

        .grid-cell#name {
          grid-area: name;
          overflow: hidden;
        }

        .grid-cell#awakenings {
          grid-area: aw;
        }

        .grid-cell#super-awakenings {
          grid-area: sa;
        }

        .grid-cell#turn-min {
          grid-area: turn;
        }

        .grid-cell#inheritable {
          grid-area: inh;
          text-align: middle;
        }

        .grid-cell#skill-desc {
          grid-area: sk;
        }

        .grid-cell#skill-desc > pre {
          font-family: inherit;
          font-size: inherit;
          display: inline;
          vertical-align: middle;
          padding-top: 3px;
        }

        .pagination {
          padding-top: 3px;
          padding-left: 9px;
          border-bottom: 1px solid rgb(85, 85, 85);
        }

        .pagination > button {
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
        ${this._paginationSection()}
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
      <a href="http://pad.skyozora.com/pets/${card.card_id}" target="_blank" class="result-row">
        <div class="grid">
          <div class="grid-cell icon-list" id="elem" style="margin-bottom: 3px">
            ${icon('orb' + card.attr_id)}
            ${icon('orb' + card.sub_attr_id)}
            ${icon('')}
          </div>
          <div class="grid-cell icon-list" id="type">
            ${card.type.map((i) => icon('t' + i))}
          </div>
          <div class="grid-cell" id="name">${card.name}</div>
          <div class="grid-cell numeric-cell" id="hp">${result.hp}</div>
          <div class="grid-cell numeric-cell" id="atk">${result.atk}</div>
          <div class="grid-cell numeric-cell" id="rcv">${result.rcv}</div>
          <div class="grid-cell icon-list" id="awakenings" style="margin-bottom: 3px">
            ${card.awakenings.map((a) => icon('a' + a))}
          </div>
          <div class="grid-cell icon-list" id="super-awakenings">
            ${card.super_awakenings.map(
              (a, i) => {
                const grayscale = (i == result.superAwakeningIndex) ? undefined : 'grayscale';
                return icon('a' + a, grayscale);
              })}
          </div>
          <div class="grid-cell numeric-cell" id="turn-min">${card.skill.turn_min}</div>
          <div class="grid-cell" id="inheritable">
            <div class="material-icons"
              style="font-size: 1rem">
              ${card.inheritable ? 'check' : ''}
            </div>
          </div>
          <div class="grid-cell" id="skill-desc">
            <pre>${card.skill.description}</pre>
          </div>
        </div>
      </a>
    `;
  }
}
customElements.define('filter-result', FilterResult);

