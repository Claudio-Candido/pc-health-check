#!/usr/bin/env python3
"""Capture UI screenshots for documentation.

Prerequisites:
  pip install playwright pymupdf
  playwright install chromium
  python run.py   # server on :5000
"""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"
OUT = Path(__file__).resolve().parents[1] / "docs" / "screenshots"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5,
            locale="pt-PT",
        )
        page = context.new_page()

        def shot(name: str, full: bool = True) -> None:
            path = OUT / f"{name}.png"
            page.screenshot(path=str(path), full_page=full)
            print("saved", path)

        page.goto(f"{BASE}/landing", wait_until="networkidle")
        shot("01-landing", full=True)

        page.goto(f"{BASE}/auth/register", wait_until="networkidle")
        shot("02-register", full=False)

        email = f"demo.screenshots.{int(time.time())}@example.com"
        page.fill("#technician_name", "Ana Ferreira")
        page.fill("#company_name", "ByteCare Informática")
        page.fill("#email", email)
        page.fill("#password", "demo1234")
        page.click("button[type=submit]")
        page.wait_for_url("**/")
        page.wait_for_load_state("networkidle")
        shot("03-dashboard-empty", full=False)

        page.goto(f"{BASE}/computers/new", wait_until="networkidle")
        shot("04-new-diagnosis", full=True)

        page.fill("#client_name", "Carlos Mendes")
        page.fill("#brand", "Lenovo")
        page.fill("#model", "ThinkPad T14")
        page.fill("#processor", "AMD Ryzen 7 PRO 5850U")
        page.fill("#ram", "32 GB DDR4")
        page.fill("#storage", "1 TB SSD NVMe")
        page.fill("#operating_system", "Windows 11 Pro")
        page.select_option("#diag_performance", "bom")
        page.select_option("#diag_storage", "excelente")
        page.select_option("#diag_operating_system", "bom")
        page.select_option("#diag_security", "regular")
        page.select_option("#diag_updates", "necessita_atencao")
        page.select_option("#diag_overall", "bom")
        page.check("input[value=diagnostico]")
        page.check("input[value=atualizacao]")
        page.check("input[value=limpeza]")
        page.fill("#svc_desc_diagnostico", "Análise completa de hardware e software")
        page.fill("#svc_desc_atualizacao", "Windows Update e drivers")
        page.fill("#svc_desc_limpeza", "Limpeza física e otimização")
        page.fill(
            "#recommendations",
            "Instalar atualizações pendentes e reforçar a proteção antivírus.\n"
            "Considerar upgrade de RAM se o uso multitasking aumentar.",
        )
        page.fill("#notes", "Cliente reportou lentidão ao abrir aplicações Office.")
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        time.sleep(0.4)
        shot("05-computer-detail", full=True)

        page.goto(f"{BASE}/computers/", wait_until="networkidle")
        shot("06-computers-list", full=False)

        href = page.locator("a.btn-sm").first.get_attribute("href")
        computer_id = href.rstrip("/").split("/")[-1]

        page.goto(f"{BASE}/reports/preview/{computer_id}", wait_until="networkidle")
        shot("07-report-preview", full=True)

        page.goto(f"{BASE}/computers/{computer_id}", wait_until="networkidle")
        with page.expect_download() as download_info:
            page.locator("form[action*='generate'] button").click()
        download_info.value.save_as(str(OUT / "sample-report.pdf"))
        print("saved", OUT / "sample-report.pdf")

        page.goto(f"{BASE}/reports/", wait_until="networkidle")
        shot("08-reports-list", full=False)

        page.goto(f"{BASE}/", wait_until="networkidle")
        shot("09-dashboard", full=False)

        page.goto(f"{BASE}/settings/", wait_until="networkidle")
        shot("10-settings", full=False)

        page.goto(f"{BASE}/settings/billing", wait_until="networkidle")
        shot("11-billing", full=False)

        page.locator("button.btn-primary").click()
        page.wait_for_load_state("networkidle")
        shot("12-billing-pro", full=False)

        page.goto(f"{BASE}/settings/", wait_until="networkidle")
        shot("13-settings-pro", full=False)

        page.goto(f"{BASE}/auth/logout", wait_until="networkidle")
        page.goto(f"{BASE}/auth/login", wait_until="networkidle")
        shot("14-login", full=False)

        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(f"{BASE}/landing", wait_until="networkidle")
        shot("15-landing-mobile", full=True)

        browser.close()

    try:
        import pymupdf

        doc = pymupdf.open(OUT / "sample-report.pdf")
        pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(2, 2))
        pix.save(str(OUT / "16-pdf-report.png"))
        print("saved", OUT / "16-pdf-report.png")
    except Exception as exc:  # noqa: BLE001
        print("PDF preview skipped:", exc)

    print("DONE")


if __name__ == "__main__":
    main()
