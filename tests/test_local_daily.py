import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('daily', Path(__file__).resolve().parents[1] / 'scripts/daily.py')
daily = importlib.util.module_from_spec(spec)
spec.loader.exec_module(daily)
bridge_spec = importlib.util.spec_from_file_location('bridge', Path(__file__).resolve().parents[1] / 'scripts/chatgpt_bridge.py')
bridge = importlib.util.module_from_spec(bridge_spec)
bridge_spec.loader.exec_module(bridge)


def paper(identifier, subjects):
    return f'''<dt><a title="Abstract" href="/abs/{identifier}">paper</a></dt><dd>
      <div class="list-title">Title: A title</div><div class="list-authors"><a>A. Author</a></div>
      <div class="list-subjects">{subjects}</div><p class="mathjax">An abstract.</p></dd>'''


class CollectionTests(unittest.TestCase):
    def test_stream_requires_successful_completion(self):
        delta = SimpleNamespace(type='response.output_text.delta', delta='{"ok":true}')
        completed = SimpleNamespace(type='response.completed', response=SimpleNamespace(status='completed', error=None, output_text=''))
        self.assertEqual(bridge.completed_text(iter([delta, completed])), '{"ok":true}')
        with self.assertRaises(RuntimeError):
            bridge.completed_text(iter([delta]))
        with self.assertRaises(RuntimeError):
            bridge.completed_text(iter([delta, SimpleNamespace(type='response.failed')]))

    def test_cross_lists_are_kept_and_replacements_excluded(self):
        html = '<h3>Showing new listings for Friday, 6 November 2026</h3><div class="paging">Total of 3 entries</div><dl>'
        html += '<h3>New submissions (showing 1 of 1 entries)</h3>' + paper('2611.00001', 'Robotics (cs.RO)')
        html += '<h3>Cross submissions (showing 1 of 1 entries)</h3>' + paper('2611.00002', 'Computer Vision (cs.CV); Robotics (cs.RO)')
        html += '<h3>Replacement submissions (showing 1 of 1 entries)</h3>' + paper('2610.00003', 'Robotics (cs.RO)') + '</dl>'
        date, papers, expected, counts, total = daily.parse_listing(html, 'cs.RO')
        self.assertEqual(date, '2026-11-06')
        self.assertEqual([p['id'] for p in papers], ['2611.00001', '2611.00002'])
        self.assertEqual(papers[1]['categories'], ['cs.CV', 'cs.RO'])
        self.assertEqual(counts, {'New submissions': 1, 'Cross-lists': 1})
        self.assertEqual(total, 3)

    def test_error_page_is_not_published_as_empty_day(self):
        with self.assertRaises(ValueError):
            daily.parse_listing('<h1>Service unavailable</h1>', 'cs.RO')

    def test_missing_paper_fields_fail_collection(self):
        html = '<h3>Showing new listings for Friday, 6 November 2026</h3><div class="paging">Total of 1 entries</div><dl>'
        html += '<h3>New submissions (showing 1 of 1 entries)</h3>' + paper('2611.00001', 'Robotics (cs.RO)').replace('An abstract.', '') + '</dl>'
        with self.assertRaises(ValueError):
            daily.parse_listing(html, 'cs.RO')

    def test_model_cannot_drop_or_duplicate_papers(self):
        papers = [{'id': 'one'}, {'id': 'two'}]
        complete = lambda identifier: dict(id=identifier, **{k: '摘要' for k in daily.FIELDS})
        with self.assertRaises(ValueError):
            daily.validate_summaries({'papers': [complete('one')]}, papers)
        with self.assertRaises(ValueError):
            daily.validate_summaries({'papers': [complete('one'), complete('one')]}, papers)
        result = daily.validate_summaries({'papers': [complete('two'), complete('one')]}, papers)
        self.assertEqual(set(result), {'one', 'two'})


if __name__ == '__main__':
    unittest.main()
