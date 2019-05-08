import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'
import { assetsToIconCss } from './common.js'
import { Awakening } from './awakening.js'
import { bind } from './util/bind.js'
import { iconCheckbox, toggleCheckbox } from './component/checkbox.js'

const FILTERS_ = [
  {
    desc: '',
    render: () => ''
  },
  {
    desc: '無效貫通',
    render: () => html`
      <filter-awakening
        class="filter"
        arg="[[${Awakening.VOID_DAMAGE_PIERCER}, 1]]"
        count="1">
      </filter-awakening>`
  },
  {
    desc: '主屬',
    render: () => html`<filter-element class="filter" main></filter-element>`
  },
  {
    desc: '副屬',
    render: () => html`<filter-element class="filter" sub></filter-element>`
  },
  {
    desc: '主或副屬',
    render: () => html`<filter-element class="filter" main sub></filter-element>`
  },
  {
    desc: '操作時間延長',
    render: () => html`
      <filter-awakening
        class="filter"
        arg="[[${Awakening.EXTEND_TIME}, 1], [${Awakening.EXTEND_TIME_PLUS}, 2]]"
        count="1"
        canEdit>
      </filter-awakening>`
  },
  {
    desc: 'Skill Boost',
    render: () => html`
      <filter-awakening
        class="filter"
        arg="[[${Awakening.SKILL_BOOST}, 1], [${Awakening.SKILL_BOOST_PLUS}, 2]]"
        count="1"
        canEdit>
      </filter-awakening>`
  },
]

class FilterBase extends LitElement {
  updated() {
    super.updated()
    document.querySelector('app-main').sort()
  }

  get commonCss() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      `
  }
}

class FilterAwakening extends FilterBase {
  static get properties() {
    return {
      arg: { type: Array },
      count: { type: Number },
      canEdit: { type: Boolean },
    }
  }

  static get styles() {
    return css`
      #count {
        width: 40px;
      }
      .hidden {
        display: none;
      }
    `
  }

  countAwakening(a) {
    for (let [awakening, value] of this.arg) {
      if (a == awakening)
        return value
    }
    return 0
  }

  render() {
    return html`
      ${this.commonCss}
      <span class="${this.canEdit ? '' : 'hidden'}">
        &ge;
        <input
          type="number" min="1" step="1" .value="${bind(this, 'count')}"
          maxlength="2" id="count">
      </span>
    `
  }

  get multi() {
    let e = document.querySelector('app-main')
      .shadowRoot.querySelector('atk-eval-config')
    return e.awakenings[Awakening.MULTI_BOOST]
  }

  apply(c) {
    let val = 0
    val += c.awakenings.reduce((x, a) => x + this.countAwakening(a), 0)
    if (!this.multi)
      val += c.super_awakenings.reduce((x, a) => x + this.countAwakening(a), 0)
    return val >= this.count
  }
}
customElements.define('filter-awakening', FilterAwakening)

class FilterElement extends FilterBase {
  static get properties() {
    return {
      elements: { type: Array },
      main: { type: Boolean },
      sub: { type: Boolean },
    }
  }

  static get styles() {
    return [
      assetsToIconCss(),
    ]
  }

  constructor() {
    super()
    this.elements = [false, false, false, false, false]
  }

  apply(c) {
    if (this.elements.every(x => !x))
      return true
    if (this.main && this.elements[c.attr_id])
      return true
    if (this.sub && this.elements[c.sub_attr_id])
      return true
    return false
  }

  handleChange() {
    this.elements = Array.from(this.shadowRoot.querySelectorAll('input'))
      .map(e => e.checked)
  }

  orbCheckbox_(i) {
    return iconCheckbox(`orb-${i}`, bind(this, 'elements', i), false)
  }

  render() {
    return html`
      ${this.commonCss}
      ${[0, 1, 2, 3, 4].map(i => this.orbCheckbox_(i))}
    `
  }
}
customElements.define('filter-element', FilterElement)

class CardFilter extends LitElement {
  static get properties() {
    return {
      filters: { type: Array },
      /* Force enabled filter of void damage piercer.
       * TODO: redesign this */
      overrideFilter: { type: Boolean },
    };
  }

  static get styles() {
    return [
      assetsToIconCss(),
    ]
  }

  constructor() {
    super()
    this.filters = []
    this.filter_elements_ = []
    this.overrideFilter = false
  }

  apply(card) {
    if (this.overrideFilter) {
    }
    return this.filter_elements_.every(e => e.apply(card))
  }

  newFilter_() {
    this.filters.push(0)
    this.requestUpdate();
  }

  deleteFilter_(i) {
    this.filters.splice(i, 1)
    this.requestUpdate();
  }

  updateFilter_(ev, index) {
    let elem = ev.target
    this.filters[index] = parseInt(elem.value)
    this.requestUpdate();
  }

  renderFilterRow_(x, i) {
    return html`
      <span @click="${()=>this.deleteFilter_(i)}" class="material-icons"
              title="remove">
        remove
      </span>
      <select @change="${ev => this.updateFilter_(ev, i)}">
        ${FILTERS_.map((y, j) =>
          html`<option value="${j}" .selected="${x == j}">${y.desc}</option>`)}
      </select>
      ${FILTERS_[x].render()}
      <br>
    `
  }

  renderForcedFilter_() {
    if (!this.overrideFilter)
      return ''

    let v = 1
    return html`
      <span class="material-icons" style="visibility: hidden">
        remove
      </span>
      <select>
        <option value="${v}" selected disabled>${FILTERS_[v].desc}</option>
      </select>
      ${FILTERS_[v].render()}
      <br>
    `
  }

  updated() {
    super.updated()
    this.filter_elements_ = Array.from(
      this.shadowRoot.querySelectorAll('.filter'))
    document.querySelector('app-main').sort()
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      <div class="card-title">Filter</div>
      <div class="card-body">
        <span @click="${this.newFilter_}" class="material-icons"
                title="add filter">
          add_circle
        </span><br>
        ${this.filters.map((x, i) => this.renderFilterRow_(x, i))}
        ${this.renderForcedFilter_()}
      </div>
    `
  }
}
customElements.define('card-filter', CardFilter);

