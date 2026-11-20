"""
Terminal YouTube downloader.

Use only for videos you own or have permission to download.
This project does not bypass DRM, paywalls, sign-in requirements, or other access controls.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


def is_valid_youtube_url(url: str) -> bool:
    """Return True when the URL points to a supported YouTube host."""
    try:
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        return parsed.scheme in {"http", "https"} and (
            host in YOUTUBE_HOSTS or host.endswith(".youtube.com")
        )
    except ValueError:
        return False


def format_duration(seconds: int | None) -> str:
    if not seconds:
        return "Unknown"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02}:{minutes:02}:{secs:02}"
    return f"{minutes:02}:{secs:02}"


def get_download_directory() -> Path | None:
    """Ask where to save the download; create the folder if needed."""
    default_dir = Path.cwd() / "downloads"

    print("\nWhere should the downloaded file be saved?")
    print(f"Press Enter to use the default: {default_dir}")

    while True:
        raw_path = input("Save folder path: ").strip()

        if not raw_path:
            folder = default_dir
        else:
            # Allow users to paste a path surrounded by quotation marks.
            raw_path = raw_path.strip('"').strip("'")
            folder = Path(raw_path).expanduser()

        try:
            folder.mkdir(parents=True, exist_ok=True)
            if not folder.is_dir():
                raise NotADirectoryError(f"{folder} is not a folder.")
            return folder.resolve()
        except (OSError, ValueError) as error:
            print(f"Cannot use that folder: {error}")
            print("Enter another folder path, or press Ctrl+C to cancel.")


def get_video_info(url: str) -> dict:
    import yt_dlp

    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        return downloader.extract_info(url, download=False)


def get_available_qualities(info: dict) -> list[int]:
    """Return unique video heights, sorted from lowest to highest."""
    heights = {
        int(item["height"])
        for item in info.get("formats", [])
        if item.get("height")
        and item.get("vcodec") not in (None, "none")
    }
    return sorted(heights)


def build_format_selector(
    height: int | None = None,
    audio_only: bool = False,
    ffmpeg_available: bool = True,
) -> str:
    """Build a yt-dlp format selector."""
    if audio_only:
        return "bestaudio/best"

    if height is None:
        if ffmpeg_available:
            return "bestvideo+bestaudio/best"
        return "best[vcodec!=none][acodec!=none]/best"

    if ffmpeg_available:
        return (
            f"bestvideo[height<={height}]+bestaudio/"
            f"best[height<={height}]"
        )

    # Without FFmpeg, use a combined audio/video format where available.
    return (
        f"best[height<={height}][vcodec!=none][acodec!=none]/"
        f"best[height<={height}]"
    )


def show_progress(status: dict) -> None:
    if status.get("status") == "downloading":
        downloaded = status.get("downloaded_bytes", 0)
        total = status.get("total_bytes") or status.get("total_bytes_estimate")

        if total:
            percent = downloaded * 100 / total
            message = f"\rDownloading: {percent:5.1f}%"
        else:
            megabytes = downloaded / (1024 * 1024)
            message = f"\rDownloaded: {megabytes:.1f} MB"

        sys.stdout.write(message)
        sys.stdout.flush()

    elif status.get("status") == "finished":
        print("\nDownload finished. Processing file if needed...")


def download_video(url: str, format_selector: str, download_dir: Path) -> None:
    import yt_dlp

    options = {
        "format": format_selector,
        "outtmpl": str(download_dir / "%(title).180B [%(id)s].%(ext)s"),
        "noplaylist": True,
        "progress_hooks": [show_progress],
        "continuedl": True,
        "retries": 3,
        "fragment_retries": 3,
        "windowsfilenames": True,
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        result = downloader.download([url])

    if result == 0:
        print(f"\nSuccess! Your file was saved in:\n{download_dir}")
    else:
        print("\nThe download did not complete. Check the error above.")


def choose_download(info: dict, ffmpeg_available: bool) -> str | None:
    qualities = get_available_qualities(info)

    print("\nAvailable video qualities:")
    if qualities:
        for index, quality in enumerate(qualities, start=1):
            print(f"{index}. {quality}p")
    else:
        print("No video quality information was provided.")

    best_option = len(qualities) + 1
    audio_option = len(qualities) + 2
    print(f"{best_option}. Best available quality")
    print(f"{audio_option}. Audio only")

    if not ffmpeg_available:
        print(
            "\nNote: FFmpeg was not found. Separate high-resolution video "
            "and audio streams cannot be merged. A combined audio/video "
            "format will be used when available."
        )

    while True:
        raw_choice = input("\nChoose an option (or q to quit): ").strip().lower()
        if raw_choice == "q":
            return None

        try:
            choice = int(raw_choice)
        except ValueError:
            print("Please enter one of the displayed numbers.")
            continue

        if 1 <= choice <= len(qualities):
            return build_format_selector(
                height=qualities[choice - 1],
                ffmpeg_available=ffmpeg_available,
            )
        if choice == best_option:
            return build_format_selector(ffmpeg_available=ffmpeg_available)
        if choice == audio_option:
            return build_format_selector(audio_only=True)
        print("Invalid choice. Try again.")


def main() -> None:
    print("=" * 48)
    print("              VIDEO DOWNLOADER")
    print("=" * 48)
    print("Use only for content you own or are authorized to download.\n")

    try:
        url = input("Paste YouTube URL: ").strip()
        if not is_valid_youtube_url(url):
            print("Invalid URL. Please enter a valid YouTube URL.")
            return

        print("\nFetching video information...")
        try:
            info = get_video_info(url)
        except Exception as error:
            print(f"\nCould not retrieve video information: {error}")
            return

        print("\nTitle:   ", info.get("title", "Unknown"))
        print("Duration:", format_duration(info.get("duration")))
        print("Uploader:", info.get("uploader", "Unknown"))

        ffmpeg_available = shutil.which("ffmpeg") is not None
        selected_format = choose_download(info, ffmpeg_available)

        if selected_format is None:
            print("Cancelled.")
            return

        download_dir = get_download_directory()
        if download_dir is None:
            return

        print(f"\nSaving to: {download_dir}")
        print("\nStarting download...")
        try:
            download_video(url, selected_format, download_dir)
        except KeyboardInterrupt:
            print("\nDownload cancelled by user.")
        except Exception as error:
            print(f"\nDownload failed: {error}")
            print(
                "Check your internet connection, update yt-dlp, and make sure "
                "the video is accessible to you."
            )
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")


if __name__ == "__main__":
    main()
    input("\nPress Enter to close...")
