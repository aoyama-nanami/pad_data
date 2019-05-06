import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
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
        width: 1600px;
        overflow: hidden;
        margin-left: auto;
        margin-right: auto;
      }
    `
  }

  constructor() {
    super()
    this.loadDatabase()
    this.data = []
  }

  loadDatabase() {
    fetch('data/jp_cards_merged.json')
      .then(r => r.json())
      .then(obj => {
        let a = []
        obj.forEach(c => a[c.card_id] = c)
        this.data = a
        this.sort()
      })
  }

  qs_(x) {
    return this.shadowRoot.querySelector(x)
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
      .map(c => [c, atkEval(c, config)])
      .sort((a1, a2) => a2[1] - a1[1])
      .slice(0, 30)
      .map(a => a[0])

    let filter_result = this.qs_('filter-result')
    filter_result.data = a
    filter_result.config = config
  }

  get ready() {
    return this.data.length > 0
  }

  render() {
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <div style="${this.ready ? 'display: none' : ''}">
        loading...
      </div>
      <div class="grid-two-col" style="${!this.ready ? 'display: none' : ''}">
        <atk-eval-config class="card"></atk-eval-config>
        <card-filter class="card"></card-filter>
        <filter-result id="result" class="card" style="grid-column-end: span 2"></filter-result>
      </div>
    `
  }
}
customElements.define('app-main', AppMain)

