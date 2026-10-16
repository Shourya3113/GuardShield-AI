"""
Opens the report in Microsoft Word, updates every field (table of contents, list of tables, list of figures,
page numbers), saves the .docx and exports a PDF next to it. Windows with Word installed.

  python scripts/final_report/finalize_with_word.py
"""

from pathlib import Path

import win32com.client

BASE = Path(__file__).resolve().parents[2]
DOCX = BASE / "docs" / "01 Reports" / "Final Project Report" / "GuardShield AI - Final Project Report.docx"
WD_FORMAT_PDF = 17


def main():
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(str(DOCX), ReadOnly=False, AddToRecentFiles=False)
        for _ in range(2):  # second pass: page numbers settle after the lists have been filled in
            doc.Fields.Update()
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents(i).Update()
            doc.Repaginate()
        pages = doc.ComputeStatistics(2)  # wdStatisticPages
        doc.Save()
        doc.ExportAsFixedFormat(str(DOCX.with_suffix(".pdf")), WD_FORMAT_PDF)
        doc.Close(False)
        print(f"updated fields, {pages} pages; wrote {DOCX.with_suffix('.pdf').name}")
    finally:
        word.Quit()


if __name__ == "__main__":
    main()
