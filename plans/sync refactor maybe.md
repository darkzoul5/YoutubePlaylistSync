You need to separate playlist sync state from download attempts.

The goal should not be “all 400 downloaded in one run”. It should be:

All downloadable items eventually reach a final state. Temporary failures are retried later. Permanent failures are recorded clearly.

Use statuses like:

queued
downloading
completed

temporary_failed
rate_limited
verification_required

unavailable
private
geo_blocked
copyright_blocked
age_restricted
unsupported
failed_permanent

skipped_by_user
removed_from_playlist

Main logic:

1. Fetch playlist metadata
2. Create/update queue items for all playlist videos
3. Download available queued items
4. On normal temporary errors: retry later
5. On YouTube rate-limit / bot check: pause the whole sync
6. On unavailable/private/deleted videos: mark as permanent failure
7. On next sync: retry only retryable items

Important: do not delete queue records just because download failed. Keep them as sync records.

For each video, store:

video_id
playlist_id
playlist_position
wanted_format: audio | video
status
failure_type
failure_message
attempt_count
last_attempt_at
next_retry_at
is_retryable
local_file_path

Retry behavior:

temporary_failed -> retry with backoff
rate_limited -> pause playlist/app queue, retry much later
verification_required -> pause until user action
unavailable/private/deleted -> do not retry often
geo/age restricted -> do not retry unless settings/auth changed

Example backoff:

attempt 1: retry after 10 minutes
attempt 2: retry after 1 hour
attempt 3: retry after 6 hours
attempt 4: retry after 24 hours
attempt 5+: retry manually or during next scheduled sync

For the user, show a sync summary:

Playlist sync partially completed

Downloaded: 200
Queued: 0
Retry later: 80
Needs attention: 1
Unavailable: 119

The playlist is still tracked. Retryable items will be attempted again in the next sync.

Best behavior for the 400-item example:

200 downloaded
50 unavailable/private/deleted -> mark permanent
149 temporary/rate-limited -> retry later
1 bot/verification error -> pause sync and ask user

Do not cancel the whole sync as “failed”. Mark it as:

completed_with_issues
paused_needs_attention
partially_synced

In UI terms, the playlist should have a health/status:

Synced
Syncing
Partially synced
Paused - needs attention
Error

The most important rule:

Never lose the reason why an item did not download.

That lets your app eventually download everything possible without repeatedly hammering YouTube or confusing the user.


## What to change to match the plan

Fix the destructive UPSERT behavior in src/app/core/database/db.py / SyncService.sync_from_config() so scans update metadata (title/index/last_seen) but do not overwrite existing downloaded/local_filename (and later: status/failure fields).

Introduce a persistent table (or extend playlist_items) with:
status, failure_type, failure_message, attempt_count, last_attempt_at, next_retry_at, is_retryable, wanted_format, local_file_path.

Update ActionExecutor / worker layer to write transitions into DB (queued → downloading → completed / temporary_failed / rate_limited / verification_required / failed_permanent).

Change “next sync” selection to only pick queued or retryable && next_retry_at <= now, not everything each time.
Add summary/health states (partially_synced, paused_needs_attention, etc.) based on counts.