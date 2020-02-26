import {html} from './util/external_lib.js';
import {Awakening, awakeningDamageMultiplier} from './util/awakening.js';

export function statAtMaxLv(card, name) {
  const maxValue = card['max_' + name];
  const minValue = card['min_' + name];

  if (card.max_level == 1) {
    return minValue;
  }
  return Math.round(maxValue * (1 + card.limit_mult / 100.0));
}

class EvalResult {
  constructor() {
    this.hp = 0;
    this.atk = 0;
    this.rcv = 0;
    this.superAwakeningIndex = -1;
  }
}

export function statEval(card, config) {
  const result = new EvalResult();
  let hp = statAtMaxLv(card, 'hp') + 990;
  let atk = statAtMaxLv(card, 'atk') + 495;
  let rcv = statAtMaxLv(card, 'rcv') * (config.sortBy == 'rcv' ? 1.9 : 1) + 297;

  card.awakenings.forEach((a) => {
    if (a == Awakening.ENHANCED_HP) {
      hp += 500;
    } else if (a == Awakening.ENHANCED_ATK) {
      atk += 100;
    } else if (a == Awakening.ENHANCED_RCV) {
      rcv += 200;
    }
  });

  let atk80 = 1, atk50 = 1;
  card.awakenings.forEach((a) => {
    if (config.awakenings.has(a)) {
      let m = awakeningDamageMultiplier(a);
      switch (a) {
        case Awakening.EIGHTY_HP_ENHANCED:
          atk80 *= m;
          break;
        case Awakening.FIFTY_HP_ENHANCED:
          atk50 *= m;
          break;
        case Awakening.MULTI_BOOST:
          hp *= m;
          rcv *= m;
          // fall through
        default:
          atk80 *= m;
          atk50 *= m;
      }
    } else if (config.sortBy == 'rcv' && a == Awakening.ENHANCED_HEART_ORB) {
      rcv *= 1.5;
    }
  });

  if (config.multi) {
    atk *= Math.max(atk80, atk50);
  } else {
    const idx = card.super_awakenings.indexOf(Awakening.ENHANCED_HEART_ORB);
    if (config.sortBy == 'rcv' && idx >= 0) {
      /*
       * If super awakenings contains heart+ and we are sorting by rcv,
       * pick heart+.
       */
      result.superAwakeningIndex = idx;
      rcv *= 1.5;
      atk *= Math.max(atk80, atk50);
    } else {
      /*
       * Otherwise, pick the highest damage option.
       */
      let [vMax, iMax] = card.super_awakenings.map(a => {
        if (config.awakenings.has(a)) {
          let m = awakeningDamageMultiplier(a);
          switch (a) {
            case Awakening.EIGHTY_HP_ENHANCED:
              return m * atk80;
            case Awakening.FIFTY_HP_ENHANCED:
              return m * atk50;
            default:
              return m * Math.max(atk80, atk50);
          }
        }
        return Math.max(atk80, atk50);
      }).reduce(([vMax, iMax], vCur, iCur) => {
        if (vCur > vMax)
          return [vCur, iCur];
        return [vMax, iMax];
      }, [Math.max(atk80, atk50), -1]);

      atk *= vMax;
      result.superAwakeningIndex = iMax;
    }
  }

  config.types.forEach((a) => {
    if (card.type.some((x) => a[0].has(x))) {
      atk *= a[1];
    }
  });

  atk *= config.elements[card.attr_id];
  if (config.includeSubElemDamage && card.attr_id == card.sub_attr_id) {
    atk *= 1.1;
  }

  result.hp = Math.round(hp);
  result.atk = Math.round(atk);
  result.rcv = Math.round(rcv);
  return result;
}

export function icon(iconName, extraClass) {
  return html`<div class="icon24x24 ${extraClass ? extraClass : ''}"
                   style="${iconCss(iconName)}"></div>`;
}

function iconCss(iconName) {
  return `background-image: url(images/${iconName}.png)`;
}
