import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import './atk-eval-config.js'
import './filter-result.js'
import { atkEval } from './common.js'

class AppMain extends LitElement {
  static get properties() {
    return {
      data: { type: Array },
    };
  }

  constructor() {
    super();
    this.loadDatabase()
    this.data = []
  }

  loadDatabase() {
    fetch('data/jp_cards.json')
      .then((r) => {
        return r.json();
      }).then((obj) => {
        let a = []
        obj.forEach(x => {
          if (x.card.released_status && x.card.card_id < 10000)
            a[x.card.card_id] = x.card
        });
        this.data = a;
      })
  }

  qs_(x) {
    return this.shadowRoot.querySelector(x)
  }

  qsa_(x) {
    return this.shadowRoot.querySelectorAll(x)
  }

  handleClick(e) {
    let config = this.qs_('atk-eval-config').generateConfig()
    let a = Array.from(this.data)
    a.sort((c1, c2) => atkEval(c2, config) - atkEval(c1, config))
    a = a.slice(0, 40)

    let filter_result = this.qs_('filter-result')
    filter_result.data = a
    filter_result.config = config
  }

  resetAtkConfig() {
    console.log(this.qs_('atk-eval-config').awakenings)
    this.qs_('atk-eval-config').reset()
    console.log(this.qs_('atk-eval-config').awakenings)
  }

  render() {
    return html`
      <button @click="${this.handleClick}" ?disabled="${this.data.length == 0}">sort!</button>
      <button @click="${this.resetAtkConfig}" ?disabled="${this.data.length == 0}">reset</button>
      <card-filter></card-filter>
      <atk-eval-config></atk-eval-config>
      <br>
      <filter-result id="result"></filter-result>
    `
  }
}
customElements.define('app-main', AppMain);

