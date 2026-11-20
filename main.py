"""
Terminal YouTube downloader.

Use only for videos you own or have permission to download, and in ways
permitted by the platform's terms. This project does not bypass DRM,
paywalls, sign-in requirements, or other access controls.
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


def get_video_info(url: str, download_playlist: bool = False) -> dict:
    import yt_dlp

    options = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": not download_playlist,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        return downloader.extract_info(url, download=False)


def get_available_qualities(info: dict) -> list[int]:
    """Return unique video heights, sorted from lowest to highest."""
    heights = {
        int(item["height"])
        for item in info.get("formats", [])
        if item.get("height") and item.get("vcodec") not in (None, "none")
    }
    return sorted(heights)


def get_representative_video_info(info: dict) -> dict:
    """For a playlist, use the first available entry to display quality choices."""
    if info.get("_type") == "playlist":
        for entry in info.get("entries") or []:
            if entry:
                return entry
        return {}
    return info


def build_format_selector(
    height: int | None = None,
    audio_only: bool = False,
    ffmpeg_available: bool = True,
) -> str:
    """Build a yt-dlp selector for formats that are actually offered."""
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

    return (
        f"best[height<={height}][vcodec!=none][acodec!=none]/"
        f"best[height<={height}]"
    )


def ask_destination() -> Path | None:
    """Ask for a destination folder and create it if needed."""
    while True:
        raw_path = input(
            "\nEnter the folder path where you want to save files "
            "(press Enter for Downloads, or q to cancel): "
        ).strip()

        if raw_path.lower() == "q":
            return None

        if not raw_path:
            destination = Path.home() / "Downloads" / "YouTubeDownloader"
        else:
            # Remove surrounding quotes, which are common when copying Windows paths.
            raw_path = raw_path.strip('"').strip("'")
            try:
                destination = Path(raw_path).expanduser()
            except (OSError, ValueError):
                print("That folder path is not valid. Try again.")
                continue

        try:
            destination.mkdir(parents=True, exist_ok=True)
            if not destination.is_dir():
                print("The selected path is not a folder. Try again.")
                continue
            return destination.resolve()
        except OSError as error:
            print(f"Could not use that folder: {error}")


def show_progress(status: dict) -> None:
    if status.get("status") == "downloading":
        downloaded = status.get("downloaded_bytes", 0)
        total = status.get("total_bytes") or status.get("total_bytes_estimate")

        if total:
            percent = downloaded * 100 / total
            message = f"\rDownloading current file: {percent:5.1f}%"
        else:
            megabytes = downloaded / (1024 * 1024)
            message = f"\rDownloaded: {megabytes:.1f} MB"

        sys.stdout.write(message)
        sys.stdout.flush()

    elif status.get("status") == "finished":
        print("\nFile downloaded. Processing if needed...")


def make_progress_hook():
    """Return a hook that reports playlist item numbers when available."""
    def hook(status: dict) -> None:
        info = status.get("info_dict") or {}
        playlist_index = info.get("playlist_index")
        playlist_count = info.get("n_entries")
        if playlist_index:
            if playlist_count:
                prefix = f"\nPlaylist item {playlist_index}/{playlist_count}: "
            else:
                prefix = f"\nPlaylist item {playlist_index}: "
            if status.get("status") == "downloading":
                sys.stdout.write(prefix)
                sys.stdout.flush()
        show_progress(status)

    return hook


def download_media(
    url: str,
    format_selector: str,
    destination: Path,
    download_playlist: bool,
    audio_only: bool,
) -> None:
    import yt_dlp

    options = {
        "format": format_selector,
        "outtmpl": str(
            destination / "%(playlist_title)s/" 
            "%(playlist_index)03d - %(title).180B [%(id)s].%(ext)s"
            if download_playlist
            else destination / "%(title).180B [%(id)s].%(ext)s"
        ),
        "noplaylist": not download_playlist,
        "progress_hooks": [make_progress_hook()],
        "continuedl": True,
        "retries": 3,
        "fragment_retries": 3,
        "windowsfilenames": True,
        "ignoreerrors": False,
    }

    if audio_only:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError(
                "FFmpeg was not found. Audio-only MP3 conversion requires "
                "FFmpeg. Install FFmpeg and add it to PATH, then reopen "
                "the terminal."
            )
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

    with yt_dlp.YoutubeDL(options) as downloader:
        result = downloader.download([url])

    if result == 0:
        print(f"\nSuccess! Files saved in: {destination}")
    else:
        print("\nThe download did not complete. Check the error above.")


def choose_download(
    info: dict,
    ffmpeg_available: bool,
) -> tuple[str, bool] | None:
    qualities = get_available_qualities(info)

    print("\nChoose download type:")
    print("1. Video")
    print("2. Audio only (MP3)")

    while True:
        media_choice = input("Enter 1 or 2 (or q to quit): ").strip().lower()
        if media_choice == "q":
            return None
        if media_choice in {"1", "2"}:
            break
        print("Please enter 1 or 2.")

    if media_choice == "2":
        if not ffmpeg_available:
            print(
                "\nFFmpeg is required to convert audio to MP3, but it was "
                "not found on this computer."
            )
            print("Install FFmpeg, add it to PATH, and run the app again.")
            return None
        return build_format_selector(audio_only=True), True

    print("\nAvailable video qualities:")
    if qualities:
        for index, quality in enumerate(qualities, start=1):
            print(f"{index}. {quality}p")
    else:
        print("No video quality information was provided.")

    best_option = len(qualities) + 1
    print(f"{best_option}. Best available quality")

    if not ffmpeg_available:
        print(
            "\nNote: FFmpeg was not found. The downloader will use a "
            "combined audio/video format when available. Some high "
            "resolutions may not be available."
        )

    while True:
        raw_choice = input("\nChoose a quality (or q to quit): ").strip().lower()
        if raw_choice == "q":
            return None

        try:
            choice = int(raw_choice)
        except ValueError:
            print("Please enter one of the displayed numbers.")
            continue

        if 1 <= choice <= len(qualities):
            return (
                build_format_selector(
                    height=qualities[choice - 1],
                    ffmpeg_available=ffmpeg_available,
                ),
                False,
            )
        if choice == best_option:
            return (build_format_selector(ffmpeg_available=ffmpeg_available), False)
        print("Invalid choice. Try again.")


def ask_playlist_mode(info: dict) -> bool:
    """Return True when the user wants the full playlist."""
    if info.get("_type") != "playlist":
        return False

    entries = info.get("entries") or []
    count = info.get("playlist_count") or len(entries)
    title = info.get("title") or "Untitled playlist"

    print(f"\nPlaylist detected: {title}")
    print(f"Videos listed: {count if count else 'Unknown'}")
    print("\n1. Download the complete playlist")
    print("2. Download only the video from this URL")

    while True:
        choice = input("Choose 1 or 2 (or q to quit): ").strip().lower()
        if choice == "q":
            raise KeyboardInterrupt
        if choice == "1":
            return True
        if choice == "2":
            return False
        print("Please enter 1 or 2.")


def main() -> None:
    print("=" * 50)
    print("             TERMINAL VIDEO DOWNLOADER")
    print("=" * 50)
    print("Use only for content you own or are authorized to download.\n")

    url = input("Paste YouTube video or playlist URL: ").strip()
    if not is_valid_youtube_url(url):
        print("Invalid URL. Please enter a valid YouTube URL.")
        return

    print("\nFetching video information...")
    try:
        # Initially inspect the URL as a single item. If it is a playlist,
        # ask the user before fetching the full playlist.
        info = get_video_info(url, download_playlist=True)
    except Exception as error:
        print(f"\nCould not retrieve video information: {error}")
        return

    try:
        download_playlist = ask_playlist_mode(info)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    representative = get_representative_video_info(info)
    print("\nTitle:   ", info.get("title") or representative.get("title", "Unknown"))
    print("Duration:", format_duration(representative.get("duration")))
    print("Uploader:", representative.get("uploader", "Unknown"))

    ffmpeg_available = shutil.which("ffmpeg") is not None
    selected = choose_download(representative, ffmpeg_available)
    if selected is None:
        print("Cancelled.")
        return

    selected_format, audio_only = selected
    destination = ask_destination()
    if destination is None:
        print("Cancelled.")
        return

    print(f"\nSave location: {destination}")
    print("\nStarting download...")
    try:
        download_media(
            url=url,
            format_selector=selected_format,
            destination=destination,
            download_playlist=download_playlist,
            audio_only=audio_only,
        )
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as error:
        print(f"\nDownload failed: {error}")
        print(
            "Check your internet connection, update yt-dlp, confirm the "
            "content is accessible to you, and verify that FFmpeg is "
            "installed if you selected MP3 or high-resolution video."
        )


if __name__ == "__main__":
    main()
