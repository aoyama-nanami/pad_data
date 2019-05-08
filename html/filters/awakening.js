import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'
import { bind } from '../util/bind.js'
import { Awakening } from '../awakening.js'
import { FilterBase } from '../card-filter.js'

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
    let e = document.querySelector('atk-eval-config')
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

