import csv
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import import_bill


INFOMANIAK_TEXT = """
Invoice
Infomaniak Network SA 7725953
Date : 01/05/2026
Domain : maindi.ch
Total CHF incl. VAT : 17.35
"""

EXOSCALE_TEXT = """
Akenes SA - Exoscale
Invoice ID: EXO3147774
Emitted: 2026-08-13
Credit
Total (CHF) 5.41
"""

SPUSU_TEXT = """
spusu AG
Rechnung                                                Winterthur, 03.08.2026
Kundennummer:            8089747
Belegnummer:             SC-480336/2026
Gesamtbetrag inkl. MWST                                 CHF 1.62
Ihr spusu Service-Team
"""


class ParserTests(unittest.TestCase):
    def test_infomaniak(self) -> None:
        invoice = import_bill.parse_invoice(INFOMANIAK_TEXT)
        self.assertEqual(
            invoice,
            import_bill.Invoice(
                "2026-05-01", "infomaniak", "7725953",
                "Domains and hosting", "17.35"
            ),
        )

    def test_exoscale(self) -> None:
        invoice = import_bill.parse_invoice(EXOSCALE_TEXT)
        self.assertEqual(invoice.filename, "2026-08-13_exoscale_EXO3147774.pdf")
        self.assertEqual(invoice.amount_chf, "5.41")

    def test_missing_chf_total_blocks(self) -> None:
        with self.assertRaisesRegex(import_bill.BillImportError, "gross CHF total"):
            import_bill.parse_invoice(EXOSCALE_TEXT.replace("Total (CHF)", "Total (EUR)"))

    def test_fractional_cent_blocks(self) -> None:
        with self.assertRaisesRegex(import_bill.BillImportError, "fractions of a cent"):
            import_bill.parse_invoice(EXOSCALE_TEXT.replace("5.41", "5.411"))

    def test_spusu(self) -> None:
        invoice = import_bill.parse_invoice(SPUSU_TEXT)
        self.assertEqual(
            invoice,
            import_bill.Invoice(
                "2026-08-03", "spusu", "SC-480336/2026", "Telecom", "1.62"
            ),
        )
        self.assertEqual(invoice.filename, "2026-08-03_spusu_SC-480336-2026.pdf")

    def test_unknown_vendor_blocks(self) -> None:
        with self.assertRaisesRegex(import_bill.BillImportError, "unsupported invoice vendor"):
            import_bill.parse_invoice("Example Vendor " * 10)


class ExtractionTests(unittest.TestCase):
    @patch("import_bill.shutil.which", return_value=None)
    def test_missing_pdftotext_blocks(self, _which: object) -> None:
        with self.assertRaisesRegex(import_bill.BillImportError, "not installed"):
            import_bill.extract_text(Path("invoice.pdf"))

    @patch("import_bill.shutil.which", return_value="/usr/bin/pdftotext")
    @patch("import_bill.subprocess.run")
    def test_extraction_failure_blocks(self, run: object, _which: object) -> None:
        run.side_effect = subprocess.CalledProcessError(1, "pdftotext")
        with self.assertRaisesRegex(import_bill.BillImportError, "extraction failed"):
            import_bill.extract_text(Path("invoice.pdf"))


class ImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.finance = Path(self.temp.name)
        self.vendor = self.finance / "bills_contracts" / "exoscale"
        self.vendor.mkdir(parents=True)
        self.register = self.finance / "expenses_register.csv"
        self.register.write_text(
            "date,vendor,bill_number,category,amount_chf\n", encoding="utf-8"
        )
        self.pdf = self.vendor / "3147774.pdf"
        self.pdf.write_bytes(b"%PDF synthetic")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def rows(self) -> list[dict[str, str]]:
        with self.register.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_restore_name_rejects_missing_paths(self) -> None:
        target = self.vendor / "canonical.pdf"
        self.pdf.unlink()
        self.assertEqual(
            import_bill.restore_name(self.pdf, target),
            "both invoice paths are missing",
        )

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_import_renames_and_appends(self, _extract: object) -> None:
        status, invoice, _register = import_bill.import_bill(self.pdf)
        self.assertEqual(status, "imported")
        self.assertFalse(self.pdf.exists())
        self.assertTrue((self.vendor / invoice.filename).is_file())
        self.assertEqual(self.rows(), [{
            "date": "2026-08-13",
            "vendor": "exoscale",
            "bill_number": "EXO3147774",
            "category": "Cloud infrastructure",
            "amount_chf": "5.41",
        }])

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_dry_run_does_not_write(self, _extract: object) -> None:
        status, _invoice, _register = import_bill.import_bill(self.pdf, dry_run=True)
        self.assertEqual(status, "planned")
        self.assertTrue(self.pdf.is_file())
        self.assertEqual(self.rows(), [])

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_existing_row_finishes_noncanonical_rename(self, _extract: object) -> None:
        invoice = import_bill.parse_invoice(EXOSCALE_TEXT)
        with self.register.open("a", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=import_bill.HEADER).writerow(invoice.row())
        status, _invoice, _register = import_bill.import_bill(self.pdf)
        self.assertEqual(status, "renamed")
        self.assertFalse(self.pdf.exists())
        self.assertTrue((self.vendor / invoice.filename).is_file())

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_canonical_invoice_is_idempotent(self, _extract: object) -> None:
        status, invoice, _register = import_bill.import_bill(self.pdf)
        self.assertEqual(status, "imported")
        canonical = self.vendor / invoice.filename
        status, _invoice, _register = import_bill.import_bill(canonical)
        self.assertEqual(status, "already")
        self.assertEqual(self.rows(), [invoice.row()])

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_conflicting_invoice_blocks(self, _extract: object) -> None:
        row = import_bill.parse_invoice(EXOSCALE_TEXT).row()
        row["amount_chf"] = "9.99"
        with self.register.open("a", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=import_bill.HEADER).writerow(row)
        with self.assertRaisesRegex(import_bill.BillImportError, "invoice conflict"):
            import_bill.import_bill(self.pdf)
        self.assertTrue(self.pdf.is_file())

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_wrong_register_header_blocks_without_changes(self, _extract: object) -> None:
        original = b"date,vendor,amount_chf\n"
        self.register.write_bytes(original)
        with self.assertRaisesRegex(import_bill.BillImportError, "unexpected register header"):
            import_bill.import_bill(self.pdf)
        self.assertEqual(self.register.read_bytes(), original)
        self.assertTrue(self.pdf.is_file())

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    def test_destination_collision_blocks_without_changes(self, _extract: object) -> None:
        target = self.vendor / "2026-08-13_exoscale_EXO3147774.pdf"
        target.write_bytes(b"different bill")
        original = self.register.read_bytes()
        with self.assertRaisesRegex(import_bill.BillImportError, "destination already exists"):
            import_bill.import_bill(self.pdf)
        self.assertEqual(self.register.read_bytes(), original)
        self.assertTrue(self.pdf.is_file())

    @patch("import_bill.import_bill")
    def test_cli_blocked_output(self, run_import: object) -> None:
        run_import.side_effect = import_bill.BillImportError("bad invoice")
        stderr = io.StringIO()
        with patch("sys.argv", ["import_bill.py", str(self.pdf)]), redirect_stderr(stderr):
            self.assertEqual(import_bill.main(), 2)
        self.assertEqual(stderr.getvalue(), "Blocked: bad invoice\n")

    @patch("import_bill.import_bill")
    def test_cli_success_output(self, run_import: object) -> None:
        invoice = import_bill.parse_invoice(EXOSCALE_TEXT)
        run_import.return_value = ("imported", invoice, self.register)
        stdout = io.StringIO()
        with patch("sys.argv", ["import_bill.py", str(self.pdf)]), redirect_stdout(stdout):
            self.assertEqual(import_bill.main(), 0)
        self.assertIn("Imported: 2026-08-13 | exoscale | EXO3147774", stdout.getvalue())

    @patch("import_bill.extract_text", return_value=EXOSCALE_TEXT)
    @patch("import_bill.os.replace", side_effect=OSError("simulated failure"))
    def test_register_failure_rolls_back_rename(
        self, _replace: object, _extract: object
    ) -> None:
        with self.assertRaisesRegex(import_bill.BillImportError, "rolled back"):
            import_bill.import_bill(self.pdf)
        self.assertTrue(self.pdf.is_file())
        self.assertFalse((self.vendor / "2026-08-13_exoscale_EXO3147774.pdf").exists())
        self.assertEqual(self.rows(), [])


if __name__ == "__main__":
    unittest.main()
