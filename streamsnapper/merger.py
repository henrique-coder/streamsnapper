# Built-in imports
from pathlib import Path
from os import PathLike
from shutil import which
from subprocess import run, DEVNULL, CalledProcessError
from typing import Union, Literal

# Local imports
from .exceptions import MergeError


class Merger:
    """A class for merging multiple audio and video streams into a single file."""

    def __init__(self, logging: bool = False) -> None:
        """
        Initialize the Merger class with the required settings for merging audio and video streams.

        :param logging: Enable or disable the FFmpeg logging.
        """

        self._logging = logging

    def merge(
        self,
        video_file_path: Union[str, PathLike],
        audio_file_path: Union[str, PathLike],
        output_file_path: Union[str, PathLike],
        ffmpeg_file_path: Union[str, PathLike, Literal['local']] = 'local',
    ) -> None:
        """
        Merge the audio and video streams into a single file.

        :param video_file_path: The path to the video file to merge.
        :param audio_file_path: The path to the audio file to merge.
        :param output_file_path: The path to save the merged file to.
        :param ffmpeg_file_path: The path to the ffmpeg executable. If 'local', the ffmpeg executable will be searched in the PATH environment variable.
        :raises MergeError: If an error occurs while merging the files.
        """

        video_file_path = Path(video_file_path).resolve()
        audio_file_path = Path(audio_file_path).resolve()
        output_file_path = Path(output_file_path).resolve()

        if ffmpeg_file_path == 'local':
            found_ffmpeg_binary = which('ffmpeg')

            if found_ffmpeg_binary:
                ffmpeg_file_path = Path(found_ffmpeg_binary)
            else:
                raise FileNotFoundError('The ffmpeg executable was not found. Please provide the path to the ffmpeg executable.')
        else:
            ffmpeg_file_path = Path(ffmpeg_file_path).resolve()

        stdout = None if self._logging else DEVNULL
        stderr = None if self._logging else DEVNULL

        try:
            run(
                [
                    ffmpeg_file_path.as_posix(),
                    '-y',
                    '-hide_banner',
                    '-i',
                    video_file_path.as_posix(),
                    '-i',
                    audio_file_path.as_posix(),
                    '-c',
                    'copy',
                    '-map',
                    '0:v',
                    '-map',
                    '1:a',
                    output_file_path.as_posix(),
                ],
                check=True,
                stdout=stdout,
                stderr=stderr,
            )
        except CalledProcessError as e:
            raise MergeError(
                f'Error occurred while merging files: "{video_file_path.as_posix()}" and "{audio_file_path.as_posix()}" to "{output_file_path.as_posix()}".'
            ) from e
