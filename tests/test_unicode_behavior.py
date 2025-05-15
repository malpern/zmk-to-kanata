from converter.behaviors.unicode import UnicodeBinding, is_unicode_binding


def test_unicodebinding_init_and_to_kanata():
    ub = UnicodeBinding("π")
    assert ub.character == "π"
    assert ub.to_kanata() == '(unicode "π")'


def test_unicodebinding_from_zmk_unicode():
    ub = UnicodeBinding.from_zmk("&unicode_foo")
    assert isinstance(ub, UnicodeBinding)
    assert ub.character == "?"


def test_unicodebinding_from_zmk_pi():
    ub = UnicodeBinding.from_zmk("&pi")
    assert isinstance(ub, UnicodeBinding)
    assert ub.character == "π"


def test_unicodebinding_from_zmk_n_tilde():
    ub = UnicodeBinding.from_zmk("&n_tilde")
    assert isinstance(ub, UnicodeBinding)
    assert ub.character == "ñ"


def test_unicodebinding_from_zmk_none():
    ub = UnicodeBinding.from_zmk("&foo")
    assert ub is None


def test_is_unicode_binding_true():
    assert is_unicode_binding("&unicode_foo")
    assert is_unicode_binding("&pi")
    assert is_unicode_binding("&n_tilde")


def test_is_unicode_binding_false():
    assert not is_unicode_binding("&foo")
    assert not is_unicode_binding("")


def test_unicodebinding_to_kanata_platform(monkeypatch):
    ub = UnicodeBinding("π")
    # Simulate macOS
    monkeypatch.setattr("sys.platform", "darwin")
    assert ub.to_kanata() == '(unicode "π")'
    # Simulate Linux
    monkeypatch.setattr("sys.platform", "linux")
    assert (
        ub.to_kanata()
        == "; WARNING: Unicode output is only supported on macOS (darwin). Unicode 'π' not emitted."
    )
    # Simulate Windows
    monkeypatch.setattr("sys.platform", "win32")
    assert (
        ub.to_kanata()
        == "; WARNING: Unicode output is only supported on macOS (darwin). Unicode 'π' not emitted."
    )
