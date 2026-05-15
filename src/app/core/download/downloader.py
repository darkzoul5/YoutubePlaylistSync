from __future__ import annotations

from typing import Optional

from .queue_manager import DownloadJob, JobState


class Downloader:
    """
    Thin wrapper around yt-dlp usage. For MVP, this is a placeholder
    where actual download logic will land (audio/video/both).
    """

    def __init__(self, yt_dlp_path: Optional[str] = None, ffmpeg_path: Optional[str] = None) -> None:
        self.yt_dlp_path = yt_dlp_path
        self.ffmpeg_path = ffmpeg_path

    async def handle_job(self, job: DownloadJob):
        try:
            job.state = JobState.DOWNLOADING
            await self._download(job)
            job.state = JobState.COMPLETED
        except Exception as exc:  # pragma: no cover - environment dependent
            job.state = JobState.FAILED
            job.error = str(exc)

    async def _download(self, job: DownloadJob):
        # Use yt-dlp Python API, executed in a worker thread
        import asyncio

        def run():
            import yt_dlp  # type: ignore

            outtmpl = str(job.output_path)
            if job.mode == "audio":
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": outtmpl,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "0",
                        }
                    ],
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True,
                }
            else:  # video
                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": outtmpl,
                    "noplaylist": True,
                    "quiet": True,
                    "no_warnings": True,
                }

            if self.ffmpeg_path:
                ydl_opts["ffmpeg_location"] = self.ffmpeg_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[attr-defined]
                ydl.download([job.url])

        await asyncio.to_thread(run)
