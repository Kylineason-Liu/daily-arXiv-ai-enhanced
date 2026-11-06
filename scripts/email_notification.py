"""Send one Gmail notification per Hong Kong day after a complete publication."""
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
import html
import json
import os
from pathlib import Path
import smtplib
import ssl
import tempfile
from zoneinfo import ZoneInfo

CONFIG = Path.home() / '.config/arxiv-daily/mail.json'


def save_state(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.delivery-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def build_message(settings, manifest, sender, now):
    date = manifest['announcement_date']
    count = manifest['total_unique']
    website = settings['email']['website']
    message = EmailMessage()
    message['From'] = f'arXiv Daily <{sender}>'
    message['To'] = sender
    message['Subject'] = f'arXiv 日报已更新 — {date} · {count} 篇论文'
    message['Date'] = format_datetime(now)
    message['Message-ID'] = make_msgid(domain='gmail.com')
    categories = '\n'.join(
        f"• {category}：{sum(counts.values())} 篇" for category, counts in manifest['categories'].items()
    )
    body = (
        f"你的 arXiv 日报已生成并发布。\n\n"
        f"arXiv 公告日期：{date}\n去重后共 {count} 篇论文，均已生成中文摘要。\n\n"
        f"阅读日报：\n{website}\n\n{categories}\n\n"
        "各分类数量包含交叉分类，因此相加可能大于去重后的总数。\n"
        "收录新论文及交叉分类，不收修订版，不按兴趣过滤。\n"
        "摘要依据论文原始摘要生成；网页中点击 Details 可查看详情及原文链接。\n\n"
        f"通知时间：{now.strftime('%Y-%m-%d %H:%M')}（香港时间）。\n"
        "如 arXiv 尚无新公告，网页仍显示最近一期；可以用日历查看往期日报。\n"
    )
    message.set_content(body)
    message.add_alternative(
        '<html><body><h2>arXiv 日报已更新</h2>'
        f'<p>公告日期：{html.escape(date)}；去重后 <strong>{count}</strong> 篇。</p>'
        f'<p><a href="{html.escape(website, quote=True)}">打开日报网页</a></p>'
        f'<pre style="white-space:pre-wrap;font-family:inherit">{html.escape(body)}</pre>'
        '</body></html>', subtype='html')
    return message


def notify(settings, manifest, state_directory):
    # Called with daily.py's exclusive run lock, only after git push succeeds.
    if not settings.get('email', {}).get('enabled'):
        raise RuntimeError('Email notifications are not enabled')
    if manifest.get('sample'):
        raise ValueError('A sample is not a complete daily digest')
    now = datetime.now(ZoneInfo(settings['time_zone']))
    day = now.date().isoformat()
    path = state_directory / 'email-delivery.json'
    state = json.loads(path.read_text()) if path.exists() else {}
    previous = state.get(day, {})
    if previous.get('status') == 'sent':
        print(f'Email already sent for {day}; skipped.', flush=True)
        return
    if previous.get('status') == 'pending':
        raise RuntimeError(f'Email delivery for {day} is uncertain; check Gmail Sent before retrying. State: {path}')
    config = json.loads(CONFIG.read_text())
    sender = config['sender']
    message = build_message(settings, manifest, sender, now)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context(), timeout=45) as server:
        server.login(sender, config['app_password'])
        state[day] = {'status': 'pending', 'message_id': message['Message-ID'],
                      'announcement_date': manifest['announcement_date'], 'started_at': now.isoformat()}
        save_state(path, state)
        refused = server.send_message(message)
        if refused:
            raise RuntimeError('Gmail refused the recipient; delivery was not confirmed')
        state[day]['status'] = 'sent'
        state[day]['sent_at'] = datetime.now(ZoneInfo(settings['time_zone'])).isoformat()
        save_state(path, state)
    print(f'Gmail accepted the daily notification for {sender}.', flush=True)
