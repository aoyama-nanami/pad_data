import { Awakening } from './awakening.js'

export const Type = {
    EVOLVE_MATERIAL: 0,
    BALANCE: 1,
    PHYSICAL: 2,
    HEALER: 3,
    DRAGON: 4,
    GOD: 5,
    ATTACK: 6,
    DEMON: 7,
    MACHINE: 8,
    AWAKEN_MATERIAL: 12,
    ENHANCE_MATERIAL: 14,
    VENDOR_MATERIAL: 15,
}

const typeToKillerMap_ = []
const TypeReverse = {}
Object.keys(Type).forEach(k =>
  typeToKillerMap_[Type[k]] = Awakening[k + '_KILLER'])

export function typeToKiller(t) {
  return typeToKillerMap_[t]
}
