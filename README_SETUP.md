# MATES Ballot Monitor — GitHub Actions Setup Guide

Run your ballot monitor free in the cloud using GitHub Actions.
No server, no credit card, works even when your PC is off.

---

## Step 1 — Create a GitHub account

If you don't have one, sign up at **https://github.com** (free).

---

## Step 2 — Create a new private repository

1. Click the **+** icon (top right) → **New repository**
2. Name it: `mates-monitor`
3. Set visibility to **Private** (keeps your credentials safer)
4. Click **Create repository**

---

## Step 3 — Upload the files

You need to upload these 4 files, keeping the folder structure:

```
mates-monitor/
├── mates_ballot_monitor.py
├── state.json
├── README.md
└── .github/
    └── workflows/
        └── monitor.yml
```

**Easiest way — GitHub web interface:**

1. In your new repo, click **Add file → Upload files**
2. Upload `mates_ballot_monitor.py`, `state.json`, and `README.md`
3. Click **Commit changes**

Then create the workflow file:
1. Click **Add file → Create new file**
2. In the filename box type: `.github/workflows/monitor.yml`
   *(GitHub will auto-create the folders as you type the `/`)*
3. Paste the contents of `monitor.yml` into the editor
4. Click **Commit changes**

---

## Step 4 — Get a Gmail App Password

1. Go to your Google Account → **Security** → enable **2-Step Verification**
2. Visit: **https://myaccount.google.com/apppasswords**
3. Click **Create app password**, name it `MATES Monitor`
4. Copy the 16-character password — remove spaces → e.g. `abcdefghijklmnop`

---

## Step 5 — Add your credentials as GitHub Secrets

GitHub Secrets store your passwords safely — they're never visible in logs.

1. In your repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add these three secrets:

| Secret name | Value |
|-------------|-------|
| `SENDER_EMAIL` | your Gmail address (e.g. `you@gmail.com`) |
| `SENDER_PASSWORD` | 16-char App Password, no spaces |
| `RECIPIENT_EMAIL` | where to receive alerts (can be same Gmail) |

---

## Step 6 — Test it manually

1. Go to the **Actions** tab in your repo
2. Click **MATES Ballot Monitor** in the left sidebar
3. Click **Run workflow → Run workflow** (green button)
4. Wait ~30 seconds, then click the run to see the logs

You should see:
```
Checking MATES ballot status...
  Ballot status detected: CLOSED
  No change (still CLOSED). Nothing to do.
  Done.
```

And `state.json` in your repo will be updated with today's date. ✅

---

## How it runs automatically

The workflow is scheduled via this cron expression in `monitor.yml`:

```
0 22 * * *   →   runs at 22:00 UTC = 8:00 AM Melbourne AEST
```

> **Daylight saving note:** Melbourne switches between AEST (UTC+10) and AEDT (UTC+11).
> - AEST (May–Oct): `0 22 * * *` = 8:00 AM ✅
> - AEDT (Oct–Apr): `0 21 * * *` = 8:00 AM ✅
>
> You can update the cron line in `monitor.yml` when clocks change, or just leave it —
> an hour's difference doesn't matter for this use case.

---

## What happens when the ballot opens?

You'll receive an email:

> **Subject:** 🟢 MATES Ballot is NOW OPEN — Register Now!
>
> Good news! The MATES (Subclass 403) ballot status has changed from 'PENDING' to ACTIVE.
> Register now at: [link]

---

## Keeping the workflow active

> ⚠️ GitHub disables scheduled workflows on **inactive repos after 60 days**.

To prevent this, simply visit your repo at least once every 2 months and click
**Enable workflow** if prompted — or make any small edit (e.g. update README).

Alternatively, add this to `monitor.yml` under `on:` to auto-re-enable via manual runs:
```yaml
  workflow_dispatch:
```
(Already included in the provided file.)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Email not sending | Check `SENDER_PASSWORD` secret has no spaces; verify Gmail 2FA is on |
| Workflow not running | Check Actions tab → ensure workflows are enabled for the repo |
| `Status detected: None` | The page structure may have changed — raise an issue |
| Workflow disabled after inactivity | Go to Actions tab → click "Enable workflow" |
