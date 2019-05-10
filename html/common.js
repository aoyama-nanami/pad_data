import {html, css, unsafeCSS} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {Awakening, awakeningDamageMultiplier} from './awakening.js';

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
    this.superAwakeningIndex = -1;
  }
}

export function atkEval(card, config) {
  let atk = statAtMaxLv(card, 'atk') + 495;
  let result = new AtkEvalResult()

  card.awakenings.forEach((a) => {
    if (a == Awakening.ENHANCED_ATK) {
      atk += 100;
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
  return result;
}

export function icon(prefix, id, cls) {
  return html`<div class="icon24x24 ${cls ? cls : ''}"
                   style="${iconCss(prefix, id)}"></div>`
}

export function iconCss(prefix, id) {
  return `background-image: url(images/${prefix}${id}.png)`
}
