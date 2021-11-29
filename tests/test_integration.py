"""Real youtube-dl transfers against local generated media, never YouTube."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from khan_dl.media import MediaDownloader
from khan_dl.options import DownloadOptions


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class LocalMediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        cls.root = Path(cls.fixture.name)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi',
                        '-i', 'color=c=blue:s=64x64:d=0.3', '-f', 'lavfi',
                        '-i', 'sine=frequency=440:duration=0.3', '-shortest', '-c:v', 'mpeg4',
                        '-c:a', 'aac', '-y', str(cls.root / 'clip.mp4')], check=True)
        class Handler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        (cls.root / 'captions.vtt').write_text(chr(10).join(['WEBVTT', '',
            '00:00:00.000 --> 00:00:00.250', 'Hello course', '']), encoding='utf-8')
        (cls.root / 'page.html').write_text('<html><title>Lesson</title><video controls>'
            '<source src="clip.mp4" type="video/mp4">'
            '<track kind="subtitles" src="captions.vtt" srclang="en" label="English">'
            '</video></html>', encoding='utf-8')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(cls.root)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:{}/clip.mp4'.format(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.fixture.cleanup()

    def probe(self, path):
        output = subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)])
        return json.loads(output)['streams']

    def test_video_transfer_and_progress_are_real(self):
        with tempfile.TemporaryDirectory() as directory:
            events = []
            media = MediaDownloader(DownloadOptions(output=directory, quiet=True, retries=0), progress=events.append)
            media.download(self.url, title='lesson')
            path = Path(directory) / 'lesson.mp4'
            self.assertEqual(path.read_bytes(), (self.root / 'clip.mp4').read_bytes())
            self.assertEqual(events[-1].status, 'finished')
            self.assertTrue(any(stream['codec_type'] == 'video' for stream in self.probe(path)))

    def test_audio_extraction_produces_real_mp3(self):
        with tempfile.TemporaryDirectory() as directory:
            media = MediaDownloader(DownloadOptions(output=directory, mode='audio', quiet=True, retries=0))
            media.download(self.url, title='lecture')
            streams = self.probe(Path(directory) / 'lecture.mp3')
            self.assertEqual([stream['codec_type'] for stream in streams], ['audio'])
            self.assertEqual(streams[0]['codec_name'], 'mp3')

    def test_metadata_does_not_create_download_files(self):
        with tempfile.TemporaryDirectory() as directory:
            media = MediaDownloader(DownloadOptions(output=directory, quiet=True, retries=0))
            self.assertEqual(media.extract(self.url)['ext'], 'mp4')
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_video_conversion_produces_matroska(self):
        with tempfile.TemporaryDirectory() as directory:
            media = MediaDownloader(DownloadOptions(output=directory, video_format='mkv', quiet=True, retries=0))
            media.download(self.url, title='converted')
            path = Path(directory) / 'converted.mkv'
            self.assertTrue(path.exists())
            self.assertTrue(any(stream['codec_type'] == 'video' for stream in self.probe(path)))

    def test_subtitle_only_converts_vtt_to_srt_without_video(self):
        with tempfile.TemporaryDirectory() as directory:
            options = DownloadOptions(output=directory, subtitle_only=True, subtitle_languages=('en',),
                                      subtitle_format='srt', quiet=True, retries=0)
            media = MediaDownloader(options)
            media.download(self.url.replace('clip.mp4', 'page.html'), title='captions')
            self.assertIn('Hello course', (Path(directory) / 'captions.en.srt').read_text())
            self.assertFalse((Path(directory) / 'captions.mp4').exists())

    def test_archive_records_only_completed_media(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / 'archive.txt'
            media = MediaDownloader(DownloadOptions(output=directory, archive=str(archive),
                                                   write_metadata=True, quiet=True, retries=0))
            media.download(self.url, title='archived')
            self.assertTrue(archive.read_text().strip())
            media.download(self.url, title='archived')
            self.assertEqual(len(archive.read_text().splitlines()), 1)
            self.assertTrue((Path(directory) / 'archived.info.json').exists())
