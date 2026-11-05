# Session portability

The phone screen has a Session button next to Cherrygram's QR button. The import
popup offers Telethon/Pyrogram SQLite `.session`, a ZIP containing `tdata/` or its
contents, Telethon String Session, Pyrogram String Session, and a hexadecimal
256-byte Auth Key with DC ID 1–5. Documents are selected with Android's system
file picker. No broad storage permission is needed.

Under Settings → Devices → This device, Export account session offers the same
six output formats. String sessions and the manual credentials are saved as text;
Desktop authorization is saved as a ZIP. The destination is chosen with Android's
system document creation dialog. Export reuses this device's authorization.

## Supported formats and behavior

- Telethon StringSession v1, IPv4 and IPv6 layouts; SQLite v7 export, readable by
  stable Telethon 1.x and migrated by later versions. SQLite import reads named
  fields, including databases with newer optional columns.
- Pyrogram old 32-bit/64-bit and current string layouts; SQLite schema v3 export.
- Modern Desktop `key_data` / TDF$ authorization files, including local passcodes
  and multiple accounts (select one to import). Export creates minimal,
  single-account tdata without a local passcode; Desktop rebuilds caches.
- Production user accounts only. Test sessions and bots are rejected. The imported
  key is checked with `users.getUsers(inputUserSelf)` before the normal login
  completion path saves user data. Existing accounts are never overwritten.
- Invalid/revoked keys, mismatched user IDs and verification timeouts clear the
  imported local key. No `auth.logOut` request is sent to revoke the source key.
- Archives must be ZIP, with one tdata root; path traversal, duplicate entries,
  excessive entry counts and more than 64 MiB unpacked are rejected. Authorization
  files are read in memory. Remove Desktop caches before zipping large tdata.
  Legacy pre-key_data Desktop formats and custom Desktop data-file names are not
  supported.
- A `.session` must be a standalone database, cleanly closed by its source client;
  WAL sidecar recovery is not performed.

The export warning explains that the output grants full account access. Session
values are never logged or automatically copied to the clipboard or uploaded.
Temporary SQLite files are in the private app cache and deleted after use.
Do not run two clients sharing one authorization concurrently: Telegram can revoke
it (`AUTH_KEY_DUPLICATED`). Importing a key does not create an independent device
session. Revoking this device also invalidates the exported copies.

## Validation

Run `bash tests/sessions/run.sh` with JDK 17, Python 3 and `cryptography==50.0.2`.
The tests use synthetic keys, fixed Python struct/base64 vectors, and independently
implemented Python PBKDF2/AES-IGE fixtures, including passcoded multi-account
input. Java exports are independently decoded and verified by Python. No live
Telegram credentials are needed.

Android SQLite/stream instrumentation tests are in
`TMessagesProj_AppTests/src/androidTest/java/uz/unnarsx/cherrygram/sessions/SessionFilesTest.java`;
they have not been run because the base Android sources are incomplete.

The Android UI, SAF/SQLite integration and native login need an APK/device check:
first and additional account login; canceled pickers; invalid and expired keys;
all six export formats opened in their respective clients; local-passcoded and
multi-account tdata; rotation/back/fragment destruction during verification;
light/dark theme, Russian/English, narrow screens and large font settings.

## GitHub Actions and the upstream build blocker

`.github/workflows/session-build.yml` runs the codec tests on push/PR and attempts
a debug APK on push/manual dispatch. APKs are uploaded as
`Cherrygram-session-debug`. The build does not invoke upstream Telegram upload
finalizers and uses an ephemeral debug signing key. It cannot update an installed
copy signed by the upstream developer; debug signing also changes between runs.

The fork's public `main` at `3050af6` **is not self-contained**. Its `.gitignore`
excludes required code: `Extra.kt`, `jni/security`, `jni/colorado`, and multiple
camera, chat-menu and folder classes that the tracked source still references.
`tools/ci/check_sources.py` lists the missing paths and fails before expensive
Android setup. A passing codec job alone does not establish that an APK builds.

Supply the missing code from a source you are authorized to use. Keep private code
and credentials out of this public fork. For Actions, a private build-input
repository can hold those files at their original paths relative to the project
root. Set the repository variable `CHERRYGRAM_BUILD_INPUTS_REPO` to `owner/repo`
and secret `CHERRYGRAM_BUILD_INPUTS_TOKEN` to a token with read access to that
repository. Only absent, explicitly upstream-excluded source paths are restored;
feature files and tracked source are not replaced. This step is disabled on PRs.

Once inputs are supplied, rerun Session portability. Further upstream build issues
may still need resolving: no Android build has been validated from the incomplete
public source tree. The debug job uses the checked-in Firebase configuration;
configure your own Firebase/API credentials in your private build inputs for a
redistributable application.

## Format references

Implementation was checked against the source formats rather than embedding a
Python runtime in the app:

- https://github.com/batreller/AndroidTelePorter/blob/main/AndroidTelePorter/androidsession.py
- https://github.com/LonamiWebs/Telethon/tree/v1/telethon/sessions
- https://github.com/pyrogram/pyrogram/tree/master/pyrogram/storage
- https://github.com/thedemons/opentele/tree/main/src/td

AndroidTelePorter helped confirm that the mobile permanent auth key and main DC,
with the user ID, provide the portable authorization. The native implementation
accesses them on the account network thread rather than parsing a concurrently
written `tgnet.dat`.
