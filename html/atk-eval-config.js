import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'
import './atk-eval-config.js'
import { assetsToIconCss } from './common.js'
import { Awakening } from './awakening.js'
import { Type, TypeReverse } from './type.js'

class AtkEvalConfig extends LitElement {
  static get properties() {
    return {
      awakenings: { type: Array },
      elements: { type: Array },
      target: { type: String },
    }
  }

  static get styles() {
    return [
      assetsToIconCss(),
      css`
        #elements > input {
          width: 3em;
          text-align: right;
        }
        .card-body > div {
          margin-top: 3px;
        }
      `
    ]
  }

  constructor() {
    super()
    this.reset()
  }

  handleChange() {
    this.awakenings = Array.from(this.shadowRoot.querySelectorAll('#awakenings input:checked'))
      .map(e => parseInt(e.id.slice(1)))
    this.elements = [0, 1, 2, 3, 4]
      .map(i => this.shadowRoot.querySelector('#o' + i).value)
      .map(x => parseFloat(x, 10))
      .map(x => isNaN(x) ? 1 : x)
    this.target = this.shadowRoot.querySelector('#target').value
    document.querySelector('app-main').sort()
  }

  reset() {
    this.awakenings = [27, 43, 57]
    this.elements = [1, 1, 1, 1, 1]
    this.target = ""
  }

  generateConfig() {
    let awakenings = new Set(this.awakenings)
    let multi = awakenings.has(Awakening.MULTI_BOOST)
    let elements = Array.from(this.elements)

    let target = this.targetCard
    if (target) {
      [target.type_1_id, target.type_2_id, target.type_3_id]
        .filter(x => x >= 0)
        .map(x => TypeReverse[x] + '_KILLER')
        .map(x => Awakening[x])
        .forEach(x => awakenings.add(x))

      switch (target.attr_id) {
        case 0:
          elements[1] *= 2
          elements[2] *= 0.5
          break;
        case 1:
          elements[2] *= 2
          elements[0] *= 0.5
          break;
        case 2:
          elements[0] *= 2
          elements[1] *= 0.5
          break;
        case 3:
          elements[4] *= 2
          break;
        case 4:
          elements[3] *= 2
          break;
      }
    }

    return {
      awakenings: awakenings,
      multi: multi,
      elements: this.elements,
    }
  }

  awakeningCheckBox_(i) {
    return html`
      <span class="icon-checkbox">
        <input type="checkbox" id="a${i}" @change="${this.handleChange}"
               .checked=${this.awakenings.includes(i)}>
        <label for="a${i}">
          <div class="awakening-${i}"></div>
        </label>
      </span>
    `
  }

  orbField_(i) {
    return html`
      <div class="orb-${i}"></div>
      <input type="text" placeholder="1" id="o${i}"
             .value="${this.elements[i] == 1 ? '' : this.elements[i]}"
             @change="${this.handleChange}">
    `
  }

  get targetCard() {
    let n = parseInt(this.target)
    if (isNaN(n)) return undefined
    return document.querySelector('app-main').card(n)
  }

  displayTargetName_() {
    let card = this.targetCard
    if (!card) return ''
    return html`${card.name}`
  }

  render() {
    const awakenings = [
      27, 30, /* two way, multi boost */
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, /* killers */
      43, 48, 50, 57, 58, 60, 61,
    ]
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <div class="card-title">damage parameters</div>
      <div class="card-body">
        <div id="awakenings">
          ${awakenings.map(i => this.awakeningCheckBox_(i))}
        </div>
        <div id="elements">
          ${[0, 1, 2, 3, 4].map(i => this.orbField_(i))}
        </div>
        <div>
          Target:
          <input type="text" id="target" .value="${this.target}"
                 @change="${this.handleChange}"
                 size="5" maxlength="5">
          ${this.displayTargetName_()}
        </div>
      </div>
    `
  }
}
customElements.define('atk-eval-config', AtkEvalConfig)

