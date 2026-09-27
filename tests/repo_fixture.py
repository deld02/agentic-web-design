"""Source-only test copies; never duplicate installed tools or generated runs."""
import shutil


def copy_source_repo(source, destination):
    return shutil.copytree(source, destination, ignore=shutil.ignore_patterns(
        '.git', '__pycache__', '.harness', 'node_modules', 'dist', 'dist2', '.publish-remote-*'))
