# Build a Discord Virtual-Credit Game in Azure

**RITSEC Azure Mentorship • Student lab • Four-person team • 110–120 minutes**

> **The goal:** deploy a working Discord slash-command bot using Azure Functions and Azure Table Storage, collaborate in GitHub, and collect clear evidence of what each teammate built. All credits are fictional. There is no real-money gambling, purchasing, withdrawals, payouts, or transferable value.

## What success looks like

At the end of the lab, your team should be able to:

- Run `/ping`, `/balance`, and `/coinflip` in a **private test Discord server**.
- Point to a **Python Azure Function**, a **Storage account / Table**, and a **resource group** in the Azure Portal.
- Run **six passing unit tests** and show at least **two individual GitHub contributions** (ideally one per student).
- Show a live demo and explain how a request moves from Discord to Azure and back.
- Keep secrets outside of GitHub and write a short README that another student could follow.

## How the architecture works

```text
Discord /coinflip command
       │ HTTPS request (signed by Discord)
       ▼
Azure Functions: /api/discord
       │ Verify signature + parse command
       ├──► game.py   (input validation + random coin flip)
       └──► Azure Table Storage: PlayerBalances (persist a user's credits)
       │
       ▼
Discord receives the result

GitHub → shared source code, pull requests, and documentation
```

**Why serverless?** Discord can send interactions directly to an HTTPS endpoint. This avoids the complexity and cost of a permanently running VM. Azure Functions may still have a cold start after inactivity; Discord expects a response within **3 seconds**, so see troubleshooting below.

## Before the lab (mentor/one student, 20–40 minutes outside the clock)

1. **Accounts:** one verified **Azure for Students** subscription with enough available credit and rights to create resources; a Discord account able to manage a private test server; a GitHub account for each teammate. One subscription per team is enough. Do not share Azure passwords.
2. **Software:** install VS Code, **Python 3.11**, **Python extension**, **Azure Functions extension**, and Git. The Azure Functions extension can install Core Tools if local debugging is needed; it is not necessary for the unit tests in this lab.
3. **Prep a GitHub repository:** create a private team repository and upload the contents of this `starter/` folder. Invite all four students as collaborators. Keep `local.settings.json`, `.env`, and bot tokens out of the repo.
4. **Verify Azure region access:** the instructor should check that Azure Functions **Flex Consumption** and Storage are available in a region permitted by the student subscription. Azure for Students access/quota differs by student and region. If a create wizard fails, stop and check your permitted regions/quotas rather than repeatedly retrying random locations.
5. **Reserve a project name:** choose a short, globally unique function app name like `rit-discord-sim-team7` (if available). Create only **one deployment for the team**.

## Roles (assign in the first five minutes)

| Student | Primary role | Evidence / contribution |
|---|---|---|
| A: Discord/API | App creation, installation, command registration | Screenshot of working commands; describe webhook and signature verification |
| B: Python backend | Run/edit game logic and tests | A feature or unit-test commit/PR; explain input validation and randomness |
| C: Azure/cloud | Function app, Table Storage, app settings, deploy | Architecture screenshot; explain storage and deployment |
| D: DevOps/QA | GitHub workflow, testing, README, demo | PR(s), test result, troubleshooting notes and README |

**Important:** all four teammates should take turns explaining a component. Each should push an individual commit, or pair on a PR and document their contribution clearly. Only one student needs to deploy.

## 110-minute run of show

| Time | Team milestone |
|---|---|
| 0–10 min | Read architecture; assign roles; clone/download starter; identify team goal |
| 10–25 min | Create and install Discord app in the private server |
| 25–40 min | Run tests; read the backend code; make one small team customization |
| 40–65 min | Create Azure Function App; locate storage; create credits table |
| 65–80 min | Add two app settings; deploy the Python project |
| 80–95 min | Add Discord interaction URL; register commands; test `/ping` and `/balance` |
| 95–105 min | Test `/coinflip`, demonstrate persistence, make/check GitHub contributions |
| 105–110 min | Demo, reflection, write resume-worthy takeaways; leave follow-up features for later |

Keep 10 minutes of buffer inside the 2-hour session for Azure or Discord setup issues.

## Part 1 — Set up your Discord application (Student A, 15 min)

