import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'
import { assetsToIconCss } from './common.js'
import { Awakening } from './awakening.js'

const FILTERS_ = [
  {
    desc: '',
    render: () => ''
  },
  {
    desc: '無效貫通',
    render: () => html`<filter-void-damage-piercer class="filter"></filter-void-damage-piercer>`
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
]

class VoidDamagePiercer extends LitElement {
  apply(c) {
    return c.awakenings.includes(Awakening.VOID_DAMAGE_PIERCER)
  }
}
customElements.define('filter-void-damage-piercer', VoidDamagePiercer)

class Element extends LitElement {
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
    this.elements = [0, 0, 0, 0, 0]
  }

  apply(c) {
    if (this.main && this.elements[c.attr_id])
      return true
    if (this.sub && this.elements[c.sub_attr_id])
      return true
    return false
  }

  handleChange() {
    this.elements = Array.from(this.shadowRoot.querySelectorAll('input'))
      .map(e => e.checked ? 1 : 0)
  }

  orbCheckbox_(i) {
    return html`
      <span class="icon-checkbox">
        <input type="checkbox" id="o${i}" @change="${this.handleChange}"
               .checked=${this.elements[i]}>
        <label for="o${i}">
          <div class="orb-${i}"></div>
        </label>
      </span>
    `
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      ${[0, 1, 2, 3, 4].map(i => this.orbCheckbox_(i))}
    `
  }
}
customElements.define('filter-element', Element)

class CardFilter extends LitElement {
  static get properties() {
    return {
      filters: { type: Array }
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
  }

  apply(card) {
    return Array.from(this.shadowRoot.querySelectorAll('.filter'))
      .every(e => e.apply(card))
  }

  newFilter_() {
    this.filters.push(0)
    this.requestUpdate();
  }

  deleteFilter_(i) {
    this.filters.splice(i, 1)
    this.requestUpdate();
  }

  updateFilter_(e) {
    let elem = e.currentTarget
    let index = parseInt(elem.dataset.index)
    this.filters[index] = parseInt(elem.value)
    this.requestUpdate();
  }

  renderFilterRow_(x, i) {
    return html`
      <button @click="${()=>this.deleteFilter_(i)}">-</button>
      <select .value="${x}" @change="${this.updateFilter_}" data-index="${i}">
        ${FILTERS_.map((y, j) => html`<option value="${j}">${y.desc}</option>`)}
      </select>
      ${FILTERS_[x].render()}
      <br>
    `
  }

  updated() {
    super.updated()
    document.querySelector('app-main').sort()
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <div class="card-title">search filter</div>
      <div class="card-body">
        ${this.filters.map((x, i) => this.renderFilterRow_(x, i))}
        <button @click=${this.newFilter_}>+</button>
      </div>
    `
  }
}
customElements.define('card-filter', CardFilter);

