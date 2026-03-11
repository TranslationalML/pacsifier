"""Tests for pacsifier --count mode CLI behavior."""

import json
import os
import sys
import types

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


def test_get_parser_accepts_karnak_flag():
    parser = pacsifier_cli.get_parser()
    args = parser.parse_args(["--config", "config.json", "--karnak"])
    assert args.karnak is True


def test_main_count_calls_count_handler(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    query_path = tmp_path / "query.csv"
    out_dir = tmp_path / "out"
    _write_valid_config(config_path)
    query_path.write_text("PatientID\nPACSMAN1\n", encoding="utf-8")

    calls = {"count": 0, "retrieve": 0}

    def _fake_count(table, parameters, output_dir, resume, verbose):
        calls["count"] += 1
        assert "PatientID" in table.columns
        assert os.path.normcase(output_dir) == os.path.normcase(str(out_dir))
        assert isinstance(parameters, dict)
        assert resume is False
        assert verbose is False

    def _fake_retrieve(*_args, **_kwargs):
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


def test_main_karnak_calls_retrieve_handler(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    query_path = tmp_path / "query.csv"
    out_dir = tmp_path / "out"
    command_file = tmp_path / "commands.txt"
    _write_valid_config(config_path)
    query_path.write_text("PatientID\nPACSMAN1\n", encoding="utf-8")

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    config.update({
        "karnak_address": "127.0.0.1",
        "karnak_port": 11113,
        "karnak_aet": "KARNAK",
        "pynetdicom_address": "127.0.0.1",
        "pynetdicom_port": 11112,
        "pynetdicom_aet": "PACSIFIER",
    })
    config_path.write_text(json.dumps(config), encoding="utf-8")

    calls = {"retrieve": 0, "listener_start": 0, "listener_stop": 0}

    class _FakeListener:
        def __init__(self, address, port, aet, output_dir):
            assert address == "127.0.0.1"
            assert port == 11112
            assert aet == "PACSIFIER"
            assert os.path.normcase(output_dir) == os.path.normcase(str(out_dir))

        def start(self):
            calls["listener_start"] += 1

        def stop(self):
            calls["listener_stop"] += 1

    def _fake_retrieve(
        table,
        parameters,
        output_dir,
        save,
        info,
        move,
        karnak,
        command_file_arg,
        no_source_aet,
        resume,
        verbose,
    ):
        calls["retrieve"] += 1
        assert karnak is True
        assert command_file_arg == os.path.normcase(os.path.abspath(str(command_file)))
        assert no_source_aet is True
        assert save is False and info is False and move is False
        assert resume is False and verbose is False
        assert "PatientID" in table.columns
        assert isinstance(parameters, dict)
        assert os.path.normcase(output_dir) == os.path.normcase(str(out_dir))

    monkeypatch.setattr(pacsifier_cli, "retrieve_dicoms_using_table", _fake_retrieve)
    monkeypatch.setitem(
        sys.modules,
        "pacsifier.core.pynetdicom_listener",
        types.SimpleNamespace(PynetdicomListener=_FakeListener),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pacsifier",
            "--config",
            str(config_path),
            "--karnak",
            "--queryfile",
            str(query_path),
            "--out_directory",
            str(out_dir),
            "--command_file",
            str(command_file),
            "--no_source_aet",
        ],
    )

    pacsifier_cli.main()

    assert calls["retrieve"] == 1
    assert calls["listener_start"] == 1
    assert calls["listener_stop"] == 1


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


def test_main_count_integration_writes_output_file(monkeypatch, tmp_path, capsys):
    config_path = tmp_path / "config.json"
    query_path = tmp_path / "query.csv"
    out_dir = tmp_path / "out"
    _write_valid_config(config_path)
    query_path.write_text("PatientID\nPACSMAN1\n", encoding="utf-8")

    monkeypatch.setattr(pacsifier_cli, "echo", lambda **_: True)
    monkeypatch.setattr(pacsifier_cli, "find", lambda *_, **__: "FIND")

    def _fake_write_file(_results, file):
        import pathlib
        pathlib.Path(file).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(file).write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(pacsifier_cli, "write_file", _fake_write_file)
    monkeypatch.setattr(
        pacsifier_cli,
        "parse_findscu_series_count_dump_file",
        lambda *_: [
            {
                "PatientID": "PACSMAN1",
                "StudyInstanceUID": "1.2.3",
                "SeriesInstanceUID": "1.2.3.1",
                "NumberOfInstances": "42",
            },
            {
                "PatientID": "PACSMAN1",
                "StudyInstanceUID": "1.2.3",
                "SeriesInstanceUID": "1.2.3.2",
                "NumberOfInstances": "84",
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
    assert "PatientID=PACSMAN1: series=2, instances=126" in out
    assert "1.2.3.1" in out
    assert "1.2.3.2" in out
    assert "instances=42" in out
    assert "instances=84" in out

    output_file = out_dir / "count_results.csv"
    assert output_file.exists(), "count_results.csv was not created"
    content = output_file.read_text(encoding="utf-8")
    assert "SeriesInstanceUID" in content  # header present
    assert "1.2.3.1" in content
    assert "1.2.3.2" in content
    assert "COMPLETED_QUERY" not in content  # progress tracked separately
    progress_file = out_dir / "count_results.progress"
    assert progress_file.exists(), "count_results.progress was not created"
    assert "0" in progress_file.read_text(encoding="utf-8")