1. Open <https://discord.com/developers/applications> and click **New Application**. Name it something recognizable, such as `RIT Cloud Casino Sim`.
2. Open **General Information**. Copy the **Application ID** and **Public Key** to a temporary private team note. The Public Key verifies that requests truly came from Discord.
3. Open **Bot**. Reset or reveal the **bot token** only when it is needed later for command registration. **Never** send it in Discord, paste it into GitHub, or capture it in a screenshot. (You do **not** need to enable Message Content Intent for slash commands.)
4. On **Installation**, enable **Guild Install** with `applications.commands` and `bot` scopes. Use the minimum permissions required (for this lab, `Send Messages` if shown). Save, copy the install link, and install the application in your **private test server**. You must have permission to manage that server.
5. In your Discord client, enable **User Settings → Advanced → Developer Mode**, then right-click the test server and choose **Copy Server ID**. This is also called its **Guild ID**.
6. Do not set the **Interactions Endpoint URL** yet. It will point to your deployed Azure Function in Part 4.

**Checkpoint:** Can you find the Application ID, Public Key, Guild ID, and your private test server? Do **not** put the bot token in the team notebook.

## Part 2 — Inspect, test, and customize Python code (Student B, 15 min)

1. Open the `starter` project folder in VS Code. Open `game.py` and locate `STARTING_BALANCE`, `MAX_BET`, and the `coinflip()` function.
2. In VS Code's terminal run:

   ```powershell
   python -m unittest discover -s tests -v
   ```

   Expected: **six tests pass**. These test the math and input validation without cloud resources.
3. Trace one example together: beginning balance `100`, bet `20`, choose `heads`. If the result is `heads`, the new balance is `120`; otherwise it is `80`.
4. **Choose one customization (required):** change the starting balance **and update the corresponding test**, or improve the wording of the coin-flip result, or add a **new unit test** for a zero-credit bet. Keep the original three commands working.
5. Commit your change on a branch like `feature/game-customization`; ask another teammate to review it. If you change `MAX_BET`, also update the matching `max_value` in `scripts/register_commands.py`.

**Checkpoint:** The tests pass after your change, and a reviewer can explain your code change in one sentence.

## Part 3 — Create the Azure infrastructure (Student C, 25 min)

1. In VS Code, open the **Azure** extension and sign in using the team deployment student's **Azure for Students** account.
2. With your starter project open, open the command palette (`F1`) and select **Azure Functions: Create Function App in Azure**. Choose your student subscription.
3. Enter a globally unique app name; select a region **supported by that subscription**. Choose **Python 3.11** (or a currently supported version that matches your local interpreter). For hosting, use **Flex Consumption** if offered; leave **Always Ready at 0** to avoid idle instance charges. If the wizard offers other options, use the lowest-resource settings compatible with the app and instructor's budget.
4. Let the extension create the Function App and its supporting Azure resources. In <https://portal.azure.com/>, navigate to the resource group associated with the new Function App. Record:
   - resource group name: `________________`
   - function app name: `________________`
   - region: `________________`
   - generated Storage account name: `________________`
5. Open the Storage account. In **Storage browser → Tables**, create a table named **`PlayerBalances`**. This table will store one row per Discord user. (Azure portal menu labels may change.)
6. Open the Storage account's **Access keys** page and copy a **connection string** privately. This is a credential; never paste it into a README, screenshot, repository, or shared chat. If Shared Key access is disabled by organization policy, ask the mentor; this starter would need a managed-identity alternative.

**Checkpoint:** Resource group + Function App + Storage account + `PlayerBalances` table all exist.

**Budget check:** a student credit is not an unlimited free plan. Check Cost Management/credits, use consumption pricing, and avoid Premium/Dedicated/Always Ready for this short lab without instructor approval.

## Part 4 — Configure and deploy the Python Function (Students C + D, 15 min)

1. In the Azure Portal, open the new **Function App** and locate **Settings → Environment variables** (or **Configuration → Application settings**).
2. Add these two **Application settings**, saving and applying changes:

   | Setting name | Value |
   |---|---|
   | `DISCORD_PUBLIC_KEY` | Public Key from Discord **General Information** |
   | `GAME_STORAGE_CONNECTION_STRING` | The Storage account connection string from Part 3 |

   Existing settings such as `AzureWebJobsStorage` and `FUNCTIONS_WORKER_RUNTIME` are managed by Azure; **do not delete them**.
