"""Synthetic local regressions. No credentials, remote model, API, or GPU."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import torch
from legislm.training.checkpoint import load_checkpoint
from legislm.training.persistence import LocalPersistenceBackend


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AuditRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.data = {'scientific_config_hash':'science', 'value':torch.tensor([17])}
        torch.save(self.data, self.source / 'checkpoint.pt')
        self.manifest = {k:'fixture' for k in ['run_id','checkpoint_id','segment_id','config_file_sha256','execution_config_hash']}
        self.manifest.update(schema_version=1,global_step=1,tokens_seen=1,tokens_for_successful_updates=1,
                             budget_counter='successful_update_tokens',scientific_config_hash='science',files=[self.entry('checkpoint.pt')])
        self.write_manifest()

    def entry(self, name):
        path = self.source / name
        return {'path':name,'size_bytes':path.stat().st_size,'sha256':digest(path)}

    def write_manifest(self):
        (self.source / 'manifest.json').write_text(json.dumps(self.manifest))

    def test_checkpoint_payload_must_be_in_hashed_manifest(self):
        (self.source / 'decoy.bin').write_bytes(b'fixture-only-decoy')
        self.manifest['files'] = [self.entry('decoy.bin')]
        self.write_manifest()
        with self.assertRaises(ValueError):
            load_checkpoint(self.source)

    def test_checkpoint_path_traversal_rejected_before_write(self):
        self.manifest['checkpoint_id'] = '../../escaped'
        self.write_manifest()
        with self.assertRaises(ValueError):
            LocalPersistenceBackend().publish_checkpoint(self.source, self.root / 'persistent')
        self.assertFalse((self.root / 'escaped').exists())

    def test_checkpoint_manifest_file_escape_rejected(self):
        outside = self.root / 'outside.bin'
        outside.write_bytes(b'outside-fixture')
        self.manifest['files'].append({'path':'../outside.bin','size_bytes':outside.stat().st_size,'sha256':digest(outside)})
        self.write_manifest()
        with self.assertRaises(ValueError):
            load_checkpoint(self.source)

    def test_checkpoint_size_mismatch_rejected_before_deserialization(self):
        self.manifest['files'][0]['size_bytes'] += 1
        self.write_manifest()
        with patch('torch.load', side_effect=AssertionError('must not deserialize invalid artifact')):
            with self.assertRaises(ValueError):
                load_checkpoint(self.source)

    def test_checkpoint_scientific_metadata_binds_loaded_payload(self):
        self.manifest['scientific_config_hash'] = 'altered-science'
        self.write_manifest()
        with self.assertRaises(ValueError):
            load_checkpoint(self.source, expected_scientific_hash='altered-science')

    def test_checkpoint_symlink_outside_rejected(self):
        outside = self.root / 'external.pt'
        (self.source / 'checkpoint.pt').rename(outside)
        (self.source / 'checkpoint.pt').symlink_to(outside)
        with self.assertRaises(ValueError):
            load_checkpoint(self.source)

    def test_local_publish_checks_declared_size(self):
        self.manifest['files'][0]['size_bytes'] += 1
        self.write_manifest()
        with self.assertRaises(ValueError):
            LocalPersistenceBackend().publish_checkpoint(self.source, self.root / 'persistent')

    def test_explicit_selector_cannot_escape_root(self):
        with self.assertRaises(ValueError):
            LocalPersistenceBackend().resolve_checkpoint(self.root / 'persistent', '../../source')

    def test_latest_escape_is_ignored_in_favor_of_valid_local_checkpoint(self):
        backend = LocalPersistenceBackend()
        run = self.root / 'persistent'
        backend.publish_checkpoint(self.source, run)
        (run / 'latest.json').write_text(json.dumps({'checkpoint_id':'../../source'}))
        self.assertEqual(backend.resolve_checkpoint(run).resolve(), (run / 'checkpoints/fixture').resolve())

    def test_valid_checkpoint_round_trip_remains_supported(self):
        data = load_checkpoint(self.source, expected_scientific_hash='science')
        self.assertEqual(data['value'].item(), 17)
        LocalPersistenceBackend().publish_checkpoint(self.source, self.root / 'persistent')
        self.assertTrue((self.root / 'persistent/checkpoints/fixture/COMPLETE.json').is_file())


if __name__ == '__main__':
    unittest.main(verbosity=2)
