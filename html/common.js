import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
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
    this.atk = 0;
    this.rcv = 0;
    this.superAwakeningIndex = -1;
  }
}

export function statEval(card, config) {
  if (config.sortBy == 'rcv') {
    return rcvEval(card, config);
  }
  return atkEval(card, config);
}

function rcvEval(card, config) {
  let atk = statAtMaxLv(card, 'atk') + 495;
  let rcv = statAtMaxLv(card, 'rcv') * 1.9 + 297;
  const result = new EvalResult();

  card.awakenings.forEach((a) => {
    if (a == Awakening.ENHANCED_ATK) {
      atk += 100;
    } else if (a == Awakening.ENHANCED_RCV) {
      rcv += 200;
    }
  });

  card.awakenings.forEach((a) => {
    if (a == Awakening.ENHANCED_HEART_ORB) {
      rcv *= 1.5;
    } else if (a == Awakening.MULTI_BOOST && config.multi) {
      rcv *= 1.5;
    }
  });

  if (!config.multi) {
    const idx = card.super_awakenings.findIndex(
      (a) => a == Awakening.ENHANCED_HEART_ORB);
    if (idx >= 0) {
      result.superAwakeningIndex = idx;
      rcv *= 1.5;
    }
  }

  result.atk = Math.round(atk);
  result.rcv = Math.round(rcv);
  return result;
}

function atkEval(card, config) {
  const result = new EvalResult();
  let atk = statAtMaxLv(card, 'atk') + 495;
  let rcv = statAtMaxLv(card, 'rcv') + 297;

  card.awakenings.forEach((a) => {
    if (a == Awakening.ENHANCED_ATK) {
      atk += 100;
    } else if (a == Awakening.ENHANCED_RCV) {
      rcv += 200;
    }
  });

  let atk_80 = 1, atk_50 = 1;
  card.awakenings.forEach((a) => {
    if (config.awakenings.has(a)) {
      let m = awakeningDamageMultiplier(a);
      switch (a) {
        case Awakening.EIGHTY_HP_ENHANCED:
          atk_80 *= m;
          break;
        case Awakening.FIFTY_HP_ENHANCED:
          atk_50 *= m;
          break;
        default:
          atk_80 *= m;
          atk_50 *= m;
      }
    }
  });

  if (config.multi) {
    atk *= Math.max(atk_80, atk_50);
  } else {
    let max = Math.max(atk_80, atk_50);
    card.super_awakenings.forEach((a, i) => {
      if (config.awakenings.has(a)) {
        let m = awakeningDamageMultiplier(a);
        switch (a) {
          case Awakening.EIGHTY_HP_ENHANCED:
            m *= atk_80;
            break;
          case Awakening.FIFTY_HP_ENHANCED:
            m *= atk_50;
            break;
          default:
            m *= Math.max(atk_80, atk_50);
        }

        if (m > max) {
          result.superAwakeningIndex = i;
          max = m
        }
      }
    });
    atk *= max;
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
