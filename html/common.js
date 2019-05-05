import { css, unsafeCSS } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import { Awakening, awakeningDamageMultiplier } from './awakening.js'

function statAtMaxLv(card, name) {
  const max_v = card['max_' + name]
  const min_v = card['min_' + name]

  if (card.max_level == 1)
    return min_v
  return Math.round(max_v * (1 + card.limit_mult / 100.0))
}

function atkEval(card, config) {
  let atk = statAtMaxLv(card, 'atk') + 495

  card.awakenings.forEach(a => {
    if (a == Awakening.ENHANCED_ATK)
      atk += 100
  })

  let config_awakenings = new Set(config.awakenings)
  card.awakenings.forEach(a => {
    if (config_awakenings.has(a))
      atk *= awakeningDamageMultiplier(a)
  })

  if (!config.multi) {
    atk *= card.super_awakenings.reduce((x, a) => {
      if (config_awakenings.has(a))
        return Math.max(x, awakeningDamageMultiplier(a))
      return x
    }, 1)
  }

  atk *= config.elements[card.attr_id]

  if (config.includeSubElemDamage && card.attr_id == card.sub_attr_id)
    atk *= 1.1

  return Math.round(atk)
}

const ORB_CSS_ = Array(5).fill(0).map((_, i) =>
  css`.orb-${unsafeCSS(i)} {
    background-image: url(images/orb${unsafeCSS(i)}.png);
    background-size: contain;
    width: 24px;
    height: 24px;
    display: inline-block;
    vertical-align: middle;
  }`)

const AWAKENING_CSS_ = Array(65).fill(0).map((_, i) =>
  css`.awakening-${unsafeCSS(i)} {
    background-image: url(images/a${unsafeCSS(i)}.png);
    background-size: contain;
    width: 24px;
    height: 24px;
    display: inline-block;
    vertical-align: middle;
  }`)

const TYPE_CSS_ = Array(16).fill(1).map((_, i) =>
  css`.type-${unsafeCSS(i)} {
    background-image: url(images/t${unsafeCSS(i)}.png);
    background-size: contain;
    width: 24px;
    height: 24px;
    display: inline-block;
    vertical-align: middle;
  }`)

function assetsToIconCss() {
  return [
    ORB_CSS_,
    AWAKENING_CSS_,
    TYPE_CSS_,
    css`
      .orb--1, .awakening--1, .type--1 {
        width: 20px;
        height: 20px;
        display: inline-block;
      }
    `
  ]
}

export { statAtMaxLv, assetsToIconCss, atkEval }
