#! /usr/bin/env python3

import unittest
from pad_data.common import Orb, Type
from pad_data import database
from pad_data.leader_skill import effect as LS

_FIVE_COLOR = [Orb.FIRE, Orb.WATER, Orb.WOOD, Orb.LIGHT, Orb.DARK]
_SIX_COLOR = _FIVE_COLOR + [Orb.HEART]

# random selected golden data
class TestSkillData(unittest.TestCase):
    def setUp(self):
        self._db = database.Database()
        # pylint: disable=invalid-name
        self.maxDiff = None

    def assert_skill_equal(self, card_id, *effects):
        self.assertSequenceEqual(
            self._db.card(card_id).leader_skill.effects, effects)

    def test_skill_effect(self):
        # 黃角的天鬼姬・雷神
        self.assert_skill_equal(
            3416,
            LS.StatBoost(types=[Type.ATTACK], atk=300),
            LS.Rainbow(elements=_FIVE_COLOR, color_min=4, atk=350, dr=25))

        # 五機龍融合・デモンハダル
        self.assert_skill_equal(
            1207,
            LS.StatBoost(elements=[Orb.DARK], types=[Type.MACHINE], atk=250),
            LS.StatBoost(types=[Type.MACHINE], hp=150))

        # オレンジマテリアル
        self.assert_skill_equal(3219)

        # ダークドラゴンナイト
        self.assert_skill_equal(
            109,
            LS.StatBoost(dr_elements=[Orb.DARK], dr=30))

        # 麗乙女・プリンセスヴァルキリー
        self.assert_skill_equal(
            972,
            LS.StatBoost(types=[Type.HEALER], atk=250))

        # 初陽の蒼空神・ケプリ
        self.assert_skill_equal(
            4130,
            LS.OrbRemaining(threshold=7, atk=400),
            LS.Rainbow(elements=_FIVE_COLOR, color_min=4, atk=400))

        # ウミキキヤマララ
        self.assert_skill_equal(
            5281,
            LS.Board7x6(elements=[Orb.WATER, Orb.LIGHT], hp=150, atk=150,
                        rcv=150),
            LS.Rainbow(elements=[Orb.WATER, Orb.WOOD, Orb.LIGHT, Orb.DARK],
                       color_min=4, atk=600))

if __name__ == '__main__':
    unittest.main()
