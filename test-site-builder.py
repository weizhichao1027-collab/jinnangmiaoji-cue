#!/usr/bin/env python3
"""Regressions for releases, newly added support answers and page semantics."""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('site_builder', SOURCE_ROOT / 'build-i18n.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuilderRegressionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.previous_root = builder.ROOT
        self.addCleanup(setattr, builder, 'ROOT', self.previous_root)
        builder.ROOT = Path(self.directory.name)
        shutil.copytree(SOURCE_ROOT / 'templates', builder.ROOT / 'templates')
        self.config = json.loads((SOURCE_ROOT / 'site-config.json').read_text())
        english = json.loads((SOURCE_ROOT / 'i18n/en.json').read_text())
        self.tables = {code: copy.deepcopy(english) for code in builder.LOCALES}

    def test_release_versions_flow_to_all_machine_fact_outputs(self):
        self.config['platforms']['mac']['version'] = '9.8.7'
        self.config['platforms']['iphone']['version'] = '7.6.5'
        outputs = builder.build_outputs(self.config, self.tables)
        for filename in ('llms.txt', 'llms-full.txt'):
            self.assertIn('Mac 9.8.7', outputs[filename])
            self.assertIn('iPhone 7.6.5', outputs[filename])
        facts = json.loads(outputs['app-facts.json'])
        self.assertEqual(facts['platforms']['mac']['version'], '9.8.7')
        self.assertEqual(facts['trialPolicies']['ios']['releasedVersion'], '7.6.5')
        graph = json.loads(builder.structured_data(self.config, self.tables['en'], 'home', 'en'))['@graph']
        apps = [node for node in graph if node['@type'] == 'SoftwareApplication']
        self.assertEqual({node['softwareVersion'] for node in apps}, {'9.8.7', '7.6.5'})

    def test_new_visible_support_answer_is_discovered_and_source_linked(self):
        path = builder.ROOT / 'templates/support.html'
        path.write_text(path.read_text().replace('</main>', '<article id="new-topic"><h2>{{support.q99}}</h2><p>{{support.a99}}</p></article></main>'))
        answer = 'A newly visible answer.\n\nA second paragraph with <escaped text>.'
        for table in self.tables.values():
            table.update({'support.q99': 'New supported topic?', 'support.a99': answer,
                          'support.q98': 'Unpublished question?', 'support.a98': 'Not on this page.'})
        outputs = builder.build_outputs(self.config, self.tables)
        graph = json.loads(builder.structured_data(self.config, self.tables['en'], 'support', 'en'))['@graph']
        questions = next(node for node in graph if node['@type'] == 'FAQPage')['mainEntity']
        self.assertIn('New supported topic?', [node['name'] for node in questions])
        self.assertNotIn('Unpublished question?', [node['name'] for node in questions])
        facts = json.loads(outputs['app-facts.json'])
        topic = next(topic for topic in facts['topics'] if topic['topic'] == 'New supported topic?')
        self.assertEqual(topic['text']['en'], answer)
        self.assertIn('A newly visible answer.<br><br>A second paragraph with &lt;escaped text&gt;.', outputs['en/support.html'])
        self.assertTrue(topic['sources']['en'].endswith('/en/support.html#new-topic'))
        self.assertIn('/en/support.html#new-topic', outputs['llms-full.txt'])
        self.assertEqual(set(topic['text']), set(builder.LOCALES))
        self.assertEqual(set(topic['sources']), set(builder.LOCALES))

    def test_current_ios_trial_keeps_seven_days_and_mac_keeps_twenty_uses(self):
        outputs = builder.build_outputs(self.config, self.tables)
        facts = json.loads(outputs['app-facts.json'])
        self.assertEqual(facts['trialPolicies']['mac'], {'model': 'usage', 'uses': 20})
        trial = facts['trialPolicies']['ios']
        self.assertEqual(trial['model'], 'optional-timed')
        self.assertEqual((trial['days'], trial['hours']), (7, 168))
        self.assertEqual(trial['status'], 'released')
        self.assertFalse(trial['autoCharge'])
        self.assertFalse(trial['restartsOnRestore'])
        self.assertNotIn('releasedTrialUses', trial)
        self.assertNotIn('newVersionStatus', trial)
        for filename in ('llms.txt', 'llms-full.txt'):
            self.assertIn('7-day', outputs[filename])
            self.assertIn('168 consecutive hours', outputs[filename])
            self.assertIn('20', outputs[filename])
            self.assertNotIn('being prepared for release', outputs[filename])
            self.assertNotIn('Say 20 trial uses', outputs[filename])

    def test_watch_and_review_privacy_topics_link_to_all_localized_policies(self):
        outputs = builder.build_outputs(self.config, self.tables)
        facts = json.loads(outputs['app-facts.json'])
        for heading, anchor in [('Selected AI text and source references', 'review-content'),
                                ('Watch recording transfers', 'watch-recordings')]:
            topic = next(topic for topic in facts['topics'] if topic['topic'] == heading)
            for code in builder.LOCALES:
                self.assertEqual(topic['sources'][code], builder.page_url(self.config, 'privacy', code) + '#' + anchor)

    def test_offers_are_on_product_page_and_breadcrumbs_on_child_pages(self):
        for page in builder.PAGES:
            graph = json.loads(builder.structured_data(self.config, self.tables['en'], page, 'en'))['@graph']
            apps = [node for node in graph if node['@type'] == 'SoftwareApplication']
            crumbs = [node for node in graph if node['@type'] == 'BreadcrumbList']
            self.assertEqual(len(apps), 2 if page == 'home' else 0)
            self.assertEqual(len(crumbs), 0 if page == 'home' else 1)
            if page not in ('home', 'support'):
                self.assertFalse(any(node['@type'] == 'FAQPage' for node in graph))


if __name__ == '__main__':
    unittest.main()
