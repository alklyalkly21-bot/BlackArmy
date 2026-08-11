# BlackArmy Lab v3

APK-ready Android test controller with Telegram integration.

## Included
- Real Telegram polling.
- `/ping`, `/status`, `/device`, `/help`.
- Explicit user-facing file/contact workflow.
- No remote shell.
- No silent contact extraction.
- No silent file collection.
- No hidden screenshot capture.
- No arbitrary remote command execution.
- Minimal Android permission: `INTERNET`.
- Token is entered at runtime rather than embedded in source.

## Build

Install Buildozer and Android build prerequisites, then:

```bash
buildozer android debug
```

APK output is placed in `bin/`.

## Security

The Bot Token from the original uploaded source was exposed. Revoke it and create a new token before testing.

For a release build, use your own signing key and keep it outside the project repository.
