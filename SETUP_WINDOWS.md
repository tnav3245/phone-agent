# Windows setup guide

Do these steps once, in order. Plan on about an hour. Each step ends with a ✅
check. Don't move on until that check passes.

You need:
- A Windows PC and your iPhone's USB cable
- Your Anthropic API key (from console.anthropic.com)
- Your Apple ID
- Apple Pay set up in Wallet with the card you want to use

---

## Step 1: Install Python

1. Go to https://www.python.org/downloads/ and download the latest **Python 3.12 or 3.13** installer.
2. Run it. On the first screen, **check "Add python.exe to PATH"**, then click **Install Now**.

✅ Open **PowerShell** (Start menu → type "PowerShell"). Run `python --version`. It should print `Python 3.12...` or `3.13...`.

## Step 2: Let Windows talk to your iPhone

1. Install **Apple Devices** from the Microsoft Store. It includes the iPhone USB drivers.
2. Plug in your iPhone and unlock it. When the phone asks **"Trust This Computer?"**, tap **Trust** and enter your passcode.

✅ Your iPhone shows up in the Apple Devices app.

## Step 3: Download the code

1. Go to https://github.com/tnav3245/phone-agent, click the green **Code** button, then **Download ZIP**.
2. Unzip it to `C:\phone-agent`. That folder should contain `run.py`, not another folder.

## Step 4: Install the Python packages

In PowerShell:

```powershell
cd C:\phone-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you get an error that **"running scripts is disabled"**, run this once, then repeat the `Activate.ps1` line:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

✅ `pip install` ends with "Successfully installed ...". Your prompt now starts with `(.venv)`.

## Step 5: Add your API key

```powershell
copy .env.example .env
notepad .env
```

Paste your key after `ANTHROPIC_API_KEY=` (no spaces or quotes), then save and close.
**Never share this file.** It's already excluded from GitHub.

## Step 6: Get WebDriverAgent, the "thumb"

1. Go to https://github.com/appium/WebDriverAgent/releases and open the latest release.
2. Under **Assets**, download **`WebDriverAgentRunner-Runner.zip`**. That's the build for real devices, not the simulator.
3. Turn it into an `.ipa` file that Sideloadly can install. In PowerShell, from `C:\phone-agent`:

```powershell
Expand-Archive "$HOME\Downloads\WebDriverAgentRunner-Runner.zip" -DestinationPath wda_tmp -Force
New-Item -ItemType Directory -Force wda_tmp\Payload | Out-Null
Move-Item wda_tmp\WebDriverAgentRunner-Runner.app wda_tmp\Payload\ -Force
Compress-Archive wda_tmp\Payload -DestinationPath WebDriverAgent.zip -Force
Rename-Item WebDriverAgent.zip WebDriverAgent.ipa -Force
```

✅ You now have `C:\phone-agent\WebDriverAgent.ipa`.

(If `Move-Item` says the `.app` wasn't found, open `wda_tmp` in File Explorer
and see where the `WebDriverAgentRunner-Runner.app` folder ended up. Adjust the path.)

## Step 7: Install WebDriverAgent on the iPhone with Sideloadly

1. Download and install **Sideloadly** from https://sideloadly.io. It needs the Apple Devices app from Step 2.
2. With the phone plugged in and unlocked, open Sideloadly and drag `WebDriverAgent.ipa` into it.
3. Enter your Apple ID and click **Start**. Sideloadly signs the app with your Apple ID so the phone accepts it.
   - With a free Apple ID, the app stops working after 7 days. Redo this step weekly. A $99/year Apple Developer account lasts a year.
   - If you'd rather not enter your main Apple ID, you can create a separate free Apple ID just for this.
4. On the iPhone:
   - **Settings → Privacy & Security → Developer Mode → On**, then restart the phone when asked. This option only appears after step 3.
   - **Settings → General → VPN & Device Management**, tap your Apple ID, then tap **Trust**.

✅ A "WebDriverAgentRunner" icon appears on your phone. Don't open it yourself; the PC starts it.

## Step 8: Find WebDriverAgent's exact name (bundle ID)

Sideloadly may rename the app slightly. With the venv active (`(.venv)`), run:

```powershell
python -m pymobiledevice3 apps list | findstr /i webdriver
```

Write down the result that ends in `.xctrunner`, for example
`com.facebook.WebDriverAgentRunner.xctrunner`. That's your **bundle ID**.

## Step 9: Connect to the phone

1. Close PowerShell. Open it again with **right-click → Run as administrator**. The secure tunnel to iOS 17+ needs admin rights.
2. Run:

```powershell
cd C:\phone-agent
.\.venv\Scripts\Activate.ps1
.\scripts\start_phone.ps1 -BundleId "PASTE-YOUR-BUNDLE-ID-HERE"
```

Three new windows open: the tunnel, WebDriverAgent, and the port forward.
**Leave them open** the whole time you use the agent. If a window asks you to pick a device, type its number.

## Step 10: Test the connection (no AI yet)

Open a **normal** PowerShell window:

```powershell
cd C:\phone-agent
.\.venv\Scripts\Activate.ps1
python test_connection.py --home
```

✅ It prints three green checks, saves `screenshot.png` (open it, it should match your phone), and your phone jumps to the home screen.

**This is the big milestone.** If it works, the hard part is done. If not, see Troubleshooting below and send me the error.

## Step 11: First agent run (safe mode)

Before running, set **Settings → Display & Brightness → Auto-Lock → Never**. A locked phone can't be controlled. Set it back afterward.

```powershell
python run.py --step "Open Uber Eats and search for Chipotle. Don't order anything."
```

`--step` asks you before **every** tap. Press Enter to allow each one, or type `n` to block it.

## Step 12: A real order

```powershell
python run.py --step "Order a chicken burrito bowl from the nearest Chipotle on Uber Eats"
```

When the agent reaches checkout, it:
1. Shows a **READY TO BUY** summary in PowerShell. Type `yes` only if it's correct.
2. Taps **Pay with Apple Pay**.
3. Asks you to **double-click the side button and look at your phone** for Face ID.

Without your Face ID, nothing gets paid. Once you trust it, leave out `--step`.

---

## Every time you use it afterward

1. Plug in and unlock the phone.
2. Run `.\scripts\start_phone.ps1 -BundleId "..."` as admin (Step 9).
3. Run `python run.py "your task"` in a normal window.

## Troubleshooting

| Problem | Try this |
|---|---|
| `python` is not recognized | Reinstall Python and check **Add to PATH** (Step 1). |
| Can't reach WebDriverAgent | Are the 3 windows from Step 9 still open? Is the phone unlocked? Look in the WebDriverAgent window for errors. |
| Tunnel window shows errors | Make sure that PowerShell was opened **as administrator**. Unplug and replug the phone. |
| `auto-mount` fails | Turn Developer Mode on (Step 7) and restart the phone. Run the script again. |
| WebDriverAgent window says the app isn't trusted or valid | Step 7: trust the profile in **VPN & Device Management**. If it's been 7 days, reinstall with Sideloadly. |
| Taps land in the wrong place | Send me `screenshot.png` and the screen size `test_connection.py` printed. |
| The agent gets stuck in an app | Press Ctrl+C to stop it. Try a more specific task, or use `--effort high`. |

If you're stuck, copy the exact error message and send it to me.
