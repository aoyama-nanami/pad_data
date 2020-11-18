import {LitElement, html, css} from './util/external_lib.js';
import {icon} from './common.js';
import {Awakening} from './util/awakening.js';
import {Type, typeToKiller} from './util/type.js';
import {bind, bindRadio} from './util/bind.js';
import {iconRadio, toggleCheckbox, radio} from './component/checkbox.js';
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
      targetAttr: {type: Number},
      passiveResistIndexes: {type: Array},
      sortBy: {type: String},
      showLeaderSkill: {type: Boolean},
    };
  }

  static get styles() {
    return css`
      #latent-killer-count {
        width: 40px;
      }
      div.row {
        padding: 3px 3px 1px 3px;
        height: 24px;
      }
      fieldset {
        border-color: rgb(85, 85, 85);
        padding: 5px 0 5px 12px;
      }
      legend {
        border: 1px solid rgb(85, 85, 85);
        padding-left: 15px;
        padding-right: 15px;
      }
      legend:hover {
        text-decoration: underline;
      }
      .flex-awakenings-list {
        flex-wrap: wrap;
        height: auto !important;
      }
    `;
  }

  constructor() {
    super();
    this.awakenings = [];
    [27, 43, 57, 58, 60].forEach((i) => this.awakenings[i] = true);
    this.target = '';
    this.latentKillerCount = 0;
    this.includeSubElemDamage = true;
    this.passiveResistIndexes = [];
    this.sortBy = 'atk';
    this.showLeaderSkill = false;
  }

  firstUpdated(changedProperties) {
    super.firstUpdated(changedProperties);
    this.shadowRoot.querySelector('#target').addEventListener(
        'change', (ev) => this.handleTargetChange_(ev));
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
    const latentKillerTypes = new Set();

    const target = this.targetCard;
    if (target) {
      this.overrideAwakenings.forEach(
          (v, k) => v ? awakenings.add(k) : awakenings.delete(k));

      switch (this.targetAttr) {
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
        target.type.forEach((x) => {
          if (x >= 1 && x <= 8) {
            LATENT.get(x).forEach((y) => latentKillerTypes.add(y));
          } else if (x == 0 || x == 12 || x == 14 || x == 15) {
            Object.keys(Type).forEach((k) => latentKillerTypes.add(Type[k]));
          }
        });
      }

      this.passiveResistIndexes.forEach((enabled, i) => {
        if (!enabled) {
          return;
        }
        const [type, effect] =
          this.targetCard.enemy_passive_resist[i].effects[0];

        if (type == 'ElementDamageReduction') {
          effect.elements.forEach((x) => elements[x] *= 1 - (effect.dr / 100.0));
        } else if (type == 'TypeDamageReduction') {
          types.push([new Set(effect.types), effect.dr / 100.0]);
        }
      });
    }

    return {
      awakenings: awakenings,
      multi: multi,
      elements: elements,
      includeSubElemDamage: this.includeSubElemDamage,
      types: types,
      latentKillerTypes: latentKillerTypes,
      latentKillerCount: this.latentKillerCount,
      sortBy: this.sortBy,
    };
  }

  awakeningCheckBox_(i) {
    return html`<icon-checkbox
        icon="a${i}"
        ?checked="${bind(this, 'awakenings', i)}"
        ?override="${this.overrideAwakenings.has(i)}"
        ?overrideChecked="${this.overrideAwakenings.get(i)}"
      >
      </icon-checkbox>`;
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

  displayPassiveResist_(skill, i) {
    const [type, effect] = skill.effects[0];
    if (type == 'ElementDamageReduction' || type == 'TypeDamageReduction') {
      return toggleCheckbox(
          html`
            ${skill.name} -
            ${type == 'ElementDamageReduction' ?
              effect.elements.map((i) => icon('orb' + i)) :
              effect.types.map((i) => icon('t' + i))}
            傷害${effect.dr}%輕減
          `,
          bind(this, 'passiveResistIndexes', i),
          false
      );
    } else if (type == 'VoidDamageShield') {
      return toggleCheckbox(
          `${skill.name} - ${effect.duration} 回合,
           ${effect.threshold} 以上傷害無效化`,
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
    if (this.targetCard) {
      this.targetAttr = this.targetCard.attr_id;
    } else {
      this.targetAttr = 0;
    }
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
        (v, i) => (v.effects[0][0] == 'VoidDamageShield' &&
                   this.passiveResistIndexes[i]))) {
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
    document.querySelector('filter-result').showLeaderSkill =
      this.showLeaderSkill;

    if (changed.size == 1 && changed.has('showLeaderSkill')) {
      return;
    }
    database.sort();
  }

  render() {
    const awakenings = [
      27, 30, /* two way, multi boost */
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, /* killers */
      43, 48, 50, 57, 58, 60, 61, 71, 72,
    ];
    return html`
      <link rel="stylesheet" type="text/css" href="css/base.css">
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
      <div class="card-title">
        Damage Parameters
      </div>
      <div class="card-body">
        <div id="awakenings" class="row icon-list flex-awakenings-list">
          ${awakenings.map((i) => this.awakeningCheckBox_(i))}
        </div>
        <div class="row">
          目標敵人ID:
          <input type="text" id="target" .value="${bind(this, 'target')}"
                 size="5" maxlength="5"
                 @focus="${(ev) => ev.target.select()}">
        </div>
        <fieldset style="${!this.targetCard ? 'display: none' : 'content'}">
          <legend> ${this.displayTargetName_()} </legend>
          <div class="row icon-list">
            屬性:
            ${[0, 1, 2, 3, 4].map((i) =>
              iconRadio('orb' + i, 'target-attr', i,
                        bindRadio(this, 'targetAttr'), 'number'))}
          </div>
          <div class="row">
            潛覺殺手:
            <input type="number" .value="${bind(this, 'latentKillerCount')}"
                   min="0" max="4" step="1" id="latent-killer-count"
                   @focus="${(ev) => ev.target.select()}"
                   >
          </div>
          ${this.targetCard ?
            this.targetCard.enemy_passive_resist.map(
                (skill, i) => html`
                  <div class="row">
                    ${this.displayPassiveResist_(skill, i)}
                  </div>`) :
            ''}
        </fieldset>
        <div class="row">
          ${toggleCheckbox('主副屬相同時加算副屬傷害',
                           bind(this, 'includeSubElemDamage'), false)}
        </div>
        <div class="row">
          ${toggleCheckbox('顯示隊長技',
                           bind(this, 'showLeaderSkill'), false)}
        </div>
        <div class="row">
          排序方式:
          ${radio('HP', 'sort-by', 'hp', bindRadio(this, 'sortBy'))}
          ${radio('攻擊', 'sort-by', 'atk', bindRadio(this, 'sortBy'))}
          ${radio('回復', 'sort-by', 'rcv', bindRadio(this, 'sortBy'))}
          ${radio('最小CD', 'sort-by', 'cd', bindRadio(this, 'sortBy'))}
          ${radio('自動回復', 'sort-by', 'extraheal', bindRadio(this, 'sortBy'))}
        </div>
      </div>
    `;
  }
}
customElements.define('atk-eval-config', AtkEvalConfig);

