#! /usr/bin/env python3

import unittest
from pad_data import database
# pylint: disable=wildcard-import,unused-wildcard-import
from pad_data.util.global_enums import *

class TestCardData(unittest.TestCase):
    def setUp(self) -> None:
        self._db = database.Database()

    def test_stat_calculation_1(self) -> None:
        # 蒼刻の魔導姫・アルス＝パウリナ
        card = self._db.card(1752)
        self.assertEqual(card.atk_at_level(1), 787)
        self.assertEqual(card.atk_at_level(99), 1217)
        self.assertEqual(card.atk_at_level(43), 1025)
        with self.assertRaises(ValueError):
            card.atk_at_level(110)

    def test_stat_calculation_2(self) -> None:
        # 転生イシス
        card = self._db.card(3383)
        self.assertEqual(card.hp_at_level(1), 1719)
        self.assertEqual(card.hp_at_level(90), 3825)
        self.assertEqual(card.hp_at_level(99), 4038)
        self.assertEqual(card.hp_at_level(103), 4185)
        self.assertEqual(card.hp_at_level(110), 4442)

    def test_stat_calculation_3(self) -> None:
        # 炎の番人
        card = self._db.card(147)
        self.assertEqual(card.hp_at_level(), 1031)
        self.assertEqual(card.atk_at_level(), 331)
        self.assertEqual(card.rcv_at_level(), 83)

    def test_awakening(self) -> None:
        self.assertSequenceEqual(
            self._db.card(1).awakenings, [SKILL_BOOST, SKILL_BOOST])

        self.assertSequenceEqual(
            self._db.card(651).awakenings,
            [ENHANCED_HP, ENHANCED_RCV, SKILL_BOOST])

        self.assertSequenceEqual(
            self._db.card(2895).awakenings,
            [TWO_WAY, SKILL_BOOST, AUTO_RECOVER])

        self.assertSequenceEqual(
            self._db.card(2895).super_awakenings, [])

        self.assertSequenceEqual(
            self._db.card(4897).awakenings,
            [AWOKEN_ASSIST, RESIST_DARK, RESIST_JAMMERS,
             RESIST_POISON, EXTEND_TIME])

        self.assertSequenceEqual(
            self._db.card(3764).awakenings,
            [TWO_WAY, SKILL_BOOST, ENHANCED_WATER_ORB,
             RESIST_SKILL_BIND, ENHANCED_WATER_ORB, ENHANCED_HEART_ORB,
             BONUS_ATTACK, ENHANCED_COMBO, ENHANCED_COMBO])

        self.assertSequenceEqual(
            self._db.card(4419).awakenings,
            [EXTEND_TIME, SKILL_BOOST, EIGHTY_HP_ENHANCED,
             SUPER_BONUS_ATTACK, SUPER_BONUS_ATTACK, MULTI_BOOST])

        self.assertSequenceEqual(
            self._db.card(5101).awakenings,
            [AWOKEN_ASSIST, RESIST_CLOUD, ENHANCED_TEAM_HP,
             ENHANCED_TEAM_RCV, ENHANCED_HP])

        self.assertSequenceEqual(
            self._db.card(4780).awakenings,
            [RESIST_BIND_PLUS, L_ATTACK, SKILL_BOOST, GUARD_BREAK,
             REDUCE_FIRE_DMG, REDUCE_WATER_DMG, REDUCE_WOOD_DMG,
             REDUCE_LIGHT_DMG, REDUCE_DARK_DMG])

        self.assertSequenceEqual(
            self._db.card(3870).awakenings,
            [AUTO_RECOVER, AUTO_RECOVER, RECOVER_BIND,
             RESIST_BIND, RESIST_BIND, VOID_DAMAGE_PIERCER,
             ENHANCED_HEART_ORB, ENHANCED_HEART_ORB])

        self.assertSequenceEqual(
            self._db.card(3268).awakenings,
            [GOD_KILLER, DRAGON_KILLER, DEMON_KILLER, MACHINE_KILLER,
             BALANCE_KILLER, ATTACK_KILLER, PHYSICAL_KILLER, HEALER_KILLER])

        self.assertSequenceEqual(
            self._db.card(3094).awakenings,
            [ENHANCED_DARK_ORB, ENHANCED_DARK_ORB, ENHANCED_DARK_ORB,
             ENHANCED_DARK_ORB, ENHANCED_DARK_ORB, EVOLVE_MATERIAL_KILLER,
             AWAKEN_MATERIAL_KILLER, ENHANCE_MATERIAL_KILLER,
             VENDOR_MATERIAL_KILLER])

        self.assertSequenceEqual(
            self._db.card(4650).awakenings,
            [RESIST_BIND, RESIST_BIND, EXTEND_TIME_PLUS, SKILL_BOOST_PLUS,
             RESIST_SKILL_BIND, ENHANCED_DARK_ATTR, ENHANCED_DARK_ATTR,
             ENHANCED_DARK_ATTR, COMBO_DROP])

        self.assertSequenceEqual(
            self._db.card(4799).awakenings,
            [RESIST_BIND_PLUS, SKILL_BOOST, SKILL_BOOST, FIFTY_HP_ENHANCED,
             FIFTY_HP_ENHANCED, FIFTY_HP_ENHANCED, BONUS_ATTACK,
             EXTEND_TIME_PLUS, SKILL_VOICE])

    def test_type(self) -> None:
        self.assertSequenceEqual(self._db.card(4831).type,
                                 (DRAGON, DEMON, NO_TYPE))
        self.assertSequenceEqual(self._db.card(232).type,
                                 (GOD, BALANCE, NO_TYPE))
        self.assertSequenceEqual(self._db.card(4839).type,
                                 (GOD, ATTACK, PHYSICAL))
        self.assertSequenceEqual(self._db.card(4027).type,
                                 (HEALER, MACHINE, NO_TYPE))
        self.assertSequenceEqual(self._db.card(5198).type,
                                 (EVOLVE_MATERIAL, ENHANCE_MATERIAL, NO_TYPE))
        self.assertSequenceEqual(self._db.card(5055).type,
                                 (AWAKEN_MATERIAL, ENHANCE_MATERIAL,
                                  VENDOR_MATERIAL))

if __name__ == '__main__':
    unittest.main()
