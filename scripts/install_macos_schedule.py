"""Install the confirmed 09:00 Hong Kong schedule without starting a job now."""
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'com.arxiv.daily-subscription'
settings = json.loads((ROOT / 'personal-settings.json').read_text())
if sys.platform != 'darwin':
    raise SystemExit('This installer is for macOS.')
if not str(Path('/etc/localtime').resolve()).endswith('/' + settings['time_zone']):
    raise SystemExit('Set the Mac system time zone to Asia/Hong_Kong before installing.')
logs = Path.home() / '.local/share/arxiv-daily/logs'
logs.mkdir(parents=True, exist_ok=True)
agent = {
    'Label': LABEL,
    'ProgramArguments': ['/usr/bin/caffeinate', '-i', str(ROOT / '.venv/bin/python'), str(ROOT / 'scripts/daily.py'), 'run', '--publish', '--email'],
    'WorkingDirectory': str(ROOT),
    'StartCalendarInterval': {'Hour': settings['hour'], 'Minute': settings['minute']},
    'RunAtLoad': False, 'KeepAlive': False,
    'EnvironmentVariables': {'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
                             'TZ': settings['time_zone'], 'PYTHONUNBUFFERED': '1', 'GIT_TERMINAL_PROMPT': '0'},
    'StandardOutPath': str(logs / 'scheduler.stdout.log'),
    'StandardErrorPath': str(logs / 'scheduler.stderr.log'),
}
path = Path.home() / 'Library/LaunchAgents' / f'{LABEL}.plist'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(plistlib.dumps(agent))
path.chmod(0o600)
domain = f'gui/{os.getuid()}'
if subprocess.run(['launchctl', 'print', f'{domain}/{LABEL}'], capture_output=True).returncode == 0:
    subprocess.run(['launchctl', 'bootout', f'{domain}/{LABEL}'], check=True)
subprocess.run(['launchctl', 'bootstrap', domain, str(path)], check=True)
subprocess.run(['launchctl', 'print', f'{domain}/{LABEL}'], check=True, stdout=subprocess.DEVNULL)
print(f'Installed {LABEL}: {settings["hour"]:02}:{settings["minute"]:02} {settings["time_zone"]}.')
print(f'Logs: {logs}')