3. Return to VS Code → Azure view; under **Workspace**, find the Functions project and choose **Deploy to Function App**, then select the Function App you created. Confirm the deployment. (You can also use command palette **Azure Functions: Deploy to Function App**.) Deployment replaces function code in the target app.
4. Once deployed, obtain the HTTP trigger URL from the Azure Portal function **`discord_interactions` → Get Function URL** or VS Code's deployed Functions list. It should have the form:

   ```text
   https://YOUR-FUNCTION-APP.azurewebsites.net/api/discord
   ```

   This endpoint intentionally uses **anonymous HTTP trigger access**, because Discord cannot send Azure function keys. Instead, `function_app.py` checks each request's **Ed25519 signature** using `DISCORD_PUBLIC_KEY`; unsigned requests receive `401`.
5. In Discord's Developer Portal, open **General Information → Interactions Endpoint URL**. Paste the entire `https://.../api/discord` URL and **Save Changes**. Discord should send a signed `PING`, which your Function responds to automatically.

**Checkpoint:** Discord accepts and saves the interactions endpoint URL. If not, go to troubleshooting and Azure Function logs.

## Part 5 — Register the commands and test the bot (Students A + D, 15 min)

Discord slash commands are **registered through Discord's API**, not merely defined in Python. The starter includes a safe helper that asks for the bot token **without displaying the input**.

1. In a terminal opened at the project root, run:

   ```powershell
   python scripts/register_commands.py
   ```

2. When prompted, paste your **Discord Application ID**, **Server (Guild) ID**, and **bot token** (the token input is hidden). The script uses Discord's bulk-overwrite **guild command** endpoint, so it updates just the test server's three commands.
3. In the test server, try these commands:

   ```text
   /ping
   /balance
   /coinflip amount:20 side:heads
   /balance
   ```

4. Ask **a second teammate** to run `/balance`. Each user should receive their own starting balance. After one person runs `/coinflip`, their credits should persist across separate commands because the data is stored in Azure Table Storage.
5. Return to the Azure Portal. Open **Storage browser → Tables → PlayerBalances** and show the new row(s), or view available telemetry/logs in the Function App. Screenshot only non-sensitive information.

**Checkpoint:** Demonstrate all three commands and the stored balance. If `/ping` works but `/balance` fails, focus on Storage account settings, connection string, and table existence.

## Part 6 — Personalize the project (10 minutes now; more after lab)

Pick **one** project decision and record it in a GitHub issue or README; implement it during the session only if the core bot is already working:

| Difficulty | Upgrade | Skills added |
|---|---|---|
| Easy | Make credits, win/loss text, emojis, and bot branding unique | UI wording and configuration |
| Easy | `/roll` (virtual dice wager) | Extra command, random values, automated tests |
| Medium | `/daily` (fixed virtual bonus once per UTC day) | Timestamps, validation, state |
| Medium | `/leaderboard` with top virtual balances | Azure Table queries and sorting |
| Medium | GitHub Actions to test every pull request | Continuous integration |
| Advanced | Detect duplicate interaction IDs, use ETags for balances | Idempotency, concurrency control |
| Advanced | Use Azure managed identity instead of a Storage connection string | RBAC and secrets management |

**Be aware:** the baseline uses simple table upserts. Concurrent commands may overwrite one another, and replayed requests are not deduplicated. It is a **teaching MVP, not a secure production economy**. Adding optimistic concurrency and idempotency is a strong next-sprint task.

## Final demonstration (5 minutes)

Each teammate gives a **30–45 second explanation**:

- **A / Discord:** how application commands reach a webhook; what the Public Key verifies.
- **B / Python:** how amount validation and outcome calculation prevent invalid wagers.
- **C / Azure:** why the app needs Functions and Table Storage, and what a resource group contains.
- **D / DevOps:** how branches, tests, commits, and reviews contributed to a deployable result.

### Evidence checklist

- [ ] Screenshot of a successful `/ping` in Discord
- [ ] Screenshot of `/coinflip` and changed `/balance` (hide server/user identifiers if public)
- [ ] Screenshot of Azure resource group and Function App (hide secrets)
- [ ] Screenshot/table evidence that a user balance persisted
- [ ] Unit tests passed
- [ ] GitHub repository with README, group contributions, and a feature backlog
- [ ] A sentence describing **each person's exact technical contribution**

