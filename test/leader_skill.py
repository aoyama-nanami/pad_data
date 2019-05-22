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
            LS.Rainbow(orbs=_FIVE_COLOR, color_min=4, atk=350, dr=25))

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
            LS.Rainbow(orbs=_FIVE_COLOR, color_min=4, atk=400))

        # ウミキキヤマララ
        self.assert_skill_equal(
            5281,
            LS.Board7x6(elements=[Orb.WATER, Orb.LIGHT], hp=150, atk=150,
                        rcv=150),
            LS.Rainbow(orbs=[Orb.WATER, Orb.WOOD, Orb.LIGHT, Orb.DARK],
                       color_min=4, atk=600))

        # 人斬りの妻・雪代巴
        self.assert_skill_equal(
            4003,
            LS.StatBoost(types=[Type.BALANCE], atk=300),
            LS.CrossAtkBoost(args=[[Orb.LIGHT, 200]]))

        # セイレーン
        self.assert_skill_equal(91, LS.ExtraHeal(100))

        # ホノピィ
        # スキルレベルアップ・火
        self.assert_skill_equal(1547, LS.Dummy())

        # 神理の裁断者・メタトロン
        self.assert_skill_equal(
            3535,
            LS.NoSkyfall(types=[Type.GOD], hp=150, atk=150, rcv=150),
            LS.HpBelow(hp_below=80, types=[Type.GOD], atk=600))

        # 虹石龍・オリハルコン
        self.assert_skill_equal(
            740,
            LS.StatBoost(dr_elements=[Orb.WATER, Orb.LIGHT], dr=50))

        # キム・カッファン
        self.assert_skill_equal(
            4106,
            LS.ElementCombo(combos=[[Orb.WOOD]] * 3, combo_min=2, atk=150,
                            atk_step=50),
            LS.Combo(combo=5, combo_max=7, atk=200, atk_step=100))

        # 転生カリン
        self.assert_skill_equal(
            3488,
            LS.StatBoost(dr=30),
            LS.Rainbow(orbs=[Orb.WATER, Orb.WOOD, Orb.DARK], color_min=2,
                       atk=450))

        # ホノぷれドラ
        # ポイント還元・極少
        self.assert_skill_equal(2299, LS.Dummy())

        # 双天の皇祖神・イザナギ
        self.assert_skill_equal(
            2281,
            LS.HpAbove(hp_above=80, types=[Type.GOD], atk=350),
            LS.ElementCombo(combos=[[Orb.LIGHT]] * 3, combo_min=2, atk=200,
                            atk_step=100))

        # 霧沢風子
        self.assert_skill_equal(
            2470,
            LS.ConnectedOrbs(orbs=[Orb.WOOD], size=4, atk=200))

        # 裁魂冥穣神・オシリス
        self.assert_skill_equal(
            2386,
            LS.StatBoost(elements=[Orb.WOOD], hp=135, rcv=135),
            LS.Combo(combo=6, atk=350))

        # ドット・クラウド
        self.assert_skill_equal(
            3808,
            LS.StatBoost(types=[Type.PHYSICAL, Type.ATTACK], hp=200, atk=200),
            LS.ConnectedOrbs(orbs=[Orb.LIGHT], size=6, size_max=9, atk=350,
                             atk_step=50))

        # 秘神・オーディン
        self.assert_skill_equal(
            364,
            LS.StatBoost(types=[Type.GOD], atk=250))

        # 覚醒ネフティス
        self.assert_skill_equal(
            4282,
            LS.StatBoost(elements=[Orb.DARK], hp=150, atk=150, rcv=150),
            LS.HpAbove(hp_above=100, atk=300),
            LS.Rainbow(orbs=_SIX_COLOR, color_min=3, atk=300))

        # 焔剣リオレウス
        self.assert_skill_equal(4139)

        # 覚醒イシス
        self.assert_skill_equal(
            2010,
            LS.Rainbow(orbs=_FIVE_COLOR, color_min=3, atk=300),
            LS.Trigger(elements=[Orb.WATER], atk=150))

        # 神王妃・ミニへら
        self.assert_skill_equal(
            2315,
            LS.StatBoost(types=[Type.GOD], rcv=150),
            LS.HpAbove(hp_above=50, types=[Type.DEMON], atk=350))

        # 雷光の巨漢・サイクロプス
        self.assert_skill_equal(
            794,
            LS.StatBoost(elements=[Orb.LIGHT], atk=150, rcv=150))

        # バルボワ
        self.assert_skill_equal(
            2944,
            LS.StatBoost(elements=[Orb.WOOD], atk=200, rcv=200),
            LS.ElementCombo(combos=[[Orb.WOOD], [Orb.WATER]], combo_min=2,
                            atk=300))

        # ヴァンパイア
        self.assert_skill_equal(110)

        # キン肉マンのマスク
        self.assert_skill_equal(5306)

        # 第10の使徒・戦闘形態
        self.assert_skill_equal(712, LS.StatBoost(dr=20))

        # 俊才の臥龍神・ミニ諸葛亮
        self.assert_skill_equal(
            1715,
            LS.HpBelow(hp_below=80, elements=[Orb.WOOD], atk=300))

        # 黄金聖闘士・アフロディーテ
        self.assert_skill_equal(
            1456,
            LS.StatBoost(elements=[Orb.WATER], atk=200))

        # 覚醒馬超
        self.assert_skill_equal(
            4582,
            LS.Board7x6(),
            LS.Combo(combo=8, atk=200, rcv=150),
            LS.Rainbow(orbs=[Orb.WATER, Orb.WOOD, Orb.LIGHT], color_min=3,
                       atk=400, dr=25))

        # サンダーギア
        self.assert_skill_equal(2198)

        # 紅天の果実・いちごドラゴン
        self.assert_skill_equal(
            1076,
            LS.StatBoost(elements=[Orb.FIRE], hp=200, rcv=200))

        # アパンダ
        self.assert_skill_equal(
            462,
            LS.Counter(proc_rate=50, atk=500, orb=Orb.FIRE))

        # 聖天使・アリエル
        self.assert_skill_equal(
            1832,
            LS.StatBoost(types=[Type.ATTACK], hp=125, atk=125),
            LS.ElementCombo(combos=[[Orb.FIRE], [Orb.LIGHT], [Orb.LIGHT]],
                            combo_min=2, atk=300))


if __name__ == '__main__':
    unittest.main()
