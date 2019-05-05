import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'
import './atk-eval-config.js'
import { assetsToIconCss } from './common.js'
import { Awakening } from './awakening.js'
import { Type, TypeReverse } from './type.js'

const LATENT = new Map([
  [Type.GOD, new Set([Type.BALANCE, Type.DEMON, Type.MACHINE])],
  [Type.DRAGON, new Set([Type.BALANCE, Type.HEALER])],
  [Type.DEMON, new Set([Type.BALANCE, Type.GOD, Type.ATTACK])],
  [Type.MACHINE, new Set([Type.BALANCE, Type.PHYSICAL, Type.DRAGON])],
  [Type.BALANCE, new Set([Type.BALANCE, Type.MACHINE])],
  [Type.ATTACK, new Set([Type.BALANCE, Type.HEALER])],
  [Type.PHYSICAL, new Set([Type.BALANCE, Type.ATTACK])],
  [Type.HEALER, new Set([Type.BALANCE, Type.DRAGON, Type.PHYSICAL])],
])

function bitFlagToArray(x) {
  let ret = []
  for (let i = 0; i < 32; i++) {
    let j = 1 << i
    if (j > x) break
    if (j & x) ret.push(i)
  }
  return ret
}

class AtkEvalConfig extends LitElement {
  static get properties() {
    return {
      awakenings: { type: Array },
      target: { type: String },
      includeSubElemDamage: { type: Boolean },
      latentKillerCount: { type: Number },
      passiveResistIndex: { type: Number },
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
          padding: 3px 3px 3px 3px;
        }
        #latent-killer-count {
          width: 40px;
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
    this.target = this.shadowRoot.querySelector('#target').value
    this.latentKillerCount =
      parseInt(this.shadowRoot.querySelector('#latent-killer-count').value)
    this.includeSubElemDamage =
      this.shadowRoot.querySelector('#sub-elem').checked
    this.passiveResistIndex =
      parseInt(this.shadowRoot.querySelector('input[name="passive-id"]:checked').value)
  }

  reset() {
    this.awakenings = [27, 43, 57]
    this.target = ""
    this.latentKillerCount = 0
    this.includeSubElemDamage = true
    this.passiveResistIndex = -1
  }

  generateConfig() {
    let awakenings = new Set(this.awakenings)
    let multi = awakenings.has(Awakening.MULTI_BOOST)
    let elements = [1, 1, 1, 1, 1]
    let types = []

    let target = this.targetCard
    if (target) {
      target.type
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
      if (this.latentKillerCount > 0) {
        let latentTypes = new Set()
        let latentBonusDamage = Math.pow(1.5, this.latentKillerCount)
        target.type.forEach(x => {
          if (x >= 1 && x <= 8) {
            LATENT.get(x).forEach(y => latentTypes.add(y))
          } else if (x == 0 || x == 12 || x == 14 || x == 15) {
            Object.keys(Type).forEach(k => latentTypes.add(Type[k]))
          }
        })
        types.push([latentTypes, latentBonusDamage])
      }
      if (this.passiveResistIndex >= 0) {
        let skill = this.targetCard['enemy_passive_resist'][this.passiveResistIndex]
        let type = skill['skill_type']
        let args = bitFlagToArray(skill['param'][0])
        let ratio = skill['param'][1]

        if (type == 72) {
          args.forEach(x => elements[x] *= (ratio / 100.0))
        } else {
          types.push([args, ratio / 100.0])
        }
      }
    }

    return {
      awakenings: awakenings,
      multi: multi,
      elements: elements,
      includeSubElemDamage: this.includeSubElemDamage,
      types: types,
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

  get targetCard() {
    let n = parseInt(this.target)
    if (isNaN(n)) return undefined
    return document.querySelector('app-main').card(n)
  }

  displayTargetName_() {
    let card = this.targetCard
    if (!card) return ''
    return html`
      <a href="http://pad.skyozora.com/pets/${card.card_id}"
         class="target-name-info">
        ${card.name}
      </a>`
  }

  displayPassiveResist_(x, i) {
    let type = x['skill_type']
    let args = bitFlagToArray(x['param'][0])
    let ratio = x['param'][1]
    return html`
      <div>
        <input type="radio" name="passive-id" value="${i}"
               id="passive-id-${i}"
               @click="${this.handleChange}"
               .checked="${this.passiveResistIndex == i}">
        <label for="passive-id-${i}">
          ${x['skill_name']} -
          ${type == 72 ?
            args.map(i => html`<div class="orb-${i}"></div>`) :
            args.map(i => html`<div class="type-${i}"></div>`)
          }
          傷害${ratio}%輕減
        </label>
      </div>
    `
  }

  updated() {
    document.querySelector('app-main').sort()
  }

  render() {
    const awakenings = [
      27, 30, /* two way, multi boost */
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, /* killers */
      43, 48, 50, 57, 58, 60, 61,
    ]
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      <div class="card-title">
        Damage Parameters
        <span id="reset" @click="${this.reset}" class="material-icons"
                title="reset">
          cached
        </span>
      </div>
      <div class="card-body">
        <div id="awakenings">
          ${awakenings.map(i => this.awakeningCheckBox_(i))}
        </div>
        <div>
          目標敵人:
          <input type="text" id="target" .value="${this.target}"
                 @change="${this.handleChange}"
                 size="12" maxlength="5"
                 placeholder="input pet ID">
          ${this.displayTargetName_()}
          <br>
          <div style="${!this.targetCard ? 'display: none' : ''}">
            <div>
              潛覺殺手:
              <input type="number" .value="${this.latentKillerCount}"
                     @change="${this.handleChange}"
                     min="0" max="3" step="1" id="latent-killer-count">
            </div>
            <div>
              被動減傷:
              <div>
                <input type="radio" name="passive-id" value="-1"
                       id="passive-id--1"
                       @click="${this.handleChange}"
                       .checked="${this.passiveResistIndex == -1}">
                <label for="passive-id--1">無</label>
              </div>
              ${this.targetCard ?
                this.targetCard['enemy_passive_resist'].map(
                  (x, i) => this.displayPassiveResist_(x, i)) :
                ''}
            </div>
          </div>
        </div>
        <div>
          <span class="toggle-checkbox">
            <input type="checkbox" .checked="${this.includeSubElemDamage}"
                   id="sub-elem" @change="${this.handleChange}">
            <label for="sub-elem" class="material-icons"></label>
            主副屬相同時加算副屬傷害
          </span>
        </div>
      </div>
    `
  }
}
customElements.define('atk-eval-config', AtkEvalConfig)

