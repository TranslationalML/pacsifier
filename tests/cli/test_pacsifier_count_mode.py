"""Tests for pacsifier --count mode CLI behavior."""

import json
import os
import sys

import pytest

import pacsifier.cli.pacsifier as pacsifier_cli


def _write_valid_config(config_path):
    config = {
        "server_address": "127.0.0.1",
        "port": 104,
        "server_AET": "SERVERAET",
        "AET": "CLIENTAET",
        "move_AET": "MOVEAET",
        "move_port": 11112,
        "batch_size": 30,
        "batch_wait_time": 0,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")


def test_get_parser_accepts_count_flag():
    parser = pacsifier_cli.get_parser()
    args = parser.parse_args(["--config", "config.json", "--count"])
    assert args.count is True


def test_main_count_calls_count_handler(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    query_path = tmp_path / "query.csv"
    out_dir = tmp_path / "out"
    _write_valid_config(config_path)
    query_path.write_text("PatientID\nPACSMAN1\n", encoding="utf-8")

    calls = {"count": 0, "retrieve": 0}

    def _fake_count(table, parameters, output_dir, verbose):
        calls["count"] += 1
        assert "PatientID" in table.columns
        assert os.path.normcase(output_dir) == os.path.normcase(str(out_dir))
        assert isinstance(parameters, dict)
        assert verbose is False

    def _fake_retrieve(*args, **kwargs):
        calls["retrieve"] += 1

    monkeypatch.setattr(pacsifier_cli, "count_dicoms_using_table", _fake_count)
    monkeypatch.setattr(pacsifier_cli, "retrieve_dicoms_using_table", _fake_retrieve)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pacsifier",
            "--config",
            str(config_path),
            "--count",
            "--queryfile",
            str(query_path),
            "--out_directory",
            str(out_dir),
        ],
    )

    pacsifier_cli.main()

    assert calls["count"] == 1
    assert calls["retrieve"] == 0


def test_main_count_rejects_incompatible_flags(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    _write_valid_config(config_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pacsifier",
            "--config",
            str(config_path),
            "--save",
            "--count",
            "--queryfile",
            "query.csv",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        pacsifier_cli.main()
    assert exc_info.value.code == 1


def test_main_count_requires_queryfile(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    _write_valid_config(config_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pacsifier",
            "--config",
            str(config_path),
            "--count",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        pacsifier_cli.main()
    assert exc_info.value.code == 1


def test_main_count_integration_prints_summary(monkeypatch, tmp_path, capsys):
    config_path = tmp_path / "config.json"
    query_path = tmp_path / "query.csv"
    out_dir = tmp_path / "out"
    _write_valid_config(config_path)
    query_path.write_text("PatientID\nPACSMAN1\n", encoding="utf-8")

    monkeypatch.setattr(pacsifier_cli, "echo", lambda **_: True)
    monkeypatch.setattr(pacsifier_cli, "find", lambda *_, **__: "FIND")

    def _fake_write_file(_results, file):
        file_path = tmp_path / "current_count.txt"
        file_path.write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(pacsifier_cli, "write_file", _fake_write_file)
    monkeypatch.setattr(
        pacsifier_cli,
        "parse_findscu_count_dump_file",
        lambda *_: [
            {
                "PatientID": "PACSMAN1",
                "StudyInstanceUID": "1.2.3",
                "NumberOfStudyRelatedSeries": "2",
                "NumberOfStudyRelatedInstances": "42",
            },
            {
                "PatientID": "PACSMAN1",
                "StudyInstanceUID": "1.2.4",
                "NumberOfStudyRelatedSeries": "3",
                "NumberOfStudyRelatedInstances": "84",
            },
        ],
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pacsifier",
            "--config",
            str(config_path),
            "--count",
            "--queryfile",
            str(query_path),
            "--out_directory",
            str(out_dir),
        ],
    )

    pacsifier_cli.main()

    out = capsys.readouterr().out
    assert "Count summary:" in out
    assert "PatientID=PACSMAN1: studies=2, series=5, instances=126" in out
