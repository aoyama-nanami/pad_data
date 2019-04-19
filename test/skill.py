#! /usr/bin/env python3

import unittest
from pad_data.common import Element, Orb
from pad_data.database import Database
from pad_data import effect

# random selected golden data
class TestSkillData(unittest.TestCase):
    def setUp(self):
        self._db = Database()

    def assert_skill_equal(self, card_id, *effects):
        self.assertSequenceEqual(
            self._db.card(card_id).skill.effects, effects)

    def test_skill_effect(self):
        # 隠密御庭番衆御頭・四乃森蒼紫
        self.assert_skill_equal(
            3029,
            effect.Skyfall(2, [Orb.WATER], 15, 2),
            effect.RandomOrbSpawn(6, [Orb.WATER], [Orb.WATER]))

        # 生徒会長・ルシファー
        self.assert_skill_equal(
            2014,
            effect.AtkBasedDamage(element=Element.DARK,
                                  target=effect.Target.ONE,
                                  hp_remain=0,
                                  percentage=20000),
            effect.RandomOrbSpawn(6, [Orb.HEART], [Orb.DARK, Orb.HEART]))

        # ガンダー
        self.assert_skill_equal(
            4678,
            effect.RandomOrbSpawn(1, [Orb.FIRE], [Orb.FIRE]))

        # ライザー
        self.assert_skill_equal(
            4705,
            effect.AtkBasedDamage(element=Element.WOOD,
                                  target=effect.Target.ONE,
                                  hp_remain=50,
                                  percentage=10000),
            effect.OrbChange(from_=[Orb.FIRE, Orb.DARK, Orb.JAMMER, Orb.POISON,
                                    Orb.MORTAL_POISON],
                             to=[Orb.WOOD]))

        # ラモット
        # no skill means id=0 and other_fields=[0,0]
        self.assert_skill_equal(
            1039,
            effect.AtkBasedDamage(
                element=Element.FIRE, percentage=0, target=effect.Target.ALL))

        # 炎の番人
        self.assert_skill_equal(
            147,
            effect.DamageReduction(duration=3, percentage=50))

if __name__ == '__main__':
    unittest.main()
