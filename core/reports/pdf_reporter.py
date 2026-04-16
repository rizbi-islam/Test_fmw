"""
PDF Report Generator using ReportLab.
Produces a structured PDF test report with cover page,
summary table, and per-test step breakdown.
"""
import os
from datetime import datetime
from loguru import logger
from core.reports.base_reporter import BaseReporter


class PdfReporter(BaseReporter):

    def generate(self, suite_result) -> str:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable, PageBreak
        )
        from reportlab.lib.enums import TA_CENTER

        os.makedirs(self.output_dir, exist_ok=True)
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe     = suite_result.suite_name.replace(" ", "_").replace("/", "_")
        filepath = os.path.join(self.output_dir, f"report_{safe}_{ts}.pdf")

        doc    = SimpleDocTemplate(filepath, pagesize=A4,
                                    topMargin=15*mm, bottomMargin=15*mm,
                                    leftMargin=20*mm, rightMargin=20*mm)
        styles = getSampleStyleSheet()

        CLR_PASS = colors.HexColor("#e8f5e9")
        CLR_FAIL = colors.HexColor("#ffebee")
        CLR_SKIP = colors.HexColor("#fff8e1")
        CLR_HEAD = colors.HexColor("#1a1a2e")
        CLR_WHT  = colors.white

        title_s = ParagraphStyle("t", fontSize=22, fontName="Helvetica-Bold",
                                  textColor=CLR_HEAD, alignment=TA_CENTER, spaceAfter=6)
        sub_s   = ParagraphStyle("s", fontSize=10, fontName="Helvetica",
                                  textColor=colors.HexColor("#555555"),
                                  alignment=TA_CENTER, spaceAfter=4)
        sec_s   = ParagraphStyle("sec", fontSize=12, fontName="Helvetica-Bold",
                                  textColor=CLR_HEAD, spaceBefore=8, spaceAfter=4)
        body_s  = ParagraphStyle("b", fontSize=8, fontName="Helvetica",
                                  textColor=colors.HexColor("#333333"), spaceAfter=2)

        story = []

        # ── Cover ─────────────────────────────────────────────
        story.append(Spacer(1, 20*mm))
        story.append(Paragraph("KWAF — Test Execution Report", title_s))
        story.append(Paragraph(f"Suite: {suite_result.suite_name}", sub_s))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", sub_s))
        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="100%", thickness=1, color=CLR_HEAD))
        story.append(Spacer(1, 8*mm))

        # Summary metrics
        sum_data = [
            ["Total", "Passed", "Failed", "Skipped"],
            [str(suite_result.total), str(suite_result.passed),
             str(suite_result.failed), str(suite_result.skipped)],
        ]
        sum_tbl = Table(sum_data, colWidths=[40*mm]*4)
        sum_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), CLR_HEAD),
            ("TEXTCOLOR",  (0,0),(-1,0), CLR_WHT),
            ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0),(-1,0), 10),
            ("FONTSIZE",   (0,1),(-1,1), 18),
            ("FONTNAME",   (0,1),(-1,1), "Helvetica-Bold"),
            ("ALIGN",      (0,0),(-1,-1), "CENTER"),
            ("BACKGROUND", (1,1),(1,1), CLR_PASS),
            ("BACKGROUND", (2,1),(2,1), CLR_FAIL if suite_result.failed > 0 else CLR_PASS),
            ("BACKGROUND", (3,1),(3,1), CLR_SKIP),
            ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("TOPPADDING", (0,0),(-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ]))
        story.append(sum_tbl)
        story.append(Spacer(1, 8*mm))

        # Overview table
        story.append(Paragraph("Test Case Overview", sec_s))
        ov_data = [["ID", "Name", "Status", "Steps", "Time"]]
        for r in suite_result.results:
            ov_data.append([
                r.test_id,
                (r.test_name[:38] + "...") if len(r.test_name) > 38 else r.test_name,
                r.status,
                str(r.total_steps),
                f"{r.elapsed_seconds}s",
            ])
        ov_tbl = Table(ov_data, colWidths=[28*mm, 65*mm, 20*mm, 18*mm, 22*mm])
        ov_sty = [
            ("BACKGROUND", (0,0),(-1,0), CLR_HEAD),
            ("TEXTCOLOR",  (0,0),(-1,0), CLR_WHT),
            ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0),(-1,-1), 8),
            ("ALIGN",      (0,0),(-1,-1), "CENTER"),
            ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#cccccc")),
            ("TOPPADDING", (0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]
        for i, r in enumerate(suite_result.results, 1):
            bg = CLR_PASS if r.status=="PASS" else (CLR_FAIL if r.status=="FAIL" else CLR_SKIP)
            ov_sty.append(("BACKGROUND", (2,i),(2,i), bg))
        ov_tbl.setStyle(TableStyle(ov_sty))
        story.append(ov_tbl)

        # ── Per-test pages ────────────────────────────────────
        for result in suite_result.results:
            story.append(PageBreak())
            sc = colors.HexColor("#2e7d32") if result.status=="PASS" else colors.HexColor("#c62828")
            ts_s = ParagraphStyle("tc", fontSize=13, fontName="Helvetica-Bold",
                                   textColor=sc, spaceAfter=4)
            story.append(Paragraph(
                f"[{result.status}]  {result.test_id} — {result.test_name}", ts_s))
            story.append(Paragraph(
                f"Duration: {result.elapsed_seconds}s  |  Steps: {result.total_steps}  |  "
                f"Passed: {result.passed_steps}  |  Failed: {result.failed_steps}", body_s))
            if result.error_message:
                story.append(Paragraph(f"Error: {result.error_message}", body_s))
            story.append(Spacer(1, 4*mm))

            st_data = [["#", "Keyword", "Status", "Message", "ms"]]
            for s in result.step_results:
                d   = s.to_dict() if hasattr(s,"to_dict") else vars(s)
                msg = str(d.get("message",""))
                st_data.append([
                    str(d.get("step_no","")),
                    str(d.get("keyword","")),
                    str(d.get("status","")),
                    (msg[:75]+"...") if len(msg)>75 else msg,
                    str(round(float(d.get("elapsed_ms",0)),1)),
                ])
            st_tbl = Table(st_data, colWidths=[10*mm,28*mm,15*mm,92*mm,15*mm])
            st_sty = [
                ("BACKGROUND", (0,0),(-1,0), CLR_HEAD),
                ("TEXTCOLOR",  (0,0),(-1,0), CLR_WHT),
                ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0),(-1,-1), 7),
                ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#cccccc")),
                ("TOPPADDING", (0,0),(-1,-1), 3),
                ("BOTTOMPADDING",(0,0),(-1,-1), 3),
            ]
            for i, s in enumerate(result.step_results, 1):
                d   = s.to_dict() if hasattr(s,"to_dict") else vars(s)
                bg  = CLR_PASS if d.get("status")=="PASS" else (
                      CLR_FAIL if d.get("status")=="FAIL" else CLR_SKIP)
                st_sty.append(("BACKGROUND", (2,i),(2,i), bg))
            st_tbl.setStyle(TableStyle(st_sty))
            story.append(st_tbl)

        doc.build(story)
        logger.success(f"[PdfReporter] Report -> {filepath}")
        return filepath
