import unittest

from main import (
    build_format_selector,
    format_duration,
    get_available_qualities,
    is_valid_youtube_url,
)


class DownloaderHelperTests(unittest.TestCase):
    def test_valid_youtube_urls(self):
        self.assertTrue(is_valid_youtube_url("https://www.youtube.com/watch?v=abc"))
        self.assertTrue(is_valid_youtube_url("https://youtu.be/abc"))

    def test_rejects_non_youtube_urls(self):
        self.assertFalse(is_valid_youtube_url("https://example.com/video"))
        self.assertFalse(is_valid_youtube_url("not-a-url"))

    def test_get_available_qualities_is_unique_and_sorted(self):
        info = {
            "formats": [
                {"height": 720, "vcodec": "avc1"},
                {"height": 360, "vcodec": "avc1"},
                {"height": 720, "vcodec": "vp9"},
                {"height": 1080, "vcodec": "none"},
            ]
        }
        self.assertEqual(get_available_qualities(info), [360, 720])

    def test_format_selector(self):
        self.assertEqual(
            build_format_selector(height=720, ffmpeg_available=True),
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )
        self.assertEqual(
            build_format_selector(audio_only=True),
            "bestaudio/best",
        )

    def test_duration_formatting(self):
        self.assertEqual(format_duration(625), "10:25")
        self.assertEqual(format_duration(3725), "01:02:05")
        self.assertEqual(format_duration(None), "Unknown")


if __name__ == "__main__":
    unittest.main()
