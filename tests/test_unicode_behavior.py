from converter.behaviors.unicode import UnicodeBinding, is_unicode_binding


def test_unicodebinding_init_and_to_kanata():
    ub = UnicodeBinding("π")
    assert ub.character == "π"
    assert ub.to_kanata() == "(unicode π)"


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
