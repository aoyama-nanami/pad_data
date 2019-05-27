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

class AtkEvalResult {
  constructor() {
    this.atk = 0;
    this.subAtk = 0;
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
  const result = new AtkEvalResult();

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
  const result = new AtkEvalResult();
  let atk = statAtMaxLv(card, 'atk') + 495;
  let rcv = statAtMaxLv(card, 'rcv') + 297;

  card.awakenings.forEach((a) => {
    if (a == Awakening.ENHANCED_ATK) {
      atk += 100;
    } else if (a == Awakening.ENHANCED_RCV) {
      rcv += 200;
    }
  });

  card.awakenings.forEach((a) => {
    if (config.awakenings.has(a)) {
      atk *= awakeningDamageMultiplier(a);
    }
  });

  if (!config.multi) {
    let max = 1;
    card.super_awakenings.forEach((a, i) => {
      if (config.awakenings.has(a)) {
        if (awakeningDamageMultiplier(a) > max) {
          result.superAwakeningIndex = i;
          max = awakeningDamageMultiplier(a);
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
