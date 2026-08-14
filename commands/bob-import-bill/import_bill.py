#!/usr/bin/env python3
"""Rename a supported PDF invoice and append its minimal expense row."""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


HEADER = ["date", "vendor", "bill_number", "category", "amount_chf"]


class BillImportError(Exception):
    pass


@dataclass(frozen=True)
class Invoice:
    date: str
    vendor: str
    bill_number: str
    category: str
    amount_chf: str

    def row(self) -> dict[str, str]:
        return dict(zip(HEADER, (self.date, self.vendor, self.bill_number,
                                 self.category, self.amount_chf), strict=True))

    @property
    def filename(self) -> str:
        safe_bill_number = self.bill_number.replace("/", "-")
        return f"{self.date}_{self.vendor}_{safe_bill_number}.pdf"


def require_match(pattern: str, text: str, field: str, flags: int = 0) -> str:
    match = re.search(pattern, text, flags)
    if not match:
        raise BillImportError(f"missing or changed {field}")
    return match.group(1).strip()


def iso_date(value: str, source_format: str) -> str:
    try:
        return datetime.strptime(value, source_format).date().isoformat()
    except ValueError as exc:
        raise BillImportError(f"invalid invoice date: {value}") from exc


def chf_amount(value: str) -> str:
    normalized = value.replace("'", "").replace(" ", "").replace(",", ".")
    try:
        amount = Decimal(normalized)
        cents = amount.quantize(Decimal("0.01"))
    except InvalidOperation as exc:
        raise BillImportError(f"invalid CHF amount: {value}") from exc
    if amount <= 0:
        raise BillImportError("invoice amount must be positive")
    if cents != amount:
        raise BillImportError(f"CHF amount has fractions of a cent: {value}")
    return f"{cents:.2f}"


def parse_infomaniak(text: str) -> Invoice:
    bill_number = require_match(
        r"Infomaniak Network SA\s+(\d{6,})", text, "Infomaniak invoice number"
    )
    date = iso_date(
        require_match(r"\bDate\s*:\s*(\d{2}/\d{2}/\d{4})", text, "invoice date"),
        "%d/%m/%Y",
    )
    amount = chf_amount(require_match(
        r"Total CHF incl\. VAT\s*:\s*([\d'.,]+)", text, "gross CHF total"
    ))
    if re.search(r"\bDomain\s*:", text):
        category = "Domains and hosting"
    elif re.search(r"Email Service\s*:", text):
        category = "Email"
    else:
        raise BillImportError("unsupported Infomaniak product category")
    return Invoice(date, "infomaniak", bill_number, category, amount)


def parse_exoscale(text: str) -> Invoice:
    bill_number = require_match(
        r"Invoice ID:\s*(EXO\d+)", text, "Exoscale invoice number"
    )
    date = iso_date(
        require_match(r"Emitted:\s*(\d{4}-\d{2}-\d{2})", text, "invoice date"),
        "%Y-%m-%d",
    )
    amount = chf_amount(require_match(
        r"Total \(CHF\)\s+([\d'.,]+)", text, "gross CHF total"
    ))
    return Invoice(date, "exoscale", bill_number, "Cloud infrastructure", amount)


def parse_spusu(text: str) -> Invoice:
    bill_number = require_match(
        r"Belegnummer:\s*(SC-\d+/\d+)", text, "spusu invoice number"
    )
    date = iso_date(
        require_match(r"Winterthur,\s*(\d{2}\.\d{2}\.\d{4})", text, "invoice date"),
        "%d.%m.%Y",
    )
    amount = chf_amount(require_match(
        r"Gesamtbetrag inkl\. MWST\s*CHF\s*([\d'.,]+)", text, "gross CHF total"
    ))
    return Invoice(date, "spusu", bill_number, "Telecom", amount)


def parse_invoice(text: str) -> Invoice:
    if "Infomaniak Network SA" in text:
        return parse_infomaniak(text)
    if "Akenes SA - Exoscale" in text:
        return parse_exoscale(text)
    if "spusu AG" in text:
        return parse_spusu(text)
    raise BillImportError("unsupported invoice vendor")


def extract_text(pdf: Path) -> str:
    if shutil.which("pdftotext") is None:
        raise BillImportError("pdftotext is not installed")
    try:
        extraction = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BillImportError("PDF text extraction failed") from exc
    if len(extraction.stdout.strip()) < 50:
        raise BillImportError("PDF has no usable text; OCR may be required")
    return extraction.stdout


def find_register(pdf: Path) -> Path:
    for directory in (pdf.parent, *pdf.parent.parents):
        candidate = directory / "expenses_register.csv"
        if candidate.is_file():
            return candidate
    raise BillImportError("no ancestor expenses_register.csv found")


def read_register(register: Path) -> list[dict[str, str]]:
    try:
        with register.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != HEADER:
                actual = ",".join(reader.fieldnames or [])
                raise BillImportError(
                    f"unexpected register header: {actual or 'empty register'}"
                )
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise BillImportError(f"cannot read expense register: {exc}") from exc
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise BillImportError("malformed register row")
    return rows


def write_temp_register(register: Path, rows: list[dict[str, str]]) -> Path:
    try:
        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{register.name}.", dir=register.parent, text=True
        )
    except OSError as exc:
        raise BillImportError(f"cannot prepare expense register: {exc}") from exc
    temp = Path(raw_path)
    try:
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temp.chmod(register.stat().st_mode)
        return temp
    except (OSError, csv.Error) as exc:
        temp.unlink(missing_ok=True)
        raise BillImportError(f"cannot prepare expense register: {exc}") from exc


