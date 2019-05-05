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
          grid-template-columns: repeat(8, max-content) auto;
          line-height: 24px;
        }
        .grid-row {
          display: contents;
        }

        .grid-row:hover .grid-cell {
          background-color: rgba(161, 194, 250, 0.2);
        }

        .grid-cell {
          padding: 3px 3px 0 3px;
          height: 54px;
          display: inline-block;
          vertical-align: baseline;
          border-bottom: 1px solid rgb(85, 85, 85);
        }

        .numeric-cell {
          font-family: Roboto;
          text-align: right;
          padding-left: 5px;
          padding-right: 5px;
        }
        a {
          color: #DDD;
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        .skill-desc {
          font-family: inherit;
          font-size: inherit;
          display: inline;
          vertical-align: middle;
          padding-top: 3px;
        }
      `
    ]
  }

  render() {
    if (this.data) {
      return html`
        <link rel="stylesheet" type="text/css" href="style.css">
        <div class="grid">${this.data.map(x => this._renderRow(x))}</div>
      `
    }
    else
      return html``
  }

  _renderRow(card) {
    return html`
      <div class="grid-row">
        <div class="grid-cell">
          <div style="height: 27px">
            <div class="orb-${card.attr_id}"></div><div class="orb-${card.sub_attr_id}"></div>
          </div>
          <div style="height: 24px">
            ${card.type.map(i => html`<div class="type-${i}"></div>`)}
          </div>
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
          <div style="height: 27px">
            ${card.awakenings.map(
              i => html`<div class="awakening-${i}"></div>`)}
          </div>
          <div style="height: 24px">
            ${card.super_awakenings.map(
              i => html`<div class="awakening-${i}"></div>`)}
          </div>
        </div>
        <div class="grid-cell numeric-cell">${card.skill.turn_min}</div>
        <div class="grid-cell">
          <pre class="skill-desc">${card.skill.description}</pre>
        </div>
        <div class="grid-cell">
        </div>
      </div>
    `
  }
}
customElements.define('filter-result', FilterResult);
