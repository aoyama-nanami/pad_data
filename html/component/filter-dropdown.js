import {css, html, LitElement} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';

import {Awakening} from '../util/awakening.js';

import {FilterAssist} from '../filters/assist.js';
import {FilterAwakening} from '../filters/awakening.js';
import {FilterElement} from '../filters/element.js';
import {FilterSkillCd} from '../filters/skill-cd.js';

import {FilterAllOrbChange} from '../filters/all-orb-change.js';
import {FilterCombo} from '../filters/combo.js';
import {FilterDelayEnemyAttack} from '../filters/delay-enemy-attack.js';
import {FilterDefenseReduction} from '../filters/defense-reduction.js';
import {FilterDmgBuff} from '../filters/dmg-buff.js';
import {FilterGravity} from '../filters/gravity.js';
import {FilterLowHpNuke} from '../filters/low-hp-nuke.js';
import {FilterNuke} from '../filters/nuke.js';
import {FilterOrbChange} from '../filters/orb-change.js';
import {FilterRandomOrbSpawn} from '../filters/random-orb-spawn.js';
import {FilterReduceCooldown} from '../filters/reduce-cooldown.js';
import {FilterSacrifice} from '../filters/sacrifice.js';
import {FilterType} from '../filters/type.js';

export const FILTERS = [
  [
    {
      desc: '',
    },
    {
      desc: '無效貫通',
      cls: FilterAwakening,
      init: {
        awakenings: [[Awakening.VOID_DAMAGE_PIERCER, 1]],
        count: 1,
      },
    },
    {
      desc: '主屬',
      cls: FilterElement,
      init: {main: true},
    },
    {
      desc: '副屬',
      cls: FilterElement,
      init: {sub: true},
    },
    {
      desc: '主或副屬',
      cls: FilterElement,
      init: {main: true, sub: true},
    },
    {
      desc: 'Type',
      cls: FilterType,
    },
    {
      desc: '操作時間延長',
      cls: FilterAwakening,
      init: {
        awakenings: [[Awakening.EXTEND_TIME, 1], [Awakening.EXTEND_TIME_PLUS, 2]],
        canEdit: true,
      },
    },
    {
      desc: 'Skill Boost',
      cls: FilterAwakening,
      init: {
        awakenings: [[Awakening.SKILL_BOOST, 1], [Awakening.SKILL_BOOST_PLUS, 2]],
        canEdit: true,
      },
    },
    {
      desc: '五色破防',
      cls: FilterAwakening,
      init: {
        awakenings: [[Awakening.GUARD_BREAK, 1]],
        count: 1,
      },
    },
    {
      desc: '可裝備',
      cls: FilterAssist,
    },
    {
      desc: '技能 CD',
      cls: FilterSkillCd,
    },
  ],
  [
    {
      desc: '主動技',
    },
    {
      desc: '大砲',
      cls: FilterNuke,
    },
    {
      desc: '低血砲',
      cls: FilterLowHpNuke,
    },
    {
      desc: '自殘',
      cls: FilterSacrifice,
    },
    {
      desc: '轉珠',
      cls: FilterOrbChange,
    },
    {
      desc: '重力',
      cls: FilterGravity,
    },
    {
      desc: '真重力',
      cls: FilterGravity,
      init: {trueGravity: true},
    },
    {
      desc: '屬性/type 增傷',
      cls: FilterDmgBuff,
    },
    {
      desc: '陣',
      cls: FilterAllOrbChange,
    },
    {
      desc: '隨機產生寶珠',
      cls: FilterRandomOrbSpawn,
    },
    {
      desc: 'combo 增加',
      cls: FilterCombo,
    },
    {
      desc: '降防',
      cls: FilterDefenseReduction,
    },
    {
      desc: '技能 CD 減少',
      cls: FilterReduceCooldown,
    },
    {
      desc: '威嚇',
      cls: FilterDelayEnemyAttack,
    },
  ]
];

export function FilterById(id) {
  for (const arr of FILTERS) {
    for (const spec of arr) {
      if (spec.desc == id)
        return spec;
    }
  }
  return FILTERS[0][0];
}

class FilterDropdown extends LitElement {
  static get properties() {
    return {
      value: {type: Number},
      opened: {type: Boolean},
    };
  }

  static get styles() {
    return css`
      .dropdown {
        color: rgb(226, 226, 226);
        height: 16px;
        position: relative;
      }

      input {
        width: 100px;
        padding-left: 3px;
      }

      .dropdown-closed {
        display: none;
      }

      .dropdown-opened {
        background-color: rgb(33, 33, 33);
        line-height: 1.4;
        font-size: 0.9rem;
        display: flex;
        position: absolute;
        top: 22px;
        left: 0px;
        z-index: 9999;
        box-shadow: 3px 3px 3px rgba(0, 0, 0, 0.5);
      }

      ul {
        display: block;
        padding: 0 0 0 0;
        margin: 5px 5px 5px 5px;
        white-space: nowrap;
      }

      li {
        list-style-type: none;
        display: block;
        cursor: default;
        padding-left: 3px;
        padding-right: 20px;
        padding-top: 3px;
        white-space: nowrap;
      }

      li:not(:first-child):hover, li.selected {
        background-color: rgba(161, 194, 250, 0.2);
      }

      li:first-child {
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid #DDD;
        height: 1.5rem;
      }
    `;
  }

  listItem(spec, index) {
    const id = spec.desc;
    if (index == 0) { // header
      return html`<li>${id}</li>`
    }
    return html`
      <li
        @mousedown="${(ev) => {this.value = id}}"
        class="${id == this.value ? 'selected' : ''}">
        ${id}
      </li>`
  }

  render() {
    const v = this.value || '';
    return html`
      <link rel="stylesheet" type="text/css" href="style.css">
      <div class="dropdown"
           @focusin="${() => this.opened = true}"
           @focusout="${() => this.opened = false}">
        <input type="text" value="${v}" readonly>
        <div class="dropdown-${this.opened ? 'opened' : 'closed'}">
          <ul>
            ${FILTERS[0].map((x, i) => this.listItem(x, i))}
          </ul>
          <ul>
            ${FILTERS[1].map((x, i) => this.listItem(x, i))}
          </ul>
        </div>
      </div>
    `;
  }

  updated(changedProperties) {
    if (changedProperties.has('value')) {
      this.dispatchEvent(new CustomEvent('change'));
    }
  }
};
customElements.define('filter-dropdown', FilterDropdown);
