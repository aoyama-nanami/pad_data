import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {Awakening} from './awakening.js';
import {bind} from './util/bind.js';
import {database} from './database.js';

const FILTERS_ = [
  {
    desc: '無效貫通',
    render: () => html`
      <filter-awakening
        class="filter"
        arg="[[${Awakening.VOID_DAMAGE_PIERCER}, 1]]"
        count="1">
      </filter-awakening>`,
  },
  {
    desc: '主屬',
    render: () => html`<filter-element class="filter" main></filter-element>`,
  },
  {
    desc: '副屬',
    render: () => html`<filter-element class="filter" sub></filter-element>`,
  },
  {
    desc: '主或副屬',
    render: () => html`
      <filter-element class="filter" main sub>
      </filter-element>`,
  },
  {
    desc: '操作時間延長',
    render: () => html`
      <filter-awakening
        class="filter"
        arg="[[${Awakening.EXTEND_TIME}, 1],
              [${Awakening.EXTEND_TIME_PLUS}, 2]]"
        count="1"
        canEdit>
      </filter-awakening>`,
  },
  {
    desc: 'Skill Boost',
    render: () => html`
      <filter-awakening
        class="filter"
        arg="[[${Awakening.SKILL_BOOST}, 1],
              [${Awakening.SKILL_BOOST_PLUS}, 2]]"
        count="1"
        canEdit>
      </filter-awakening>`,
  },
  {
    desc: '技能 CD',
    render: () => html`<filter-skill-cd class="filter"></filter-skill-cd>`,
  },
  {
    desc: '大砲',
    isSkill: true,
    render: () => html`<filter-nuke class="filter"></filter-nuke>`,
  },
];

export class FilterBase extends LitElement {
  updated() {
    super.updated();
    database.sort();
  }

  get commonCss() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      `;
  }
}

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
          grid-template-columns: 20px max-content auto;
          line-height: 24px;
        }
        .grid-row {
          display: contents;
        }

        .grid-cell {
          padding: 3px 3px 0 3px;
          display: inline-block;
          vertical-align: baseline;
          border-bottom: 1px solid rgb(85, 85, 85);
        }
      `,
    ];
  }

  constructor() {
    super();
    this.filters = [];
    this.overrideFilter = false;
  }

  filterFunc() {
    const elems = Array.from(
        this.shadowRoot.querySelectorAll('.filter'));
    return (card) => elems.every((e) => e.apply(card));
  }

  newFilter_() {
    this.filters.push(-1);
    this.requestUpdate();
  }

  deleteFilter_(i) {
    this.filters.splice(i, 1);
    this.requestUpdate();
  }

  renderFilterRow_(x, i) {
    return html`
      <div class="grid-row">
        <div class="grid-cell">
          <span @click="${()=>this.deleteFilter_(i)}" class="material-icons"
                  title="remove">
            remove
          </span>
        </div>
        <div class="grid-cell">
          <select .value="${bind(this, 'filters', i)}">
            <option value="-1" disabled></option>
            ${FILTERS_.map((obj, j) =>
              obj.isSkill ? '' :
              html`<option value="${j}" .selected="${x == j}">
                     ${obj.desc}
                   </option>`)}
            <optgroup label="技能">
              ${FILTERS_.map((obj, j) =>
                !obj.isSkill ? '' :
                html`<option value="${j}" .selected="${x == j}">
                       ${obj.desc}
                     </option>`)}
            </optgroup>
          </select>
        </div>
        <div class="grid-cell">
          ${x >= 0 ? FILTERS_[x].render() : ''}
        </div>
      </div>
    `;
  }

  renderForcedFilter_() {
    if (!this.overrideFilter) {
      return '';
    }

    const v = 1;
    return html`
      <div class="grid-row">
        <div class="grid-cell">
        </div>
        <div class="grid-cell">
          <select>
            <option value="${v}" selected disabled>${FILTERS_[v].desc}</option>
          </select>
        </div>
        <div class="grid-cell">
          ${FILTERS_[v].render()}
        </div>
      </div>
    `;
  }

  updated() {
    super.updated();
    if (this.filters.length == 0 ||
        this.filters[this.filters.length - 1] != -1) {
      this.newFilter_();
    }
    database.sort();
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      <div class="card-title">Filter</div>
      <div class="card-body">
        <div class="grid">
          ${this.filters.map((x, i) => this.renderFilterRow_(x, i))}
          ${this.renderForcedFilter_()}
        </div>
      </div>
    `;
  }
}
customElements.define('card-filter', CardFilter);

