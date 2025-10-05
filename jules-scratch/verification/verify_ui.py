import re
from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the application
            page.goto("http://0.0.0.0:8000")
            expect(page.locator("#status")).to_have_text("Ready. Please upload an STL file.")

            # 2. Upload STL file
            file_path = "STLfiles/assets/ayalower.stl"
            with page.expect_file_chooser() as fc_info:
                page.get_by_role("button", name="Upload STL").click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)
            expect(page.locator("#status")).to_have_text("File uploaded and wire generator initialized.", timeout=15000)

            # 3. Generate Wire
            page.get_by_role("button", name="Generate Wire").click()
            expect(page.locator("#status")).to_have_text("Wire generated successfully.", timeout=60000)
            page.wait_for_timeout(1000) # Wait for render

            # 4. Test Arrow Key Adjustment
            # Focus the viewer and press ArrowUp
            page.locator("#viewer").click()
            page.keyboard.press("ArrowUp")
            expect(page.locator("#status")).to_have_text("Wire position adjusted.", timeout=10000)
            page.wait_for_timeout(1000) # Wait for render

            # 5. Test G-code Export Modal
            page.get_by_role("button", name="Export G-code").click()
            expect(page.locator("#code-modal")).to_be_visible()
            expect(page.locator("#code-title")).to_have_text("wire.gcode")
            expect(page.locator("#code-display")).not_to_be_empty()

            # 6. Take screenshot of the modal
            page.screenshot(path="jules-scratch/verification/verification.png")

            # 7. Test Copy and Close
            page.get_by_role("button", name="Copy to Clipboard").click()
            expect(page.locator("#status")).to_have_text("Code copied to clipboard!")

            page.locator(".modal-close-btn").click()
            expect(page.locator("#code-modal")).not_to_be_visible()

            print("Verification script completed successfully.")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()