"""
Status introspection for the /settings page. These tests focus on the
detector contract — that each checker returns a populated ComponentStatus
without raising — rather than the specific install state of the runner.
"""
from src.system_status import (
    ComponentStatus,
    check_all,
    check_argos_translate,
    check_clinvar,
    check_ollama,
    check_pharmgkb,
)


def _assert_well_formed(status: ComponentStatus) -> None:
    assert isinstance(status, ComponentStatus)
    assert status.key
    assert status.name
    assert isinstance(status.installed, bool)
    assert isinstance(status.install_commands, list)
    # Detail string may be empty for installed components on some platforms,
    # but it must be a string (no None leaking through).
    assert isinstance(status.detail, str)


def test_clinvar_detector_contract():
    _assert_well_formed(check_clinvar())


def test_pharmgkb_detector_contract():
    _assert_well_formed(check_pharmgkb())


def test_argos_detector_contract():
    _assert_well_formed(check_argos_translate())


def test_ollama_detector_never_throws():
    # Ollama binary will almost certainly be absent in CI — that's the path
    # we most want to cover, since a NoneType from shutil.which() must not
    # blow up the settings page.
    _assert_well_formed(check_ollama())


def test_check_all_returns_every_component():
    components = check_all()
    keys = {c.key for c in components}
    assert keys == {"clinvar", "pharmgkb", "argos", "ollama"}


def test_clinvar_is_marked_required():
    assert check_clinvar().required is True


def test_optional_components_marked_optional():
    assert check_pharmgkb().required is False
    assert check_argos_translate().required is False
    assert check_ollama().required is False