def rename_no_replace(source: Path, target: Path) -> bool:
    if source == target:
        return False
    try:
        os.link(source, target)
    except FileExistsError as exc:
        raise BillImportError(f"destination already exists: {target.name}") from exc
    except OSError as exc:
        raise BillImportError(f"cannot create canonical invoice name: {exc}") from exc
    try:
        source.unlink()
    except OSError as exc:
        target.unlink(missing_ok=True)
        raise BillImportError(f"cannot remove original invoice name: {exc}") from exc
    return True


def restore_name(source: Path, target: Path) -> str | None:
    try:
        source_exists = source.exists()
        target_exists = target.exists()
        if source_exists and not target_exists:
            return None
        if target_exists and not source_exists:
            os.link(target, source)
            target.unlink()
            if source.exists() and not target.exists():
                return None
            return "invoice paths did not return to their original state"
        return (
            "both invoice paths exist" if source_exists
            else "both invoice paths are missing"
        )
    except OSError as exc:
        return f"invoice name: {exc}"


def restore_register(register: Path, original: bytes) -> str | None:
    restore: Path | None = None
    try:
        if register.read_bytes() == original:
            return None
        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{register.name}.restore.", dir=register.parent
        )
        restore = Path(raw_path)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(original)
        restore.chmod(register.stat().st_mode)
        os.replace(restore, register)
    except OSError as exc:
        if restore is not None:
            restore.unlink(missing_ok=True)
        return f"expense register: {exc}"
    return None


def commit_import(
    pdf: Path,
    target: Path,
    register: Path,
    rows: list[dict[str, str]],
    expected: dict[str, str],
) -> None:
    try:
        original = register.read_bytes()
    except OSError as exc:
        raise BillImportError(f"cannot read expense register: {exc}") from exc
    new_rows = [*rows, expected]
    temp = write_temp_register(register, new_rows)
    renamed = False
    try:
        renamed = rename_no_replace(pdf, target)
        os.replace(temp, register)
        if read_register(register) != new_rows or not target.is_file():
            raise BillImportError("post-write verification failed")
    except Exception as exc:
        temp.unlink(missing_ok=True)
        rollback_errors = [restore_register(register, original)]
        if renamed:
            rollback_errors.append(restore_name(pdf, target))
        incomplete = [error for error in rollback_errors if error]
        if incomplete:
            details = "; ".join(incomplete)
            raise BillImportError(
                f"import failed; rollback incomplete ({details}): {exc}"
            ) from exc
        raise BillImportError(f"import failed and was rolled back: {exc}") from exc


def handle_existing(
    pdf: Path,
    target: Path,
    invoice: Invoice,
    matches: list[dict[str, str]],
    dry_run: bool,
) -> str | None:
    if not matches:
        return None
    if len(matches) != 1 or matches[0] != invoice.row():
        raise BillImportError(
            f"invoice conflict for {invoice.vendor} {invoice.bill_number}"
        )
    if pdf == target:
        return "already"
    if target.exists():
        raise BillImportError(f"canonical invoice already exists: {target.name}")
    if dry_run:
        return "planned_rename"
    renamed = rename_no_replace(pdf, target)
    try:
        if not target.is_file() or pdf.exists():
            raise BillImportError("post-rename verification failed")
    except Exception as exc:
        rollback_error = restore_name(pdf, target) if renamed else None
        if rollback_error:
            raise BillImportError(
                f"rename verification failed; rollback incomplete ({rollback_error})"
            ) from exc
        raise BillImportError("rename verification failed and was rolled back") from exc
    return "renamed"


def import_bill(pdf: Path, dry_run: bool = False) -> tuple[str, Invoice, Path]:
    pdf = pdf.expanduser().resolve()
    if not pdf.is_file():
        raise BillImportError(f"invoice not found: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise BillImportError("invoice must be a PDF")

    register = find_register(pdf)
    invoice = parse_invoice(extract_text(pdf))
    expected = invoice.row()
    rows = read_register(register)
    matches = [
        row for row in rows
        if row["vendor"] == invoice.vendor
        and row["bill_number"] == invoice.bill_number
    ]
    target = pdf.with_name(invoice.filename)
    existing = handle_existing(pdf, target, invoice, matches, dry_run)
    if existing:
        return existing, invoice, register
    if target != pdf and target.exists():
        raise BillImportError(f"destination already exists: {target.name}")
    if dry_run:
        return "planned", invoice, register
    commit_import(pdf, target, register, rows, expected)
    return "imported", invoice, register


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("invoice", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        status, invoice, register = import_bill(args.invoice, args.dry_run)
    except BillImportError as exc:
        print(f"Blocked: {exc}", file=sys.stderr)
        return 2

    target = args.invoice.expanduser().resolve().with_name(invoice.filename)
    if status == "already":
        print(f"Already imported: {invoice.vendor} {invoice.bill_number}")
    elif status in {"planned", "planned_rename"}:
        print(f"Planned rename: {args.invoice} -> {target}")
        if status == "planned":
            print(
                "Planned row: "
                f"{invoice.date} | {invoice.vendor} | {invoice.bill_number} | "
                f"{invoice.category} | CHF {invoice.amount_chf}"
            )
    elif status == "renamed":
        print(f"Renamed existing bill: {target}")
    else:
        print(f"Renamed: {target}")
        print(
            "Imported: "
            f"{invoice.date} | {invoice.vendor} | {invoice.bill_number} | "
            f"{invoice.category} | CHF {invoice.amount_chf}"
        )
    print(f"Register: {register}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
