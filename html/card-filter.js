import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {Awakening} from './util/awakening.js';
import {bind} from './util/bind.js';
import {database} from './database.js';

import {FilterAwakening} from './filters/awakening.js'
import {FilterElement} from './filters/element.js'
import {FilterSkillCd} from './filters/skill-cd.js'
import {FilterNuke} from './filters/nuke.js'

function createFilter(cls, args, elem, i) {
  let filter = new cls();
  Object.keys(args).forEach((k) => filter[k] = args[k]);
  filter.classList.add('filter')
  if (elem)
    filter.addEventListener('change', (ev) => elem.onChange_(ev, i));
  return filter;
}

const FILTERS_ = [
  {
    desc: '無效貫通',
    cls: FilterAwakening,
    init: {
      awakenings: [[Awakening.VOID_DAMAGE_PIERCER, 1]],
      count: 1,
    },
  },
  {
    desc: '主屬',
    cls: FilterElement,
    init: {main: true},
  },
  {
    desc: '副屬',
    cls: FilterElement,
    init: {sub: true},
  },
  {
    desc: '主或副屬',
    cls: FilterElement,
    init: {main: true, sub: true},
  },
  {
    desc: '操作時間延長',
    cls: FilterAwakening,
    init: {
      awakenings: [[Awakening.EXTEND_TIME, 1], [Awakening.EXTEND_TIME_PLUS, 2]],
      canEdit: true,
    },
  },
  {
    desc: 'Skill Boost',
    cls: FilterAwakening,
    init: {
      awakenings: [[Awakening.SKILL_BOOST, 1], [Awakening.SKILL_BOOST_PLUS, 2]],
      canEdit: true,
    },
  },
  {
    desc: '技能 CD',
    cls: FilterSkillCd,
    init: {},
  },
  {
    desc: '大砲',
    isSkill: true,
    cls: FilterNuke,
    init: {},
  },
];

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
    this.filters.push({id: -1});
    this.requestUpdate();
  }

  deleteFilter_(i) {
    this.filters.splice(i, 1);
    this.requestUpdate();
  }

  onChange_(ev, i) {
    this.filters[i].args = ev.target.value;
    this.requestUpdate();
  }

  renderFilterRow_(row, i) {
    let {id, args} = row;

    return html`
      <div class="grid-row">
        <div class="grid-cell">
          <span @click="${() => this.deleteFilter_(i)}" class="material-icons"
                  title="remove">
            remove
          </span>
        </div>
        <div class="grid-cell">
          <select .value="${bind(this, 'filters', i, 'id')}">
            <option value="-1" disabled></option>
            ${FILTERS_.map((obj, j) =>
              obj.isSkill ? '' :
              html`<option value="${j}">${obj.desc}</option>`)}
            <optgroup label="技能">
              ${FILTERS_.map((obj, j) =>
                !obj.isSkill ? '' :
                html`<option value="${j}">${obj.desc}</option>`)}
            </optgroup>
          </select>
        </div>
        <div class="grid-cell">
          ${id >= 0 ?
            createFilter(FILTERS_[id].cls, args || FILTERS_[id].init, this, i) :
            ''}
        </div>
      </div>
    `;
  }

  renderForcedFilter_() {
    if (!this.overrideFilter) {
      return '';
    }

    const v = 0;
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
          ${createFilter(FILTERS_[v].cls, FILTERS_[v].init)}
        </div>
      </div>
    `;
  }

  updated() {
    super.updated();
    if (this.filters.length == 0 ||
        this.filters[this.filters.length - 1].id != -1) {
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
          ${this.filters.map((row, i) => this.renderFilterRow_(row, i))}
          ${this.renderForcedFilter_()}
        </div>
      </div>
    `;
  }
}
customElements.define('card-filter', CardFilter);