### Resume bullet examples (choose only what you actually did)

**Cloud / backend:** “Developed and deployed a Python Discord simulation bot using Azure Functions and Azure Table Storage, implementing HTTP interaction handling and persistent user state.”

**DevOps / collaboration:** “Collaborated on a four-person cloud project using GitHub branches, peer reviews, and unit tests to deliver and document a serverless Discord application.”

**Security / APIs:** “Integrated Discord slash commands with a Python HTTP endpoint, validating Ed25519 request signatures and server-side wager inputs before processing actions.”

**Never** claim that you built a production-grade financial platform, secure ledger, CI/CD pipeline, or infrastructure as code unless the team actually implements those things.

## Troubleshooting decision tree

| Symptom | Check / fix |
|---|---|
| Function App cannot be created | Student subscription quotas, supported regions/plan, available credit, and permissions; try a confirmed permitted region or an instructor-approved alternative |
| Discord cannot save endpoint URL | Exact `/api/discord` URL; app deployed; `DISCORD_PUBLIC_KEY` exact; HTTPS; Discord signed `PING` handled; inspect Function logs |
| HTTP request returns `401` | Expected for unsigned curl/browser requests. Real Discord interactions must include valid signature headers; verify Public Key |
| `/ping` works, `/balance` errors | `GAME_STORAGE_CONNECTION_STRING`, Storage network access, table name exactly `PlayerBalances` |
| Slash commands are missing | App installed in correct test server; Application ID/Guild ID correct; rerun `register_commands.py`; bot token must be valid |
| “The application did not respond” intermittently | Discord requires initial response within 3 seconds; Azure consumption cold starts or slow Storage calls can exceed this. Retry after warming, check Application Insights; defer-response architecture is a later enhancement |
| `404` on Function URL | Inspect deployed function list/route; expected route `/api/discord`, HTTP POST only |
| Balance changes unexpectedly with rapid requests | MVP does not yet use ETag compare-and-swap or interaction-ID deduplication; see advanced upgrades |

## End-of-lab cleanup

Keep the project resources **only if** the group wants to continue and checks the credit usage. Otherwise delete the lab **resource group**, which removes its associated Function App and storage resources. **Deleting the Azure resource group does not delete the Discord app, GitHub repository, or secrets already copied elsewhere.** Reset the bot token if exposed and remove the app from the test server when done.

## Official references (instructor review)

- [Discord Interactions Overview](https://docs.discord.com/developers/interactions/overview)
- [Discord Application Commands](https://docs.discord.com/developers/interactions/application-commands)
- [Discord quickstart / Installing app](https://docs.discord.com/developers/quick-start/getting-started)
- [Azure Functions Python developer guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions VS Code deployment guide](https://learn.microsoft.com/azure/azure-functions/functions-develop-vs-code)
- [Azure Table Storage Python SDK](https://learn.microsoft.com/python/api/overview/azure/data-tables-readme)
- [Azure for Students](https://learn.microsoft.com/azure/education-hub/about-azure-for-students)

---

## Mentor facilitation notes (not required reading for students)

**Preflight is the biggest predictor of success.** If the team spends the live session installing Python or sorting out student subscription restrictions, they may not reach a demo. Have one working Azure subscription, private Discord server, and starter repo ready first. Ideally, verify a minimal Azure Function can deploy in an allowed region prior to the meeting.

**Don't overteach the code.** Ask, “Where is the request verified?”, “Where do we check a bet is affordable?”, and “What happens to data if the Function is restarted?” Have students point to relevant code, then make a small modification and test it.

**Allow partial success.** If Azure resource creation fails, demonstrate passing unit tests and GitHub PRs; use screenshots/architecture notes as a partial lab artifact. The group can deploy in a follow-up session when their subscription quota is resolved. Do not claim the cloud deployment worked without testing it.

**Security/cost defaults:** one private server, one Azure Function App, one Storage account; token copied only into the hidden registration prompt; Public Key and Storage connection string in Function App settings (do not log or commit them). Avoid always-ready instances unless you deliberately accept their cost. Configure a spending alert/credit check and clean up unused resources.
