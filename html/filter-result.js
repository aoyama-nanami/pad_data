import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import { statAtMaxLv, assetsToIconCss, atkEval } from './common.js'

class FilterResult extends LitElement {
  static get properties() {
    return {
      data: { type: Array },
      config: { type: Object },
    };
  }

  static get styles() {
    return [
      assetsToIconCss(),
      css`
        .grid {
          display: grid;
          grid-template-columns: repeat(5, max-content);
          grid-column-gap: 0.5rem;
          grid-auto-rows: 1.2rem;
        }
        .numeric-cell {
          text-align: right;
          padding-left: 1rem;
        }
      `
    ]
  }

  render() {
    if (this.data) {
      return html`
        <div class="grid">${this.data.map(x => this._renderRow(x))}</div>
      `
    }
    else
      return html``
  }

  _renderRow(card) {
    return html`
      <div>
        <div class="orb-${card.attr_id}-small orb-small"></div>
        <div class="orb-${card.sub_attr_id}-small orb-small"></div>
      </div>
      <div><a href="http://pad.skyozora.com/pets/${card.card_id}" target="_blank">${card.name}</a></div>
      <div class="numeric-cell">${statAtMaxLv(card, 'hp')}</div>
      <div class="numeric-cell">${atkEval(card, this.config)}</div>
      <div class="numeric-cell">${statAtMaxLv(card, 'rcv')}</div>
    `
  }
}
customElements.define('filter-result', FilterResult);

