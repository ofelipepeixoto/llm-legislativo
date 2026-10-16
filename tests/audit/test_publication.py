import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile

REPO = Path(__file__).resolve().parents[2]


class PublicationRegressions(unittest.TestCase):
    def test_nonpdf_rejects_wrong_archive_digest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            archive_path = root / 'fixture.tar'
            raw = b'<html><body>Fictitious legislative text.</body></html>'
            with tarfile.open(archive_path, 'w') as archive:
                info = tarfile.TarInfo('fixture.html'); info.size=len(raw)
                archive.addfile(info, io.BytesIO(raw))
            index = root / 'index.csv'
            with index.open('w', newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=['tar','status','membro_tar','sha256','tamanho','url'])
                writer.writeheader();writer.writerow({'tar':archive_path.name,'status':'listado','membro_tar':'fixture.html','sha256':hashlib.sha256(raw).hexdigest(),'tamanho':len(raw),'url':'https://fixture.invalid'})
            result=subprocess.run([sys.executable,str(REPO/'scripts/publication/process_archive_nonpdf.py'),'--archive',str(archive_path),'--expected-archive-sha256','0'*64,'--index',str(index),'--output-dir',str(root/'output')],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0,'Archive digest was merely copied into provenance')
            self.assertFalse((root/'output/non_pdf_manifest.json').exists())
            valid=subprocess.run([sys.executable,str(REPO/'scripts/publication/process_archive_nonpdf.py'),'--archive',str(archive_path),'--expected-archive-sha256',hashlib.sha256(archive_path.read_bytes()).hexdigest(),'--index',str(index),'--output-dir',str(root/'output')],capture_output=True,text=True,timeout=10)
            self.assertEqual(valid.returncode,0,valid.stderr)
            published=json.loads((root/'output/non_pdf_manifest.json').read_text())
            self.assertEqual(published['archive_sha256'],hashlib.sha256(archive_path.read_bytes()).hexdigest())

    def test_colab_bundle_preserves_mit_license(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'bundle'
            result=subprocess.run([sys.executable,str(REPO/'scripts/publication/package_colab_bundle.py'),'--output-dir',str(output)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            archives=list(output.parent.glob('*.zip'))
            self.assertEqual(len(archives),1)
            with zipfile.ZipFile(archives[0]) as z:
                licenses=[n for n in z.namelist() if n.endswith('LICENSE')]
                self.assertTrue(licenses,'Executable source bundle omitted MIT notice')
                self.assertEqual(z.read(licenses[0]),(REPO/'LICENSE').read_bytes())

if __name__=='__main__':unittest.main(verbosity=2)
