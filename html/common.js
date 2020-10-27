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

export function statEval(card, allowed_super_awakenings, config) {
  const result = new EvalResult();
  let hp = statAtMaxLv(card, 'hp') + 990;
  let atk = statAtMaxLv(card, 'atk') + 495;
  let rcv = statAtMaxLv(card, 'rcv') + 297;

  let has_skill_voice = card.awakenings.indexOf(Awakening.SKILL_VOICE) != -1;
  if (has_skill_voice) {
    hp += Math.round(statAtMaxLv(card, 'hp') * 0.1);
    atk += Math.round(statAtMaxLv(card, 'atk') * 0.1);
    rcv += Math.round(statAtMaxLv(card, 'rcv') * 0.1);
  }

  if (config.sortBy == 'rcv') {
    let latent_slot = card.extra_latent_slot ? 4 : 3;
    rcv += Math.round(statAtMaxLv(card, 'rcv') * 0.3 * latent_slot);
  } else if (config.sortBy == 'extraheal') {
    let latent_slot = card.extra_latent_slot ? 4 : 3;
    rcv += Math.round(statAtMaxLv(card, 'rcv') * 0.3 * latent_slot);

    let ls = card.leader_skill.effects.find(([type, effect]) => {
      return type == 'ExtraHeal';
    });
    if (!ls) {
      rcv = 0;
    } else {
      let effect = ls[1];
      rcv *= effect.rcv / 100;
    }
  }

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
    const idx = allowed_super_awakenings.find(
        (i) => card.super_awakenings[i] == Awakening.ENHANCED_HEART_ORB);
    if (config.sortBy == 'rcv' && idx !== undefined) {
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
      let [vMax, iMax] = allowed_super_awakenings.map((i) => {
        let a = card.super_awakenings[i];

        if (config.awakenings.has(a)) {
          let m = awakeningDamageMultiplier(a);
          switch (a) {
            case Awakening.EIGHTY_HP_ENHANCED:
              return [m * atk80, i];
            case Awakening.FIFTY_HP_ENHANCED:
              return [m * atk50, i];
            default:
              return [m * Math.max(atk80, atk50), i];
          }
        }
        return [Math.max(atk80, atk50), i]
      }).reduce(([vMax, iMax], [vCur, iCur]) => {
        if (vCur > vMax || vCur == vMax && iMax < 0)
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

  if (config.latentKillerCount) {
    var latentKillerCount = config.latentKillerCount;
    if (!card.extra_latent_slot) {
      latentKillerCount = Math.min(latentKillerCount, 3);
    }
    if (card.type.some((x) => config.latentKillerTypes.has(x))) {
      atk *= Math.pow(1.5, latentKillerCount);
    }
  }

  if (card.attr_id != 6) {
    atk *= config.elements[card.attr_id];
    if (config.includeSubElemDamage && card.attr_id == card.sub_attr_id) {
      atk *= 1.1;
    }
  } else {
    atk *= config.elements[card.sub_attr_id];
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
