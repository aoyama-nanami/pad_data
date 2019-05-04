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
          grid-template-columns: repeat(7, max-content) auto;
          grid-auto-rows: 36px;
        }
        .grid-row {
          display: contents;
        }
        .grid-row:hover .grid-cell {
          background-color: #222222;
        }
        .grid-cell {
          padding: 3px 3px 3px 3px;
        }
        .numeric-cell {
          text-align: right;
          padding-left: 8px;
        }
        a {
          color: #DDD;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
      `
    ]
  }

  render() {
    if (this.data) {
      return html`
        <link rel="stylesheet" type="text/css" href="style.css">
        <div class="card-body">
          <div class="grid">${this.data.map(x => this._renderRow(x))}</div>
        </div>
      `
    }
    else
      return html``
  }

  _renderRow(card) {
    return html`
      <div class="grid-row">
        <div class="grid-cell">
          <div class="orb-${card.attr_id}"></div><div class="orb-${card.sub_attr_id}"></div>
        </div>
        <a href="http://pad.skyozora.com/pets/${card.card_id}"
          class="grid-cell"
           target="_blank">
          ${card.name}
        </a>
        <div class="grid-cell numeric-cell">${statAtMaxLv(card, 'hp')}</div>
        <div class="grid-cell numeric-cell">${atkEval(card, this.config)}</div>
        <div class="grid-cell numeric-cell">${statAtMaxLv(card, 'rcv')}</div>
        <div class="grid-cell">
          ${card.awakenings.map(
            i => html`<div class="awakening-${i}"></div>`)}
          <div class="awakening--1"></div>
        </div>
        <div class="grid-cell">
          ${card.super_awakenings.map(
            i => html`<div class="awakening-${i}"></div>`)}
        </div>
        <div class="grid-cell">
        </div>
      </div>
    `
  }
}
customElements.define('filter-result', FilterResult);

