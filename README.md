# Terminal Video Downloader

A small Python command-line project that displays available video resolutions and lets you select a quality or audio-only format.

> **Responsible use:** Download only videos you own or have explicit permission to download, and only where the platform permits it. Respect copyright and YouTube's Terms of Service. This project does not bypass DRM, paywalls, sign-in requirements, or other access controls.

## Features

- Accepts a YouTube URL in the terminal
- Checks that the URL uses a supported YouTube domain
- Displays the title, uploader, and duration
- Detects available video heights (for example, 360p, 720p, and 1080p)
- Offers a selected resolution, best available quality, or audio-only download
- Shows download progress
- Saves files in the local `downloads/` folder
- Disables playlist downloads by default
- Retries some network and fragment failures

## Requirements

- Python 3.10 or newer
- Internet connection
- FFmpeg (recommended for merging separate video and audio streams)

## Windows setup (VS Code / PowerShell)

### 1. Open the project folder

```powershell
cd path\to\youtube-downloader
```

### 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install FFmpeg

Install FFmpeg and add its `bin` directory to your Windows PATH. Open a new terminal and check:

```powershell
ffmpeg -version
```

FFmpeg is recommended because some high-resolution videos provide video and audio as separate streams. Without FFmpeg, the program tries to select a combined audio/video format, which may limit the maximum available resolution. Audio-only mode downloads the best available audio stream without converting it to MP3.

### 5. Run the project

```powershell
python main.py
```

Paste a YouTube URL, inspect the available qualities, and enter the number for the format you want.

## Project structure

```text
youtube-downloader/
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
└── tests/
    └── test_helpers.py
```

Downloaded media is saved under `downloads/`. That folder is intentionally excluded from Git.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Update yt-dlp

Websites can change their delivery formats. If extraction stops working, update yt-dlp:

```powershell
python -m pip install --upgrade yt-dlp
```

## Troubleshooting

- **FFmpeg not found:** Install FFmpeg, add its `bin` folder to PATH, and restart the terminal.
- **No formats found:** The video may be unavailable, restricted, or not accessible to your account.
- **Extraction errors:** Update yt-dlp and retry. Do not attempt to bypass access restrictions.
- **PowerShell activation error:** Use the Command Prompt activation command shown above.

## License

MIT. See [LICENSE](LICENSE).
