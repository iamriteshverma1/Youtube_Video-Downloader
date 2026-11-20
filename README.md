# YouTube Downloader

A lightweight, terminal-based YouTube downloader built with Python. It supports individual videos, complete playlists, video quality selection, and audio-only downloads in MP3 format.

## Features

- Download individual videos.
- Download complete playlists.
- Select available video quality (360p, 480p, 720p, 1080p, etc.).
- Download audio only in MP3 format.
- Choose a custom folder to save downloaded files.
- Display download progress in the terminal.
- Generate a standalone Windows `.exe` application.

**Important:** Use this application only for content you own or have permission to download, and in accordance with YouTube's terms. It does not bypass DRM, paywalls, sign-in requirements, or other access controls.

---

## 1. Requirements

Make sure you have the following installed:

- Python 3.10 or later
- FFmpeg
- Deno (recommended for yt-dlp JavaScript support)
- Windows 10/11 (for the Windows executable)

### Install Python

Download Python from:

https://www.python.org/downloads/

During installation, enable **Add Python to PATH**.

### Install FFmpeg

Open PowerShell and run:

```powershell
winget install Gyan.FFmpeg
```

Verify the installation:

```powershell
ffmpeg -version
```

FFmpeg is required for:
- Converting audio to MP3.
- Merging separate video and audio streams.

### Install Deno

Deno provides JavaScript runtime support for yt-dlp.

```powershell
winget install DenoLand.Deno
```

Verify:

```powershell
deno --version
```

Restart your terminal after installing external tools.

---

## 2. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
```

Move into the project directory:

```bash
cd youtube-downloader
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## 3. Create a Virtual Environment

Create the environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

---

## 4. Install Python Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install all project dependencies:

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file contains:

```txt
yt-dlp[default]>=2025.1.15
pyinstaller>=6.0
```

---

## 5. Run the Application

Start the downloader:

```bash
python main.py
```

### Download options

The application supports:

1. Individual video downloads.
2. Complete playlist downloads.
3. Video quality selection.
4. Audio-only downloads in MP3 format.
5. Custom download destination.

Enter the destination folder when prompted.

Example:

```text
D:\My Videos
```

If you leave the destination blank, the default folder is:

```text
%USERPROFILE%\Downloads\YouTubeDownloader
```

---

## 6. Generate a Windows EXE

You can convert the Python application into a standalone executable using PyInstaller.

Run:

```powershell
pyinstaller --clean --onefile --console --name YouTubeDownloader --collect-all yt_dlp main.py
```

After the build completes, the executable will be available at:

```text
dist\YouTubeDownloader.exe
```

Copy `YouTubeDownloader.exe` to your desktop.

Double-click it to launch the terminal application without opening VS Code.

**Note:** FFmpeg and Deno are external dependencies and may need to be installed separately on the computer running the executable. The executable bundles Python and the packaged Python dependencies, not necessarily these external tools.

---

## 7. Project Structure

```text
youtube-downloader/
│
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── tests/
│   └── test_helpers.py
│
├── build/
│
└── dist/
    └── YouTubeDownloader.exe
```

---

## 8. Troubleshooting

### FFmpeg not found

Check:

```powershell
ffmpeg -version
```

If the command is not recognized, verify that FFmpeg is installed and its `bin` directory is included in your PATH.

### Deno not found

Check:

```powershell
deno --version
```

Restart your terminal after installation.

### Update yt-dlp

If video information cannot be retrieved, update yt-dlp:

```powershell
python -m pip install --upgrade "yt-dlp[default]"
```

### Download or format errors

- Check your internet connection.
- Confirm that the content is accessible to you.
- Check the available video qualities.
- Update yt-dlp.
- Make sure FFmpeg is installed when merging or converting media.

---

## 9. License

This project is intended for educational and personal use. See the `LICENSE` file for licensing information.

Always respect copyright, content ownership, and the platform's terms of service.
