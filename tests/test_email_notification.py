import json
from pathlib import Path
import smtplib
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import email_notification as email
import daily


class EmailTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        config = self.root / 'mail.json'
        config.write_text(json.dumps({'sender': 'owner@gmail.com', 'app_password': 'test-only'}))
        self.settings = {'model': 'test', 'language': 'Chinese', 'time_zone': 'Asia/Hong_Kong', 'email': {
            'enabled': True, 'website': 'https://example.com/daily/'}}
        self.manifest = {'announcement_date': '2026-11-06', 'total_unique': 2,
                         'categories': {'cs.RO': {'New submissions': 2}}, 'sample': False}
        self.server = MagicMock()
        self.server.send_message.return_value = {}
        self.smtp = patch.object(email.smtplib, 'SMTP_SSL')
        self.smtp.start().return_value.__enter__.return_value = self.server
        self.addCleanup(self.smtp.stop)
        self.config = patch.object(email, 'CONFIG', config)
        self.config.start()
        self.addCleanup(self.config.stop)

    def test_one_email_per_day_with_link_and_date(self):
        email.notify(self.settings, self.manifest, self.root)
        email.notify(self.settings, self.manifest, self.root)
        self.server.send_message.assert_called_once()
        message = self.server.send_message.call_args.args[0]
        self.assertEqual(message['To'], 'owner@gmail.com')
        self.assertIn('2026-11-06', message['Subject'])
        self.assertIn('https://example.com/daily/', message.get_body(preferencelist=('plain',)).get_content())

    def test_previously_sent_issue_is_marked_as_no_new_announcement(self):
        (self.root / 'email-delivery.json').write_text(json.dumps({
            '2000-01-01': {'status': 'sent', 'announcement_date': '2026-11-06'}
        }))
        email.notify(self.settings, self.manifest, self.root)
        message = self.server.send_message.call_args.args[0]
        self.assertIn('今日无新公告', message['Subject'])
        self.assertIn('最近一期仍为 2026-11-06', message.get_body(preferencelist=('plain',)).get_content())

    def test_uncertain_delivery_is_not_automatically_repeated(self):
        self.server.send_message.side_effect = TimeoutError('Connection lost')
        with self.assertRaises(TimeoutError):
            email.notify(self.settings, self.manifest, self.root)
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            email.notify(self.settings, self.manifest, self.root)
        self.server.send_message.assert_called_once()

    def test_authentication_failure_is_retryable_without_sent_record(self):
        self.server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Invalid credential')
        with self.assertRaises(smtplib.SMTPAuthenticationError):
            email.notify(self.settings, self.manifest, self.root)
        self.assertFalse((self.root / 'email-delivery.json').exists())
        self.server.send_message.assert_not_called()

    def test_publish_failure_never_sends_success_email(self):
        snapshot = dict(self.manifest, papers=[])
        with patch.object(daily, 'STATE', self.root), patch.object(daily, 'collect', return_value=snapshot), \
             patch.object(daily, 'enhance'), patch.object(daily, 'publish', side_effect=RuntimeError('Push failed')), \
             patch.object(email, 'notify') as notify:
            with self.assertRaisesRegex(RuntimeError, 'Push failed'):
                daily.run(self.settings, should_publish=True, should_email=True)
            notify.assert_not_called()


if __name__ == '__main__':
    unittest.main()
