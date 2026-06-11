# MP3 Metadata Plan

## Subject Area

- Add MP3 tag writing for downloaded YouTube playlist items.
- Scope is limited to `.mp3` outputs produced by `audio` mode and the MP3 side of `both` mode.
- Metadata is sourced from YouTube/yt-dlp and embedded after audio extraction.

## Goal

- Write useful MP3 metadata for downloaded playlist items without affecting video-only downloads.
- Keep the implementation reliable when optional fields are missing.
- Preserve successful downloads even when metadata embedding partially fails.
- Provide a per-playlist setting to enable or disable MP3 metadata embedding.

## Required Metadata

- `title` ← video title
- `artist` ← uploader, fallback to channel
- `album` ← album name if present
- `tracknumber` ← playlist index
- `date` / `year` ← upload date
- `comment` ← source URL
- `genre` ← if available
- `album_art` ← thumbnail

## Configuration Requirement

- Add a per-playlist setting to turn MP3 metadata embedding on or off.
- Default should be explicitly defined during implementation; recommended default is `enabled` for new configs.
- The setting should only affect `.mp3` metadata writing and should not change download selection, extraction, or `.mp4` handling.

## Current Constraints

- The current playlist scan keeps only a minimal item shape: title, video id, and playlist index.
- The scanner uses flat extraction, which is sufficient for diffing but not for full tag data.
- MP3 extraction currently transcodes audio but does not write ID3 metadata.

## Implementation Strategy

- Keep playlist diffing fast by retaining the current flat scan for remote playlist structure.
- Fetch full metadata only for items that are actually going to be downloaded or repaired.
- Write metadata only after MP3 extraction completes successfully.
- Treat metadata embedding as a post-processing step that can fail softly without discarding the MP3.

## Work Breakdown

### 1. Extend the metadata model

- Add optional fields to `PlaylistItem` for:
  - uploader
  - channel
  - album
  - upload_date
  - genre
  - thumbnail_url
  - webpage_url
- Keep `artist` as a derived value instead of storing a separate field.

### 2. Fetch full per-video metadata

- Introduce a metadata fetch step for each item selected for download.
- Use yt-dlp per-video extraction to retrieve richer fields than the flat playlist entry provides.
- Prefer canonical values from the video page payload for upload date, uploader/channel, album, genre, thumbnail, and source URL.

### 3. Carry metadata through the download pipeline

- Ensure the enriched `PlaylistItem` reaches the download job and post-processing stage.
- Keep this propagation in-memory unless restart-safe metadata persistence becomes necessary later.
- Avoid changing unrelated sync behavior for video-only items.
- Carry the per-playlist MP3 metadata enabled/disabled setting into the post-processing step.

### 4. Add an MP3 tag writer

- Add `mutagen` as the ID3 writing dependency.
- Implement a focused tagging component that maps `PlaylistItem` metadata into ID3 frames.
- Omit fields when the source value is missing instead of writing placeholders.

### 5. Map fields into ID3 tags

- `title` → video title
- `artist` → uploader, fallback to channel
- `album` → album if present
- `tracknumber` → playlist index
- `date/year` → parsed upload date
- `comment` → canonical source URL
- `genre` → genre if present

### 6. Embed album art

- Download the selected thumbnail for the video after the media download succeeds.
- Attach thumbnail data as embedded cover art when the image type is supported.
- Fail soft if thumbnail retrieval or embedding fails, and keep the MP3 intact.

### 7. Integrate into modes

- `audio` mode:
  - download source media
  - extract MP3
  - write MP3 tags only when the setting is enabled
  - delete temporary/source MP4 if configured
- `both` mode:
  - download source media
  - extract MP3
  - write MP3 tags only when the setting is enabled
  - keep MP4 unchanged
- `video` mode:
  - no MP3 tagging path

### 8. Add configuration surface

- Add the new per-playlist setting to the playlist config model and default config output.
- Expose the setting in the playlist configuration UI, not as a global app setting.
- Keep the naming explicit, for example `write_mp3_metadata` or `embed_mp3_metadata`.

## Error Handling Rules

- If download fails, no tagging runs.
- If extraction fails, no tagging runs.
- If metadata embedding is disabled, skip the tagging step entirely.
- If tagging fails, mark the tag step as failed in logs/events but keep the MP3 file.
- If thumbnail embedding fails, continue with text metadata only.
- Missing `album` or `genre` is normal and should not be treated as an error.

## Testing Plan

- Unit test metadata mapping from yt-dlp info to the internal metadata model.
- Unit test ID3 writing against a temporary MP3 fixture.
- Unit test fallback behavior:
  - uploader missing, channel present
  - album missing
  - genre missing
  - thumbnail missing
- Integration test the audio post-processing path with tagging mocked.
- Integration test the both-mode MP3 path with tagging mocked.

## Documentation Updates

- Document that MP3 tags are written only for `.mp3` outputs.
- Document the new per-playlist setting that enables or disables MP3 metadata embedding.
- Document the field fallback rules, especially artist and album behavior.
- Document that album art comes from the video thumbnail, not playlist artwork.
- Document that some YouTube items will not expose album or genre information.

## Dependency Decision

- Recommended library: `mutagen`
- Reason:
  - direct ID3 support
  - reliable field-level control
  - suitable for embedding cover art
  - avoids depending on ffmpeg metadata flags for all tag logic

## Delivery Order

- First: add config setting and defaults
- Second: extend metadata model and add full metadata fetch
- Third: add MP3 tag writer and field mapping
- Fourth: add thumbnail embedding
- Fifth: wire tagging into `audio` and `both`
- Sixth: add tests and docs
