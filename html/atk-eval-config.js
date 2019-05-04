import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import './atk-eval-config.js'
import { assetsToIconCss } from './common.js'

class AtkEvalConfig extends LitElement {
  static get properties() {
    return {
      awakenings: { type: Array },
      elements: { type: Array },
    };
  }

  static get styles() {
    return [
      assetsToIconCss(),
      css`
        #awakenings > input {
          display: none;
        }
        #awakenings > label {
          display: inline;
        }
        #awakenings > input:not(:checked) + label {
          filter: grayscale(100%);
        }

        #elements > input {
          width: 3em;
          text-align: right;
        }
        legend {
          padding-left: 0.5em;
          padding-right: 0.5em;
        }
      `
    ]
  }

  constructor() {
    super()
    this.reset()
  }

  handleChange() {
    this.awakenings = Array.from(this.shadowRoot
      .querySelectorAll('#awakenings > input:checked'))
      .map(e => parseInt(e.id.slice(1)))
    this.elements = [0, 1, 2, 3, 4]
      .map(i => this.shadowRoot.querySelector('#o' + i).value)
      .map(x => parseFloat(x, 10))
      .map(x => isNaN(x) ? 1 : x)
  }

  reset() {
    this.awakenings = [27, 43, 57]
    this.elements = [1, 1, 1, 1, 1]
  }

  generateConfig() {
    let multi = this.awakenings.some(x => x == 30)
    return {
      awakenings: this.awakenings,
      multi: multi,
      elements: this.elements,
    }
  }

  awakeningCheckBox_(i) {
    return html`
        <input type="checkbox" id="a${i}" @change="${this.handleChange}"
               .checked=${this.awakenings.some(x => x == i)}>
        <label for="a${i}">
          <div class="awakening-${i} awakening"></div>
        </label>
    `
  }

  orbField_(i) {
    return html`
      <div class="orb-${i} orb"></div>
      <input type="text" placeholder="1" id="o${i}"
             .value="${this.elements[i] == 1 ? '' : this.elements[i]}"
             @change="${this.handleChange}">
    `
  }

  render() {
    const awakenings = [
      27, 30, /* two way, multi boost */
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, /* killers */
      43, 48, 50, 57, 58, 60, 61,
    ]
    console.log('render')
    return html`
      <fieldset>
        <legend>damage parameters</legend>
        <div id="awakenings">
          ${awakenings.map(i => this.awakeningCheckBox_(i))}
        </div>
        <div id="elements">
          ${[0, 1, 2, 3, 4].map(i => this.orbField_(i))}
        </div>
      </fieldset>
    `
  }
}
customElements.define('atk-eval-config', AtkEvalConfig);

