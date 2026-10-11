import pytest

import error_handling_demo as demo


def test_load_valid_config(tmp_path):
    file = tmp_path / "config.json"
    file.write_text('{"port": 8080}', encoding="utf-8")
    assert demo.load_config(file) == {"port": 8080}


def test_missing_file_raises_not_found(tmp_path):
    with pytest.raises(demo.ConfigNotFoundError):
        demo.load_config(tmp_path / "nope.json")


def test_broken_json_raises_invalid(tmp_path):
    file = tmp_path / "broken.json"
    file.write_text("{oops", encoding="utf-8")
    with pytest.raises(demo.ConfigInvalidError):
        demo.load_config(file)


def test_json_list_is_rejected(tmp_path):
    file = tmp_path / "list.json"
    file.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(demo.ConfigInvalidError):
        demo.load_config(file)


def test_all_config_errors_share_base_class(tmp_path):
    with pytest.raises(demo.ConfigError):
        demo.load_config(tmp_path / "nope.json")


@pytest.mark.parametrize("value, expected", [("8080", 8080), (1, 1), (65535, 65535)])
def test_parse_port_valid(value, expected):
    assert demo.parse_port(value) == expected


@pytest.mark.parametrize("value", ["abc", None, 0, 70000, -5])
def test_parse_port_invalid(value):
    with pytest.raises(demo.ConfigInvalidError):
        demo.parse_port(value)


def test_retry_succeeds_after_failures():
    calls = {"n": 0}

    @demo.retry(times=3, delay=0)
    def sometimes():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("fail")
        return "ok"

    assert sometimes() == "ok"
    assert calls["n"] == 3


def test_retry_gives_up_and_reraises():
    @demo.retry(times=2, delay=0)
    def always_fails():
        raise ConnectionError("fail")

    with pytest.raises(ConnectionError):
        always_fails()
