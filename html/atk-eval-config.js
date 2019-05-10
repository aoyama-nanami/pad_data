import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {icon} from './common.js';
import {Awakening} from './awakening.js';
import {Type, typeToKiller} from './type.js';
import {bind, bindRadio} from './util/bind.js';
import {toggleCheckbox, radio} from './component/checkbox.js';
import {database} from './database.js';

const LATENT = new Map([
  [Type.GOD, new Set([Type.BALANCE, Type.DEMON, Type.MACHINE])],
  [Type.DRAGON, new Set([Type.BALANCE, Type.HEALER])],
  [Type.DEMON, new Set([Type.BALANCE, Type.GOD, Type.ATTACK])],
  [Type.MACHINE, new Set([Type.BALANCE, Type.PHYSICAL, Type.DRAGON])],
  [Type.BALANCE, new Set([Type.BALANCE, Type.MACHINE])],
  [Type.ATTACK, new Set([Type.BALANCE, Type.HEALER])],
  [Type.PHYSICAL, new Set([Type.BALANCE, Type.ATTACK])],
  [Type.HEALER, new Set([Type.BALANCE, Type.DRAGON, Type.PHYSICAL])],
]);

function bitFlagToArray(x) {
  const ret = [];
  for (let i = 0; i < 32; i++) {
    const j = 1 << i;
    if (j > x) break;
    if (j & x) ret.push(i);
  }
  return ret;
}

class AtkEvalConfig extends LitElement {
  static get properties() {
    return {
      awakenings: {type: Array},
      target: {type: String},
      includeSubElemDamage: {type: Boolean},
      latentKillerCount: {type: Number},
      passiveResistIndexes: {type: Array},
      sortBy: {type: String},
      maxResult: {type: String},
    };
  }

  static get styles() {
    return css`
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
    `;
  }

  constructor() {
    super();
    this.awakenings = [];
    this.reset();
  }

  firstUpdated(changedProperties) {
    super.firstUpdated(changedProperties);
    this.shadowRoot.querySelector('#target').addEventListener(
        'change', (ev) => this.handleTargetChange_(ev));
  }

  reset() {
    this.awakenings = [];
    [27, 43, 57, 58, 60].forEach((i) => this.awakenings[i] = true);
    this.target = '';
    this.latentKillerCount = 0;
    this.includeSubElemDamage = true;
    this.passiveResistIndexes = [];
    this.sortBy = 'atk';
    this.maxResult = '30';
  }

  generateConfig() {
    const awakenings =
      new Set(this.awakenings
          .map((_, i) => i)
          .filter((i) => this.awakenings[i])
      );
    const multi = awakenings.has(Awakening.MULTI_BOOST);
    const elements = [1, 1, 1, 1, 1];
    const types = [];

    const target = this.targetCard;
    if (target) {
      this.overrideAwakenings.forEach(
          (v, k) =>
              {v ? awakenings.add(k) : awakenings.delete(k);}
          );

      switch (target.attr_id) {
        case 0:
          elements[1] *= 2;
          elements[2] *= 0.5;
          break;
        case 1:
          elements[2] *= 2;
          elements[0] *= 0.5;
          break;
        case 2:
          elements[0] *= 2;
          elements[1] *= 0.5;
          break;
        case 3:
          elements[4] *= 2;
          break;
        case 4:
          elements[3] *= 2;
          break;
      }
      if (this.latentKillerCount > 0) {
        const latentTypes = new Set();
        const latentBonusDamage = Math.pow(1.5, this.latentKillerCount);
        target.type.forEach((x) => {
          if (x >= 1 && x <= 8) {
            LATENT.get(x).forEach((y) => latentTypes.add(y));
          } else if (x == 0 || x == 12 || x == 14 || x == 15) {
            Object.keys(Type).forEach((k) => latentTypes.add(Type[k]));
          }
        });
        types.push([latentTypes, latentBonusDamage]);
      }
      this.passiveResistIndexes.forEach((enabled, i) => {
        if (!enabled) {
          return;
        }
        const skill = this.targetCard.enemy_passive_resist[i];
        const type = skill.skill_type;
        const args = bitFlagToArray(skill.param[0]);
        const ratio = skill.param[1];

        if (type == 72) {
          args.forEach((x) => elements[x] *= (ratio / 100.0));
        } else if (type == 118) {
          types.push([new Set(args), ratio / 100.0]);
        }
      });
    }

    return {
      awakenings: awakenings,
      multi: multi,
      elements: elements,
      includeSubElemDamage: this.includeSubElemDamage,
      types: types,
      sortBy: this.sortBy,
      maxResult: parseInt(this.maxResult),
    };
  }

