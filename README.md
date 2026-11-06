# 🚀 daily-arXiv-ai-enhanced

## Personal installation: local ChatGPT subscription + GitHub Pages

This fork generates Chinese summaries on the owner's Mac at **09:00 Asia/Hong_Kong** and publishes paper data to the `data` branch, then emails the owner a link to the completed digest. The website is hosted at https://kylineason-liu.github.io/daily-arXiv-ai-enhanced/.

- Settings: `personal-settings.json`.
- Categories: `cs.RO`, `cs.AI`, `cs.LG`, `eess.SY`, `cs.CV`.
- Model: `gpt-6.1-sol`, using the standalone local ChatGPT authorization module; Horizon is no longer required.
- Includes new submissions and cross-lists, excludes replacements, and deduplicates papers across categories. Each category's fetched count is checked against its official announcement list.
- Summaries use abstracts, retain every collected paper, and do not call the upstream external content-filter service.
- ChatGPT credentials stay in `~/.config/arxiv-daily/chatgpt/`; the Gmail sender and app password stay in `~/.config/arxiv-daily/mail.json` (owner-only permissions, outside the Git repository). This workflow has no paid-API fallback and uploads only public paper data and summaries.
- Completed summaries are cached in `~/.local/share/arxiv-daily/` for interrupted-run recovery. The website is updated only after the complete collection has summaries.

Run these commands from the repository root:

```bash
# Verify the ChatGPT subscription connection.
.venv/bin/python scripts/daily.py check

# Generate a complete daily digest, publish it, and email its link.
.venv/bin/python scripts/daily.py run --publish --email

# Install the macOS daily schedule without triggering an immediate run.
.venv/bin/python scripts/install_macos_schedule.py
```

The Mac must be logged in, awake, and online for an on-time run. A missed sleep-time trigger may run after wake; a powered-off Mac cannot generate the report. Closing Terminal or Codex is fine. The site groups data by **arXiv announcement date**, which can differ from the Hong Kong run date. On days with no new announcement, cached summaries prevent repeated AI processing.

Logs: `~/.local/share/arxiv-daily/logs/scheduler.stdout.log` and `scheduler.stderr.log`. Outputs and completeness manifests: `~/.local/share/arxiv-daily/output/`. If subscription authorization expires or is revoked, reconnect using `.venv/bin/python scripts/chatgpt_account.py login`. The migrated authorization keeps its existing account registration, so ChatGPT settings may still show its original Horizon name; revoking that registration also revokes this installation's access. The original GitHub API workflow below is retained for manual use only.


Email is sent only after successful publication, at most once per Hong Kong calendar day. It includes the announcement date, deduplicated paper count, category counts, and website link. Days without a new arXiv announcement link to the latest available issue. Delivery state is stored in `~/.local/share/arxiv-daily/email-delivery.json`. An uncertain SMTP delivery remains `pending` to avoid duplicate mail; check Gmail Sent before manually clearing that record. Failed collection, summary generation, or publication never sends a success notification.

To retry publication and notification for an already completed issue without generating summaries again:

```bash
.venv/bin/python scripts/daily.py publish --date YYYY-MM-DD --email
```

The authentication module was adapted from the local Horizon installation; its MIT license is retained in `scripts/HORIZON-LICENSE.txt`.

---

> [!CAUTION]
> 若您所在法域对学术数据有审查要求，谨慎运行本代码；任何二次分发版本必须履行合规审查（包括但不限于原始论文合规性、AI合规性）义务，否则一切法律后果由下游自行承担。

> [!CAUTION]
> If your jurisdiction has censorship requirements for academic data, run this code with caution; any secondary distribution version must remove the entrance accessible to China and fulfill the content review obligations, otherwise all legal consequences will be borne by the downstream.


This innovative tool transforms how you stay updated with arXiv papers by combining automated crawling with AI-powered summarization.


## ✨ Key Features

🎯 **Zero Infrastructure Required**
- Leverages GitHub Actions and Pages - no server needed
- Completely free to deploy and use

🤖 **Smart AI Summarization**
- Daily paper crawling with DeepSeek-powered summaries
- Cost-effective: Only ~0.2 CNY per day

💫 **Smart Reading Experience**
- Personalized paper highlighting based on your interests
- Cross-device compatibility (desktop & mobile)
- Local preference storage for privacy
- Flexible date range filtering

🧩 **SKILL System**
- Plug-and-play skill modules for customizing paper filtering

⚙️ **Easy Preference Export & Integration**
- One-click copy in Settings to export your keywords and authors configuration
- Seamlessly combine exported preferences with SKILL for reproducible and shareable setups

