import re
import unittest
from pathlib import Path


PATCH_ROOT = Path(
    r"E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods"
    r"\zzz_mcm_cn_installed_mods_patch"
)


class McmChinesePatchTests(unittest.TestCase):
    def test_patch_mod_files_exist(self):
        expected_files = [
            "metadata.xml",
            "main.lua",
            r"scripts\mcm_cn_patch\loader.lua",
            r"scripts\mcm_cn_patch\translations.lua",
        ]

        for relative_path in expected_files:
            with self.subTest(relative_path=relative_path):
                self.assertTrue(
                    (PATCH_ROOT / relative_path).is_file(),
                    f"missing patch file: {relative_path}",
                )

    def test_loader_uses_mcm_chinese_api_safely(self):
        loader = (PATCH_ROOT / r"scripts\mcm_cn_patch\loader.lua").read_text(
            encoding="utf-8"
        )

        self.assertIn('mcm.i18n ~= "Chinese"', loader)
        self.assertIn("GetCategoryIDByName", loader)
        self.assertIn("GetSubcategoryIDByName", loader)
        self.assertIn("categoryExists", loader)
        self.assertIn("subcategoryExists", loader)
        self.assertIn("MC_POST_UPDATE", loader)
        self.assertNotRegex(
            loader,
            r"GetSubcategoryOptions\s*\(",
            "loader should not call APIs that create missing subcategories",
        )

    def test_translations_cover_installed_mcm_categories(self):
        translations = (
            PATCH_ROOT / r"scripts\mcm_cn_patch\translations.lua"
        ).read_text(encoding="utf-8")

        expected_categories = [
            "Coming Down!",
            "Dark Esau Helper",
            "EID",
            "Less Annoying Golden Pennies",
            "Penetration Up!",
            "Wave Counter",
            "Curse Settings",
            "Better Collision",
            "Dream Recorder",
            "Detailed Respawn",
            "GoodTrip [Fixed]",
            "Minimap API",
            "Missing Item Chargebars",
            "Mom's Foot Reminder",
            "Range fix for Bones & Sword",
            "Secret Room Hint",
            "Stats+",
            "Watch out, explosion!",
            "Watch out, laser!",
        ]

        for category in expected_categories:
            with self.subTest(category=category):
                escaped = re.escape(f'["{category}"]')
                self.assertRegex(translations, escaped)

        self.assertIn("displayPatterns", translations)
        self.assertIn("infoText", translations)
        self.assertIn("popupPatterns", translations)

    def test_isaac_terms_are_consistent(self):
        translations = (
            PATCH_ROOT / r"scripts\mcm_cn_patch\translations.lua"
        ).read_text(encoding="utf-8")

        preferred_terms = [
            "黑暗以扫",
            "Boss Rush",
            "迷宫诅咒",
            "失明诅咒",
            "隐藏房",
            "超级隐藏房",
            "究极隐藏房",
            "夹层",
            "标记石头",
        ]

        for term in preferred_terms:
            with self.subTest(term=term):
                self.assertIn(term, translations)

        outdated_terms = [
            "黑以扫",
            "双层诅咒",
            "致盲诅咒",
        ]

        for term in outdated_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, translations)


if __name__ == "__main__":
    unittest.main()
