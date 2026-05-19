"""
Tests for i18n module.
i18nモジュールのテスト。
"""

import pytest

from src.i18n import I18n


class TestI18n:
    """
    Test cases for I18n class.
    I18nクラスのテストケース。
    """

    def test_english_initialization(self, i18n_en: I18n) -> None:
        """
        Test English initialization.
        英語初期化のテスト。

        Parameters
        ----------
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        """
        assert i18n_en.language == "en"

    def test_japanese_initialization(self, i18n_ja: I18n) -> None:
        """
        Test Japanese initialization.
        日本語初期化のテスト。

        Parameters
        ----------
        i18n_ja : I18n
            Japanese i18n fixture.
            日本語i18nフィクスチャー。
        """
        assert i18n_ja.language == "ja"

    def test_get_english_message(self, i18n_en: I18n) -> None:
        """
        Test getting English message.
        英語メッセージ取得のテスト。

        Parameters
        ----------
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        """
        message = i18n_en.get("starting")
        assert "Starting AWS Default VPC Cleaner" in message

    def test_get_japanese_message(self, i18n_ja: I18n) -> None:
        """
        Test getting Japanese message.
        日本語メッセージ取得のテスト。

        Parameters
        ----------
        i18n_ja : I18n
            Japanese i18n fixture.
            日本語i18nフィクスチャー。
        """
        message = i18n_ja.get("starting")
        assert "AWS Default VPC Cleaner" in message
        assert "起動" in message

    def test_get_message_with_formatting(self, i18n_en: I18n) -> None:
        """
        Test getting message with formatting parameters.
        フォーマットパラメータ付きメッセージ取得のテスト。

        Parameters
        ----------
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        """
        message = i18n_en.get("found_regions", count=5)
        assert "5" in message
        assert "regions" in message

    def test_get_unknown_key(self, i18n_en: I18n) -> None:
        """
        Test getting unknown key returns the key itself.
        不明なキーを取得するとキー自体が返されるテスト。

        Parameters
        ----------
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        """
        message = i18n_en.get("unknown_key")
        assert message == "unknown_key"

    def test_set_language(self, i18n_en: I18n) -> None:
        """
        Test changing language.
        言語変更のテスト。

        Parameters
        ----------
        i18n_en : I18n
            English i18n fixture.
            英語i18nフィクスチャー。
        """
        assert i18n_en.language == "en"

        i18n_en.set_language("ja")
        assert i18n_en.language == "ja"

        message = i18n_en.get("starting")
        assert "起動" in message

    def test_auto_detect_japanese(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Test auto-detecting Japanese from environment.
        環境から日本語を自動検出するテスト。

        Parameters
        ----------
        monkeypatch : pytest.MonkeyPatch
            Pytest monkeypatch fixture.
            Pytestのmonkeypatchフィクスチャー。
        """
        monkeypatch.setenv("LANG", "ja_JP.UTF-8")

        i18n = I18n()
        assert i18n.language == "ja"

    def test_auto_detect_english(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Test auto-detecting English from environment.
        環境から英語を自動検出するテスト。

        Parameters
        ----------
        monkeypatch : pytest.MonkeyPatch
            Pytest monkeypatch fixture.
            Pytestのmonkeypatchフィクスチャー。
        """
        monkeypatch.setenv("LANG", "en_US.UTF-8")

        i18n = I18n()
        assert i18n.language == "en"

    def test_invalid_language_fallback(self) -> None:
        """
        Test fallback to English for invalid language.
        無効な言語の場合に英語にフォールバックするテスト。
        """
        i18n = I18n("invalid")
        assert i18n.language == "en"

    def test_all_keys_exist_in_both_languages(self) -> None:
        """
        Test that all keys exist in both language dictionaries.
        すべてのキーが両方の言語辞書に存在するかテスト。
        """
        from src.i18n import TRANSLATIONS

        en_keys = set(TRANSLATIONS["en"].keys())
        ja_keys = set(TRANSLATIONS["ja"].keys())

        assert en_keys == ja_keys, "Language dictionaries have different keys"
