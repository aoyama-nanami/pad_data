import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {ifDefined} from 'https://unpkg.com/lit-html@1.0.0/directives/if-defined.js?module';
import {Awakening} from './awakening.js';
import {bind} from './util/bind.js';
import {database} from './database.js';

const FILTERS_ = [
  {
    desc: '無效貫通',
    render: () => html`
      <filter-awakening
        class="filter"
        awakenings="[[${Awakening.VOID_DAMAGE_PIERCER}, 1]]"
        count="1">
      </filter-awakening>`,
  },
  {
    desc: '主屬',
    render: (args, elem, i) => html`
      <filter-element
        class="filter"
        elements="${ifDefined(JSON.stringify(args.elements))}"
        @change="${(ev) => elem.onChange_(ev, i)}"
        main>
      </filter-element>`,
  },
  {
    desc: '副屬',
    render: (args, elem, i) => html`
      <filter-element
        class="filter"
        elements="${ifDefined(JSON.stringify(args.elements))}"
        @change="${(ev) => elem.onChange_(ev, i)}"
        sub>
      </filter-element>`,
  },
  {
    desc: '主或副屬',
    render: (args, elem, i) => html`
      <filter-element
        class="filter"
        elements="${ifDefined(JSON.stringify(args.elements))}"
        @change="${(ev) => elem.onChange_(ev, i)}"
        main sub>
      </filter-element>`,
  },
  {
    desc: '操作時間延長',
    render: (args, elem, i) => html`
      <filter-awakening
        class="filter"
        awakenings="[[${Awakening.EXTEND_TIME}, 1],
                     [${Awakening.EXTEND_TIME_PLUS}, 2]]"
        count="${ifDefined(args.count)}"
        canEdit
        @change="${(ev) => elem.onChange_(ev, i)}"
        >
      </filter-awakening>`,
  },
  {
    desc: 'Skill Boost',
    render: (args, elem, i) => html`
      <filter-awakening
        class="filter"
        awakenings="[[${Awakening.SKILL_BOOST}, 1],
                     [${Awakening.SKILL_BOOST_PLUS}, 2]]"
        count="${ifDefined(args.count)}"
        canEdit
        @change="${(ev) => elem.onChange_(ev, i)}"
        >
      </filter-awakening>`,
  },
  {
    desc: '技能 CD',
    render: (args, elem, i) => html`
      <filter-skill-cd
        class="filter"
        op="${ifDefined(args.op)}"
        cd="${ifDefined(args.cd)}"
        @change="${(ev) => elem.onChange_(ev, i)}"
        >
      </filter-skill-cd>`,
  },
  {
    desc: '大砲',
    isSkill: true,
    render: (args, elem, i) => html`
      <filter-nuke
        class="filter"
        percentage="${ifDefined(args.percentage)}"
        element="${ifDefined(args.element)}"
        target="${ifDefined(args.target)}"
        selfDamage="${ifDefined(args.selfDamage)}"
        leech="${ifDefined(args.leech)}"
        @change="${(ev) => elem.onChange_(ev, i)}"
        >
      </filter-nuke>`,
  },
];

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
    this.filters.push({id: -1, args: {}});
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
          ${id >= 0 ? FILTERS_[id].render(args, this, i) : ''}
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

