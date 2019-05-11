#! /usr/bin/env python3

import unittest
from pad_data.common import Orb, Type
from pad_data import database
from pad_data import effect

# random selected golden data
class TestSkillData(unittest.TestCase):
    def setUp(self):
        self._db = database.Database()

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
            effect.AtkNuke(element=Orb.DARK,
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
            effect.AtkNuke(element=Orb.WOOD,
                           target=effect.Target.ONE,
                           hp_remain=50,
                           percentage=10000),
            effect.OrbChange(from_=[Orb.FIRE, Orb.DARK, Orb.JAMMER, Orb.POISON,
                                    Orb.MORTAL_POISON],
                             to=[Orb.WOOD]))

        # ラモット
        # no skill
        self.assert_skill_equal(1039)

        # 炎の番人
        self.assert_skill_equal(
            147,
            effect.DamageReduction(duration=3, percentage=50))

        # スサノオ
        self.assert_skill_equal(
            136,
            effect.DamageReduction(duration=5, percentage=50))

        # 奔放の緑龍契士・シルヴィ
        self.assert_skill_equal(
            3770,
            effect.AllOrbChange(orbs=[Orb.WOOD, Orb.LIGHT, Orb.HEART]),
            effect.ReduceCooldown(turn=[1, 1]))

        # ダルシム
        self.assert_skill_equal(
            5107,
            effect.Recovery(5, 0, 0, 0, 5),
            effect.OrbChange([Orb.LIGHT], [Orb.WATER]),
            effect.OrbChange([Orb.DARK], [Orb.FIRE]))

        # 最強装備・魔砲士
        self.assert_skill_equal(
            3218,
            effect.ComboIncrease(2, 1))

        # 曹操
        self.assert_skill_equal(
            1231,
            effect.DelayEnemyAttack(1, 0),
            effect.OrbChange([Orb.WATER], [Orb.FIRE]))

        # ヘラ・ベオーク
        self.assert_skill_equal(
            1188,
            effect.AllOrbChange([Orb.WOOD]))

        # ブラキオス
        self.assert_skill_equal(
            11,
            effect.ElementDamageBuff(2, [Orb.WOOD], 150),
            effect.AtkNuke(
                element=Orb.WOOD, percentage=2000, target=effect.Target.ALL))

        # 炎鎚のキリコ アナザー カード
        self.assert_skill_equal(
            1995,
            effect.AllOrbChange([Orb.FIRE, Orb.LIGHT, Orb.HEART]))

        # 大魔女の弟子・チェルン
        self.assert_skill_equal(
            4996,
            effect.ComboIncrease(1, 1),
            effect.Unlock(),
            effect.AllOrbChange([Orb.WATER, Orb.HEART]))

        # 水の精霊王・ザパン
        self.assert_skill_equal(
            4353,
            effect.OrbEnhance([Orb.WATER], unused=6),
            effect.SkyfallEnhancedOrbs(6, 50))

        # 転生アルレシャ
        self.assert_skill_equal(
            5044,
            effect.OrbChange(
                from_=[Orb.HEART, Orb.JAMMER, Orb.POISON, Orb.MORTAL_POISON],
                to=[Orb.WATER]),
            effect.OrbEnhance([Orb.WATER], unused=6),
            effect.ReduceCooldown([1, 1]))

        # 浄雷の赤龍契士・ガディウス
        self.assert_skill_equal(
            1947,
            effect.AllOrbChange([Orb.FIRE, Orb.LIGHT, Orb.DARK, Orb.HEART]),
            effect.ReduceCooldown([1, 1]))

        # プテラス
        self.assert_skill_equal(
            14,
            effect.AtkNuke(
                element=Orb.LIGHT, percentage=1000, target=effect.Target.ALL))

        # 響奏の愛猫神・バステト
        self.assert_skill_equal(
            888,
            effect.Cleave(3),
            effect.ElementDamageBuff(3, [Orb.WOOD], 115))

        # 英雄王・ギルガメッシュ
        self.assert_skill_equal(
            5010,
            effect.TypeDamageBuff(1, [Type.GOD], 500),
            effect.AtkNuke(
                element=Orb.NO_ORB, value=150000, target=effect.Target.ONE,
                ignore_def=True, repeat=5))

if __name__ == '__main__':
    unittest.main()
