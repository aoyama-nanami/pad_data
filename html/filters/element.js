import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'
import { iconCheckbox } from '../component/checkbox.js'
import { FilterBase } from '../card-filter.js'
import { assetsToIconCss } from '../common.js'
import { bind } from '../util/bind.js'

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

