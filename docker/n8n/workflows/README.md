# 🤖 n8n workflows

All workflows send to Telegram using `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from `docker/n8n/.env`,
and read service API keys from `docker/homepage/homepage.secret`. No keys live in these files.

| Workflow | When | Needs |
|---|---|---|
| `home-bot-telegram.json` | every 15 s | the bot (requests, subs, PDFs, **/todo**, delete & trim, status, power) + SSH key for trim |
| `home-power-telegram.json` | minute / hourly / 9pm | grid & battery alerts, hourly status, daily summary |
| `power-advice.json` | every 2 min | solar-surplus tips, grid-off low battery, heavy load, **5pm grid-off warning** |
| `morning-briefing.json` | 7am | **Google Calendar** credential |
| `weekly-maintenance.json` | Sunday 6pm | `GITHUB_TOKEN` (release watch, to-dos) |
| `stalled-downloads.json` | hourly | nothing extra |
| `deploy-on-push.json` | every 5 min | `GITHUB_TOKEN` + **n8n-deploy** SSH key on CT 201 |
| `spending-tracker.json` | new email / 1st of month | **Microsoft Outlook** + **Google Sheets** credentials |
| `daily-data-report.json`, `new-on-jellyfin.json` | as before | |

Only **one** workflow may read the bot's messages (the home bot). Don't activate old copies.

## 1. GitHub token (to-dos, release watch, deploy on push)

github.com → Settings → Developer settings → **Fine-grained tokens** → Generate:
- Repository access: **only `homelab`**
- Permissions: **Contents: Read-only**, **Issues: Read and write** (Metadata is added automatically)

Add to `docker/n8n/.env`:
```
GITHUB_TOKEN=github_pat_...
GITHUB_REPO=theOGpython/homelab
```
then `docker compose up -d --force-recreate n8n`.

## 2. Deploy key on CT 201 (deploy on push)

In CT 201:
```bash
apt-get install -y openssh-server && systemctl enable --now ssh
cp /opt/homelab/scripts/homelab-deploy /usr/local/bin/ && chmod +x /usr/local/bin/homelab-deploy
ssh-keygen -t ed25519 -N "" -C n8n-deploy -f /root/n8n-deploy-key
mkdir -p /root/.ssh && echo "command=\"/usr/local/bin/homelab-deploy\",restrict $(cat /root/n8n-deploy-key.pub)" >> /root/.ssh/authorized_keys
cat /root/n8n-deploy-key        # copy into n8n, then:
rm /root/n8n-deploy-key /root/n8n-deploy-key.pub
```
n8n → Credentials → **SSH Private Key**: host `192.168.3.201`, port 22, user `root`. Select it in **Deploy on the server**.
The key can only run the deploy script (which pulls the repo and redeploys named stacks).

## 3. Google (Calendar for the briefing, Sheets for spending)

console.cloud.google.com → new project → **APIs & Services**:
1. Enable **Google Calendar API** and **Google Sheets API** (+ Google Drive API for the sheet picker).
2. **OAuth consent screen**: External, add yourself as a test user, then **Publish app → In production**
   (otherwise Google expires the login every 7 days; you'll click past an "unverified app" warning once).
3. **Credentials → Create OAuth client ID → Web application**. Authorised redirect URI: copy the
   **OAuth Redirect URL** shown in n8n's credential window.
4. In n8n create **Google Calendar OAuth2** and **Google Sheets OAuth2** credentials with that client ID/secret.

Spreadsheet: create a Google Sheet with a tab named **Transactions** and headers
`Date | Month | Type | Amount | Category | Description | Balance | Source | EmailId`; paste its URL into both Sheets nodes.

## 4. Microsoft Outlook (spending tracker)

entra.microsoft.com (sign in with your Outlook account) → **App registrations → New registration**:
- Supported accounts: **"Accounts in any organizational directory and personal Microsoft accounts"**
- Redirect URI (Web): n8n's **OAuth Redirect URL** from the credential window
- **Certificates & secrets** → New client secret; **API permissions** → Microsoft Graph → delegated **Mail.Read**, **offline_access**

In n8n create a **Microsoft Outlook OAuth2** credential with the app's client ID and secret, then connect.
Tune `SENDERS` / `CATEGORIES` at the top of **Parse bank & token alerts** for your banks.

## 5. Import and activate

n8n → **Import from File** for each workflow → select credentials where asked → **Save** → **Activate**.
Test any one immediately with the ▶ button on its trigger node.
