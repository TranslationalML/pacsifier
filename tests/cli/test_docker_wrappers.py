# Copyright 2018-2024 Lausanne University Hospital and University of Lausanne,
# Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the docker wrapper scripts in `pacsifier.cli.docker_wrappers`."""

import os
import sys
import pytest
import subprocess
from unittest.mock import patch, MagicMock

from pacsifier.cli.docker_wrappers import (
    get_docker_image_name,
    get_docker_user_args,
    run_docker_command,
    docker_pacsifier,
    docker_get_pseudonyms,
    docker_add_karnak_tags,
    docker_anonymize_dicoms,
    docker_extract_carestream_report,
    docker_move_dumps,
    docker_create_dicomdir,
)


def test_get_docker_image_name_default():
    """Test that get_docker_image_name returns default when env var not set."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_docker_image_name() == 'quay.io/translationalml/pacsifier:latest'


def test_get_docker_image_name_from_env():
    """Test that get_docker_image_name returns value from environment variable."""
    with patch.dict(os.environ, {'PACSIFIER_DOCKER_IMAGE': 'pacsifier:1.0.0'}):
        assert get_docker_image_name() == 'pacsifier:1.0.0'


@pytest.mark.skipif(not hasattr(os, 'getuid'), reason="POSIX only")
def test_get_docker_user_args_default(monkeypatch):
    """Test that the container runs as the current host user by default."""
    monkeypatch.delenv('PACSIFIER_DOCKER_USER', raising=False)
    assert get_docker_user_args() == ['--user', f'{os.getuid()}:{os.getgid()}']


def test_get_docker_user_args_from_env(monkeypatch):
    """Test that PACSIFIER_DOCKER_USER overrides the user."""
    monkeypatch.setenv('PACSIFIER_DOCKER_USER', '1234:5678')
    assert get_docker_user_args() == ['--user', '1234:5678']


def test_get_docker_user_args_empty_env_disables(monkeypatch):
    """Test that an empty PACSIFIER_DOCKER_USER keeps the image's default user."""
    monkeypatch.setenv('PACSIFIER_DOCKER_USER', '')
    assert get_docker_user_args() == []


def test_get_docker_user_args_without_posix_ids(monkeypatch):
    """Test that no --user is used where os.getuid is unavailable (e.g. Windows)."""
    monkeypatch.delenv('PACSIFIER_DOCKER_USER', raising=False)
    monkeypatch.delattr(os, 'getuid', raising=False)
    assert get_docker_user_args() == []


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_user_before_image(mock_run, monkeypatch):
    """Test that --user is passed to docker run before the image name."""
    monkeypatch.setenv('PACSIFIER_DOCKER_USER', '1234:5678')
    mock_run.return_value = MagicMock(returncode=0)

    run_docker_command(['pacsifier'])

    call_args = mock_run.call_args[0][0]
    user_index = call_args.index('--user')
    assert call_args[user_index + 1] == '1234:5678'
    assert user_index < call_args.index('quay.io/translationalml/pacsifier:latest')


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_basic(mock_run, tmp_path):
    """Test that run_docker_command constructs correct docker command."""
    mock_run.return_value = MagicMock(returncode=0)

    run_docker_command(['pacsifier', '-c', '/config.json'], ['/host:/container'])

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert call_args[0] == 'docker'
    assert call_args[1] == 'run'
    assert '--rm' in call_args
    assert '--net=host' in call_args
    assert '-i' in call_args  # Interactive mode for output visibility
    assert '-e' in call_args  # Environment variable flag
    assert 'PYTHONUNBUFFERED=1' in call_args  # Python unbuffered output
    assert '-v' in call_args
    assert '/host:/container' in call_args
    assert 'quay.io/translationalml/pacsifier:latest' in call_args
    assert 'pacsifier' in call_args
    assert '-c' in call_args
    assert '/config.json' in call_args


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_error_handling(mock_run):
    """Test that run_docker_command handles errors correctly."""
    mock_run.side_effect = subprocess.CalledProcessError(1, 'docker')

    with pytest.raises(SystemExit) as exc_info:
        run_docker_command(['pacsifier'])
    assert exc_info.value.code == 1


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_docker_not_found(mock_run):
    """Test that run_docker_command handles Docker not found."""
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(SystemExit) as exc_info:
        run_docker_command(['pacsifier'])
    assert exc_info.value.code == 1


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_output_visibility_flags(mock_run):
    """Test that run_docker_command includes flags for output visibility."""
    mock_run.return_value = MagicMock(returncode=0)

    run_docker_command(['pacsifier', '--help'])

    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args[1]
    call_args = mock_run.call_args[0][0]

    # Verify stdout and stderr are passed through (None means inherit from parent)
    assert call_kwargs.get('stdout') is None
    assert call_kwargs.get('stderr') is None
    assert call_kwargs.get('check') is True

    # Verify -i flag is present for interactive mode
    assert '-i' in call_args

    # Verify PYTHONUNBUFFERED environment variable is set
    assert '-e' in call_args
    env_index = call_args.index('-e')
    assert call_args[env_index + 1] == 'PYTHONUNBUFFERED=1'


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_python_unbuffered_position(mock_run):
    """Test that PYTHONUNBUFFERED is set before the image name."""
    mock_run.return_value = MagicMock(returncode=0)

    run_docker_command(['pacsifier'])

    call_args = mock_run.call_args[0][0]

    # Find positions of key elements
    e_flag_index = call_args.index('-e')
    pyunbuf_index = call_args.index('PYTHONUNBUFFERED=1')
    image_index = call_args.index('quay.io/translationalml/pacsifier:latest')

    # PYTHONUNBUFFERED should come right after -e
    assert pyunbuf_index == e_flag_index + 1
    # Environment variable should be set before the image
    assert pyunbuf_index < image_index


