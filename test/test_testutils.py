import os
from pathlib import PurePosixPath, PureWindowsPath
from typing import Optional
from .testutils import file_uri_to_path

import pytest


def check(
    file_uri: str,
    expected_windows_path: Optional[str],
    expected_posix_path: Optional[str],
) -> None:
    if expected_windows_path is not None:
        expected_windows_path_object = PureWindowsPath(expected_windows_path)
    if expected_posix_path is not None:
        expected_posix_path_object = PurePosixPath(expected_posix_path)

    if expected_windows_path is not None:
        if os.name == "nt":
            assert file_uri_to_path(file_uri) == expected_windows_path_object
        assert (
            file_uri_to_path(file_uri, PureWindowsPath) == expected_windows_path_object
        )

    if expected_posix_path is not None:
        if os.name != "nt":
            assert file_uri_to_path(file_uri) == expected_posix_path_object
        assert file_uri_to_path(file_uri, PurePosixPath) == expected_posix_path_object


@pytest.mark.parametrize(
    "file_uri,expected_windows_path,expected_posix_path",
    [
        (
            r"file:///C:/Windows/System32/Drivers/etc/hosts",
            r"C:\Windows\System32\Drivers\etc\hosts",
            r"/C:/Windows/System32/Drivers/etc/hosts",
        ),
        (
            r"file:///C%3A/Windows/System32/Drivers/etc/hosts",
            None,
            r"/C:/Windows/System32/Drivers/etc/hosts",
        ),
        (
            r"file:///C:/some%20dir/some%20file",
            r"C:\some dir\some file",
            r"/C:/some dir/some file",
        ),
        (
            r"file:///C%3A/some%20dir/some%20file",
            None,
            r"/C:/some dir/some file",
        ),
        (
            r"file:///C:/Python27/Scripts/pip.exe",
            r"C:\Python27\Scripts\pip.exe",
            r"/C:/Python27/Scripts/pip.exe",
        ),
        (
            r"file:///C:/yikes/paths%20with%20spaces.txt",
            r"C:\yikes\paths with spaces.txt",
            r"/C:/yikes/paths with spaces.txt",
        ),
        (
            r"file://localhost/c:/WINDOWS/clock.avi",
            r"c:\WINDOWS\clock.avi",
            r"/c:/WINDOWS/clock.avi",
        ),
        (r"file:///home/example/.profile", None, r"/home/example/.profile"),
        (r"file:///c|/path/to/file", r"c:\path\to\file", r"/c|/path/to/file"),
        (r"file:/c|/path/to/file", r"c:\path\to\file", r"/c|/path/to/file"),
        (r"file:c|/path/to/file", r"c:\path\to\file", r"c|/path/to/file"),
        (r"file:///c:/path/to/file", r"c:\path\to\file", r"/c:/path/to/file"),
        (r"file:/c:/path/to/file", r"c:\path\to\file", r"/c:/path/to/file"),
        (r"file:c:/path/to/file", r"c:\path\to\file", r"c:/path/to/file"),
        (r"file:/path/to/file", None, r"/path/to/file"),
        (r"file:///home/user/some%20file.txt", None, r"/home/user/some file.txt"),
        (
            r"file:///C:/some%20dir/some%20file.txt",
            r"C:\some dir\some file.txt",
            r"/C:/some dir/some file.txt",
        ),
    ],
)
def test_paths(
    file_uri: str,
    expected_windows_path: Optional[str],
    expected_posix_path: Optional[str],
) -> None:
    check(file_uri, expected_windows_path, expected_posix_path)
