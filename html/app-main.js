import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import './atk-eval-config.js'
import './filter-result.js'
import './card-filter.js'
import { atkEval } from './common.js'

class AppMain extends LitElement {
  static get properties() {
    return {
      data: { type: Array },
    }
  }

  static get styles() {
    return css`
      .grid-two-col {
        display: grid;
        grid-template-columns: 50% 50%;
        grid-column-gap: 0.5rem;
      }
    `
  }

  constructor() {
    super()
    this.loadDatabase()
    this.data = []
  }

  loadDatabase() {
    fetch('data/jp_cards.json')
      .then(r => r.json())
      .then(obj => {
        let a = []
        obj.forEach(x => {
          if (x.card.released_status && x.card.card_id < 10000)
            a[x.card.card_id] = x.card
        })
        this.data = a
        this.sort()
      })
  }

  qs_(x) {
    return this.shadowRoot.querySelector(x)
  }

  qsa_(x) {
    return this.shadowRoot.querySelectorAll(x)
  }

  card(id) {
    return this.data[id]
  }

  handleClick(e) {
    this.sort()
  }

  sort() {
    let config = this.qs_('atk-eval-config').generateConfig()
    let filter = this.qs_('card-filter')
    let a = this.data
      .filter(c => filter.apply(c))
      .sort((c1, c2) => atkEval(c2, config) - atkEval(c1, config))
      .slice(0, 30)

    let filter_result = this.qs_('filter-result')
    filter_result.data = a
    filter_result.config = config
  }

  resetAtkConfig() {
    this.qs_('atk-eval-config').reset()
  }

  get ready() {
    return this.data.length > 0
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <div class="grid-two-col">
        <div class="card" style="grid-column-end: span 2">
          <button @click="${this.handleClick}" ?disabled="${!this.ready}">sort!</button>
          <button @click="${this.resetAtkConfig}" ?disabled="${!this.ready}">reset</button>
        </div>
        <atk-eval-config class="card"></atk-eval-config>
        <card-filter class="card"></card-filter>
        <filter-result id="result" class="card" style="grid-column-end: span 2"></filter-result>
      </div>
    `
  }
}
customElements.define('app-main', AppMain)