@patch('pacsifier.cli.docker_wrappers.subprocess.run')
def test_run_docker_command_interactive_flag_position(mock_run):
    """Test that -i flag is in the correct position after --net=host."""
    mock_run.return_value = MagicMock(returncode=0)

    run_docker_command(['pacsifier'])

    call_args = mock_run.call_args[0][0]

    # Verify the order: docker, run, --rm, --net=host, -i, [-t if tty], -e, PYTHONUNBUFFERED=1
    assert call_args[0] == 'docker'
    assert call_args[1] == 'run'
    assert call_args[2] == '--rm'
    assert call_args[3] == '--net=host'
    assert call_args[4] == '-i'
    # -t is only present when stdout is a TTY; in test environments it is not
    if sys.stdout.isatty():
        assert call_args[5] == '-t'
        assert call_args[6] == '-e'
        assert call_args[7] == 'PYTHONUNBUFFERED=1'
    else:
        assert call_args[5] == '-e'
        assert call_args[6] == 'PYTHONUNBUFFERED=1'


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_pacsifier_basic(mock_run_docker, tmp_path):
    """Test docker_pacsifier constructs correct command."""
    config_file = tmp_path / 'config.json'
    config_file.write_text('{}')
    query_file = tmp_path / 'query.csv'
    query_file.write_text('PatientID\n123')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    with patch('sys.argv', ['docker_pacsifier', '-c', str(config_file),
                            '-i', '-q', str(query_file), '-d', str(output_dir)]):
        docker_pacsifier()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier' in call_args
    assert '-c' in call_args
    assert '/config.json' in call_args
    assert '-i' in call_args
    assert '-q' in call_args
    assert '/query.csv' in call_args
    assert '-d' in call_args
    assert '/output' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 3
    assert str(config_file.absolute()) in volumes[0]
    assert str(query_file.absolute()) in volumes[1]
    assert str(output_dir.absolute()) in volumes[2]


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_get_pseudonyms_deid_mode(mock_run_docker, tmp_path):
    """Test docker_get_pseudonyms in de-id mode."""
    config_file = tmp_path / 'config.json'
    config_file.write_text('{}')
    query_file = tmp_path / 'query.csv'
    query_file.write_text('PatientID\n123')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    with patch('sys.argv', ['docker_get_pseudonyms', '--mode', 'de-id',
                            '-c', str(config_file), '-q', str(query_file),
                            '-a', 'TestProject', '-d', str(output_dir)]):
        docker_get_pseudonyms()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-get-pseudonyms' in call_args
    assert '--mode' in call_args
    assert 'de-id' in call_args
    assert '--config' in call_args
    assert '/config.json' in call_args
    assert '--queryfile' in call_args
    assert '/query.csv' in call_args
    assert '--project_name' in call_args
    assert 'TestProject' in call_args
    assert '--out_directory' in call_args
    assert '/output' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 3  # config, query, output


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_get_pseudonyms_custom_mode(mock_run_docker, tmp_path):
    """Test docker_get_pseudonyms in custom mode."""
    mapping_file = tmp_path / 'mapping.csv'
    mapping_file.write_text('old,new\nsub-1234,P0001')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    with patch('sys.argv', ['docker_get_pseudonyms', '--mode', 'custom',
                            '-mf', str(mapping_file), '-a', 'TestProject',
                            '-d', str(output_dir), '--shift-days']):
        docker_get_pseudonyms()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-get-pseudonyms' in call_args
    assert '--mode' in call_args
    assert 'custom' in call_args
    assert '--mappingfile' in call_args
    assert '/mapping.csv' in call_args
    assert '--shift-days' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 2  # mapping, output


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_add_karnak_tags(mock_run_docker, tmp_path):
    """Test docker_add_karnak_tags constructs correct command."""
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    new_ids_file = tmp_path / 'new_ids.json'
    new_ids_file.write_text('{"sub-1234": "P0001"}')
    day_shift_file = tmp_path / 'day_shift.json'
    day_shift_file.write_text('{"sub-1234": 10}')

    with patch('sys.argv', ['docker_add_karnak_tags', '-d', str(input_dir),
                            '-n', str(new_ids_file), '-a', 'TestAlbum',
                            '-s', str(day_shift_file)]):
        docker_add_karnak_tags()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-add-karnak-tags' in call_args
    assert '--in_folder' in call_args
    assert '/input' in call_args
    assert '--new_ids' in call_args
    assert '/new_ids.json' in call_args
    assert '--day_shift' in call_args
    assert '/day_shift.json' in call_args
    assert '--album_name' in call_args
    assert 'TestAlbum' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 3  # input, new_ids, day_shift


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_anonymize_dicoms(mock_run_docker, tmp_path):
    """Test docker_anonymize_dicoms constructs correct command."""
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    new_ids_file = tmp_path / 'new_ids.json'
    new_ids_file.write_text('{"sub-1234": "P0001"}')

    with patch('sys.argv', ['docker_anonymize_dicoms', '-d', str(input_dir),
                            '-o', str(output_dir), '-n', str(new_ids_file),
                            '-i', '-p', '-a']):
        docker_anonymize_dicoms()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-anonymize' in call_args
    assert '--in_folder' in call_args
    assert '/input' in call_args
    assert '--out_folder' in call_args
    assert '/output' in call_args
    assert '--delete_identifiable' in call_args
    assert '--remove_private_tags' in call_args
    assert '--fuzz_acq_dates' in call_args
    assert '--new_ids' in call_args
    assert '/new_ids.json' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 3  # input, output, new_ids


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_extract_carestream_report(mock_run_docker, tmp_path):
    """Test docker_extract_carestream_report constructs correct command."""
    data_dir = tmp_path / 'data'
    data_dir.mkdir()

    with patch('sys.argv', ['docker_extract_carestream_report',
                            '-d', str(data_dir)]):
        docker_extract_carestream_report()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-extract-carestream-report' in call_args
    assert '-d' in call_args
    assert '/data' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 1
    assert str(data_dir.absolute()) in volumes[0]


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_move_dumps(mock_run_docker, tmp_path):
    """Test docker_move_dumps constructs correct command."""
    dicom_dir = tmp_path / 'dicom'
    dicom_dir.mkdir()
    info_dir = tmp_path / 'info'
    info_dir.mkdir()

    with patch('sys.argv', ['docker_move_dumps', '-d', str(dicom_dir),
                            '-o', str(info_dir)]):
        docker_move_dumps()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-move-csv' in call_args
    assert '-d' in call_args
    assert '/dicom' in call_args
    assert '-o' in call_args
    assert '/info' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 2


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_create_dicomdir(mock_run_docker, tmp_path):
    """Test docker_create_dicomdir constructs correct command."""
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    with patch('sys.argv', ['docker_create_dicomdir', '-d', str(input_dir),
                            '-o', str(output_dir)]):
        docker_create_dicomdir()

    mock_run_docker.assert_called_once()
    call_args = mock_run_docker.call_args[0][0]
    assert 'pacsifier-create-dicomdir' in call_args
    assert '--in_folder' in call_args
    assert '/input' in call_args
    assert '--out_folder' in call_args
    assert '/output' in call_args

    volumes = mock_run_docker.call_args[1]['additional_volumes']
    assert len(volumes) == 2


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_wrappers_custom_image(mock_run_docker, tmp_path):
    """Test that --image flag overrides default docker image."""
    config_file = tmp_path / 'config.json'
    config_file.write_text('{}')
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    with patch('sys.argv', ['docker_pacsifier', '-c', str(config_file),
                            '--image', 'pacsifier:custom', '-d', str(output_dir)]):
        docker_pacsifier()

    # Check that environment variable was set
    assert os.environ.get('PACSIFIER_DOCKER_IMAGE') == 'pacsifier:custom'

    # Clean up
    del os.environ['PACSIFIER_DOCKER_IMAGE']


@patch('pacsifier.cli.docker_wrappers.run_docker_command')
def test_docker_get_pseudonyms_missing_required_args(mock_run_docker, tmp_path):
    """Test that docker_get_pseudonyms errors on missing required args."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()

    # Missing config and queryfile for de-id mode
    with patch('sys.argv', ['docker_get_pseudonyms', '--mode', 'de-id',
                            '-a', 'TestProject', '-d', str(output_dir)]):
        with pytest.raises(SystemExit):
            docker_get_pseudonyms()

    # Missing mappingfile for custom mode
    with patch('sys.argv', ['docker_get_pseudonyms', '--mode', 'custom',
                            '-a', 'TestProject', '-d', str(output_dir)]):
        with pytest.raises(SystemExit):
            docker_get_pseudonyms()
