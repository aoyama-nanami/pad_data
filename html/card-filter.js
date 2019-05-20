import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {Awakening} from './util/awakening.js';
import {bind} from './util/bind.js';
import {database} from './database.js';
import {toggleCheckbox} from './component/checkbox.js';

import {FilterAssist} from './filters/assist.js'
import {FilterAwakening} from './filters/awakening.js'
import {FilterElement} from './filters/element.js'
import {FilterSkillCd} from './filters/skill-cd.js'

import {FilterAllOrbChange} from './filters/all-orb-change.js'
import {FilterDmgBuff} from './filters/dmg-buff.js'
import {FilterGravity} from './filters/gravity.js'
import {FilterLowHpNuke} from './filters/low-hp-nuke.js'
import {FilterNuke} from './filters/nuke.js'
import {FilterOrbChange} from './filters/orb-change.js'
import {FilterRandomOrbSpawn} from './filters/random-orb-spawn.js'
import {FilterSacrifice} from './filters/sacrifice.js'
import {FilterType} from './filters/type.js'

const FILTERS_ = [
  {
    desc: ' ',  // separator
  },
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
    desc: 'Type',
    cls: FilterType,
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
    desc: '可裝備',
    cls: FilterAssist,
  },
  {
    desc: '技能 CD',
    cls: FilterSkillCd,
  },
  {
    desc: '主動技',  // separator
  },
  {
    desc: '大砲',
    cls: FilterNuke,
  },
  {
    desc: '低血砲',
    cls: FilterLowHpNuke,
  },
  {
    desc: '自殘',
    cls: FilterSacrifice,
  },
  {
    desc: '轉珠',
    cls: FilterOrbChange,
  },
  {
    desc: '重力',
    cls: FilterGravity,
  },
  {
    desc: '真重力',
    cls: FilterGravity,
    init: {trueGravity: true},
  },
  {
    desc: '屬性/type 增傷',
    cls: FilterDmgBuff,
  },
  {
    desc: '陣',
    cls: FilterAllOrbChange,
  },
  {
    desc: '隨機產生寶珠',
    cls: FilterRandomOrbSpawn,
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
          grid-template-columns: 22px 30px max-content auto;
          grid-auto-rows: 28px;
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

        .remove-btn {
          font-size: 14px;
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

  createFilter(cls, args, i, enabled) {
    let filter = new cls();
    Object.keys(args).forEach((k) => filter[k] = args[k]);
    filter.classList.add('filter')
    filter.classList.add(enabled ? 'enabled' : 'disabled')
    if (i >= 0)
      filter.addEventListener('change', (ev) => this.onChange_(ev, i));
    return filter;
  }

  newFilter_() {
    this.filters.push({id: 0});
    this.requestUpdate();
  }

  deleteFilter_(i) {
    this.filters.splice(i, 1);
    this.requestUpdate();
  }

  changeFilterId_(i, ev) {
    const id = parseInt(ev.target.value);
    this.filters[i] = {id: id, enabled: (id > 0)};
    if (i == this.filters.length - 1 && id > 0) {
      this.newFilter_();
    }
    this.requestUpdate();
  }

  onChange_(ev, i) {
    this.filters[i].args = ev.target.value;
    this.requestUpdate();
  }

  renderFilterRow_(row, i) {
    let {id, args, enabled} = row;
    args = args || FILTERS_[id].init || {};

    return html`
      <div class="grid-row">
        <div class="grid-cell">
          <span @click="${() => this.deleteFilter_(i)}"
                class="material-icons pointer remove-btn"
                style="${id <= 0 ? 'display: none' : ''}"
                title="remove">
            remove_circle_outline
          </span>
        </div>
        <div class="grid-cell">
          ${id <= 0 ? '' :
            toggleCheckbox('', bind(this, 'filters', i, 'enabled'))}
        </div>
        <div class="grid-cell">
          <select .value="${this.filters[i].id}"
                  @change="${(ev) => this.changeFilterId_(i, ev)}">
            ${FILTERS_.map((obj, j) =>
              html`<option value="${j}" ?disabled="${!obj.cls}"
                           ?selected="${this.filters[i].id == j}">
                       ${obj.desc}
                   </option>`
              )}
          </select>
        </div>
        <div class="grid-cell">
          ${FILTERS_[id].cls ?
            this.createFilter(FILTERS_[id].cls, args, i, enabled) :
            ''}
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
        </div>
        <div class="grid-cell">
          無效貫通
        </div>
        <div class="grid-cell">
          ${this.createFilter(FILTERS_[v].cls, FILTERS_[v].init, -1, true)}
        </div>
      </div>
    `;
  }

  updated() {
    super.updated();
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