  awakeningCheckBox_(i) {
    return html`
      <awakening-checkbox
        awakeningId="${i}"
        ?checked="${bind(this, 'awakenings', i)}"
        ?override="${this.overrideAwakenings.has(i)}"
        ?overrideChecked="${this.overrideAwakenings.get(i)}"
      >
      </awakening-checkbox>
    `
  }

  get targetCard() {
    const n = parseInt(this.target);
    if (isNaN(n)) return undefined;
    return database.card(n);
  }

  displayTargetName_() {
    const card = this.targetCard;
    if (!card) return '';
    return html`
      <a href="http://pad.skyozora.com/pets/${card.card_id}"
         class="target-name-info"
         target="_blank">
        ${card.name}
      </a>`;
  }

  displayPassiveResist_(x, i) {
    const type = x.skill_type;
    if (type == 72 || type == 118) {
      const args = bitFlagToArray(x.param[0]);
      const ratio = x.param[1];
      return toggleCheckbox(
          html`
            ${x.skill_name} -
            ${type == 72 ?
              args.map((i) => icon('orb', i)) :
              args.map((i) => icon('t', i))}
            傷害${ratio}%輕減
          `,
          bind(this, 'passiveResistIndexes', i),
          false
      );
    } else if (type == 71) {
      const turn = x.param[0];
      const threshold = x.param[2];
      return toggleCheckbox(
          `${x.skill_name} - ${turn} 回合, ${threshold} 以上傷害無效化`,
          this.passiveResistIndexes[i],
          false,
          (ev) => this.handleVoidShieldToggle_(ev, i)
      );
    }
  }

  handleTargetChange_(ev) {
    this.passiveResistIndexes = [];
    this.latentKillerCount = 0;
    const cardFilter = document.querySelector('card-filter');
    cardFilter.overrideFilter = false;
  }

  get overrideAwakenings() {
    const target = this.targetCard;
    const overrideAwakenings = new Map();
    if (!target) {
      return overrideAwakenings;
    }

    const killers = target.type.map(typeToKiller);
    for (let i = Awakening.DRAGON_KILLER;
        i <= Awakening.VENDOR_MATERIAL_KILLER;
        i++) {
      overrideAwakenings.set(i, killers.includes(i));
    }

    if (target.enemy_passive_resist.some(
        (v, i) => v.skill_type == 71 && this.passiveResistIndexes[i])) {
      overrideAwakenings.set(Awakening.VOID_DAMAGE_PIERCER, true);
    }

    return overrideAwakenings;
  }

  handleVoidShieldToggle_(ev, i) {
    const elem = ev.target;
    const checked = elem.checked;
    this.passiveResistIndexes[i] = checked;
    if (checked) {
      this.overrideAwakenings.set(Awakening.VOID_DAMAGE_PIERCER, true);
    } else {
      this.overrideAwakenings.delete(Awakening.VOID_DAMAGE_PIERCER);
    }
    const cardFilter = document.querySelector('card-filter');
    cardFilter.overrideFilter = checked;
    this.requestUpdate();
  }

  updated(changed) {
    database.sort();
  }

  render() {
    const awakenings = [
      27, 30, /* two way, multi boost */
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, /* killers */
      43, 48, 50, 57, 58, 60, 61,
    ];
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
          ${awakenings.map((i) => this.awakeningCheckBox_(i))}
        </div>
        <div>
          目標敵人:
          <input type="text" id="target" .value="${bind(this, 'target')}"
                 size="12" maxlength="5"
                 placeholder="input pet ID">
          ${this.displayTargetName_()}
          <br>
          <div style="${!this.targetCard ? 'display: none' : ''}">
            <div>
              潛覺殺手:
              <input type="number" .value="${bind(this, 'latentKillerCount')}"
                     min="0" max="3" step="1" id="latent-killer-count">
            </div>
            <div>
              被動減傷:<br>
              ${this.targetCard ?
                this.targetCard.enemy_passive_resist.map(
                    (x, i) => html`${this.displayPassiveResist_(x, i)}<br>`) :
                ''}
            </div>
          </div>
        </div>
        <div>
          ${toggleCheckbox('主副屬相同時加算副屬傷害',
                           bind(this, 'includeSubElemDamage'), false)}
        </div>
        <div>
          排序方式:
          ${radio('攻擊力', 'sort-by', 'atk', bindRadio(this, 'sortBy'))}
          ${radio('最小CD', 'sort-by', 'cd', bindRadio(this, 'sortBy'))}
        </div>
        <div>
          顯示數量:
          ${radio('30', 'max-result', '30', bindRadio(this, 'maxResult'))}
          ${radio('50', 'max-result', '50', bindRadio(this, 'maxResult'))}
          ${radio('100', 'max-result', '100', bindRadio(this, 'maxResult'))}
        </div>
      </div>
    `;
  }
}
customElements.define('atk-eval-config', AtkEvalConfig);

