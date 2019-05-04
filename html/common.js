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

  return Math.round(atk)
}

const ORB_CSS_ = Array(5).fill(0).map((_, i) =>
  css`
    .orb-${unsafeCSS(i)} {
      background-image: url(images/orb${unsafeCSS(i)}.png);
      background-size: contain;
      width: 30px;
      height: 30px;
      display: inline-block;
    }
  `)

/*
 * starting coord: (613, 109), padding 36
 */
function offset_(i) {
  i += 9;
  let pos = []
  for (let j = 0; j < 11; j++) {
    let width = 11 - j
    if (i < width) {
      pos = [j, j + i]
      break
    }
    if (i < width * 2 - 1) {
      i -= width
      pos = [j + i + 1, j]
      break
    }
    i -= width * 2 - 1
  }
  return [-(613 + 36 * pos[0]), -(109 + 36 * pos[1])]
}

function offsetX_(i) {
  let [x, y] = offset_(i);
  return x;
}

function offsetY_(i) {
  let [x, y] = offset_(i);
  return y;
}

const AWAKENING_CSS_ = Array(65).fill(0).map((_, i) =>
  css`.awakening-${unsafeCSS(i)} {
    background-image: url(images/eggs.png);
    background-position: ${unsafeCSS(offsetX_(i))}px
      ${unsafeCSS(offsetY_(i))}px;
    width: 32px;
    height: 32px;
    display: inline-block;
  }`)


function assetsToIconCss() {
  return [
    ORB_CSS_,
    AWAKENING_CSS_,
    css`
      .orb--1, .awakening--1 {
        width: 30px;
        height: 30px;
        display: inline-block;
      }
    `
  ]
}

export { statAtMaxLv, assetsToIconCss, atkEval }
