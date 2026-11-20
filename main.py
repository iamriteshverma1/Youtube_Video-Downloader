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



DOWNLOAD_DIR = Path("downloads")
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
    """Build a yt-dlp format selector without trying to bypass restrictions."""
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

    # Without FFmpeg, select a progressive format containing both audio and video.
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


def download_video(url: str, format_selector: str) -> None:
    import yt_dlp

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    options = {
        "format": format_selector,
        "outtmpl": str(DOWNLOAD_DIR / "%(title).180B [%(id)s].%(ext)s"),
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
        print(f"\nSuccess! Check this folder: {DOWNLOAD_DIR.resolve()}")
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
            "and audio streams cannot be merged. The downloader will use "
            "a combined audio/video format when available."
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
    print("=" * 44)
    print("          TERMINAL VIDEO DOWNLOADER")
    print("=" * 44)
    print("Use only for content you own or are authorized to download.\n")

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

    print("\nStarting download...")
    try:
        download_video(url, selected_format)
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as error:
        print(f"\nDownload failed: {error}")
        print(
            "Check your internet connection, update yt-dlp, and make sure "
            "the video is accessible to you."
        )


if __name__ == "__main__":
    main()