👉 **[Try it now!](https://dw-dengwei.github.io/daily-arXiv-ai-enhanced/)** - No installation required



https://github.com/user-attachments/assets/b25712a4-fb8d-484f-863d-e8da6922f9d7




# How to use
This repo will daily crawl arXiv papers about **cs.CV, cs.GR, cs.CL, cs.AI, cs.CE, cs.GT, cs.IT, cs.LG**, and use **DeepSeek** to summarize the papers in **Chinese**.
If you wish to crawl other arXiv categories, use other LLMs, or other languages, please follow the instructions.
Otherwise, you can watch the video above first and directly use this repo in https://dw-dengwei.github.io/daily-arXiv-ai-enhanced/. Please star it if you like :)

<details>
   <summary> If you want to customize categories, LLMs, or languages, click here.  </summary>

## Instructions
1. Fork this repo to your own account and delete my own information in [buy-me-a-coffee](./buy-me-a-coffee/README.md).
2. Go to: your-own-repo -> Settings -> Secrets and variables -> Actions
3. Go to Secrets. Secrets are encrypted and used for sensitive data
4. Create two repository secrets named `OPENAI_API_KEY` and `OPENAI_BASE_URL`, and input corresponding values.
5. [Optional] Set a password in `secrets.ACCESS_PASSWORD` if you do not wish others to access your page. (see https://github.com/dw-dengwei/daily-arXiv-ai-enhanced/pull/64)
6. Go to Variables. Variables are shown as plain text and are used for non-sensitive data
7. Create the following repository variables:
   1. `CATEGORIES`: separate the categories with ",", such as "cs.CL, cs.CV"
   2. `LANGUAGE`: such as "Chinese" or "English"
   3. `MODEL_NAME`: such as "deepseek-chat"
   4. `EMAIL`: your email for push to GitHub
   5. `NAME`: your name for push to GitHub
8. Go to your-own-repo -> Actions -> arXiv-daily-ai-enhanced
9. You can manually click **Run workflow** to test if it works well (it may take about one hour). By default, this action will automatically run every day. You can modify it in `.github/workflows/run.yml`
10. Set up GitHub pages: Go to your own repo -> Settings -> Pages. In `Build and deployment`, set `Source="Deploy from a branch"`, `Branch="main", "/(root)"`. Wait for a few minutes, go to https://\<username\>.github.io/daily-arXiv-ai-enhanced/. Please see this [issue](https://github.com/dw-dengwei/daily-arXiv-ai-enhanced/issues/14) for more precise instructions.
</details>

# Contributors
Thanks to the following special contributors for contributing code, discovering bugs, and sharing useful ideas for this project!!!
If you find that I missed your contribution below, please feel free to contact me through email.
<table>
  <tbody>
    <tr>
      <td align="center" valign="top">
        <a href="https://github.com/JianGuanTHU"><img src="https://avatars.githubusercontent.com/u/44895708?v=4" width="100px;" alt="JianGuanTHU"/><br /><sub><b>JianGuanTHU</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/Chi-hong22"><img src="https://avatars.githubusercontent.com/u/75403952?v=4" width="100px;" alt="Chi-hong22"/><br /><sub><b>Chi-hong22</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/chaozg"><img src="https://avatars.githubusercontent.com/u/69794131?v=4" width="100px;" alt="chaozg"/><br /><sub><b>chaozg</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/quantum-ctrl"><img src="https://avatars.githubusercontent.com/u/16505311?v=4" width="100px;" alt="quantum-ctrl"/><br /><sub><b>quantum-ctrl</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/Zhao2z"><img src="https://avatars.githubusercontent.com/u/141019403?v=4" width="100px;" alt="Zhao2z"/><br /><sub><b>Zhao2z</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/eclipse0922"><img src="https://avatars.githubusercontent.com/u/6214316?v=4" width="100px;" alt="eclipse0922"/><br /><sub><b>eclipse0922</b></sub></a><br />
      </td>
    </tr>


  </tbody>
  <tbody>
   <tr>
      <td align="center" valign="top">
        <a href="https://github.com/xuemian168"><img src="https://avatars.githubusercontent.com/u/38741078?v=4" width="100px;" alt="xuemian168"/><br /><sub><b>xuemian168</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/Lrrrr549"><img src="https://avatars.githubusercontent.com/u/71866027?v=4" width="100px;" alt="Lrrrr549"/><br /><sub><b>Lrrrr549</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/AinzRimuru"><img src="https://avatars.githubusercontent.com/u/59441476?v=4" width="100px;" alt="AinzRimuru"/><br /><sub><b>AinzRimuru</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/fengxueguiren"><img src="https://avatars.githubusercontent.com/u/153522370?v=4" width="100px;" alt="fengxueguiren"/><br /><sub><b>fengxueguiren</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://github.com/zerocpp"><img src="https://avatars.githubusercontent.com/u/2630297?v=4" width="100px;" alt="fengxueguiren"/><br /><sub><b>zerocpp</b></sub></a><br />
      </td>
   </tr>
  </tbody>
</table>

# Acknowledgement
We sincerely thank the following individuals and organizations for their promotion and support!!!
<table>
  <tbody>
    <tr>
      <td align="center" valign="top">
        <a href="https://x.com/GitHub_Daily/status/1930610556731318781"><img src="https://pbs.twimg.com/profile_images/1660876795347111937/EIo6fIr4_400x400.jpg" width="100px;" alt="Github_Daily"/><br /><sub><b>Github_Daily</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://x.com/aigclink/status/1930897858963853746"><img src="https://pbs.twimg.com/profile_images/1729450995850027008/gllXr6bh_400x400.jpg" width="100px;" alt="AIGCLINK"/><br /><sub><b>AIGCLINK</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://www.ruanyifeng.com/blog/2025/06/weekly-issue-353.html"><img src="https://avatars.githubusercontent.com/u/905434" width="100px;" alt="阮一峰的网络日志"/><br /><sub><b>阮一峰的网络日志 <br> 科技爱好者周刊 <br> （第 353 期）</b></sub></a><br />
      </td>
      <td align="center" valign="top">
        <a href="https://hellogithub.com/periodical/volume/111"><img src="https://github.com/user-attachments/assets/eff6b6dd-0323-40c4-9db6-444a51bbc80a" width="100px;" alt="《HelloGitHub》第 111 期"/><br /><sub><b>《HelloGitHub》<br> 月刊第 111 期</b></sub></a><br />
      </td>
    </tr>
  </tbody>
</table>


# Star history

[![Stargazers over time](https://starchart.cc/dw-dengwei/daily-arXiv-ai-enhanced.svg?variant=adaptive)](https://starchart.cc/dw-dengwei/daily-arXiv-ai-enhanced)

# Buy me a coffee
[here](./buy-me-a-coffee/README.md)
