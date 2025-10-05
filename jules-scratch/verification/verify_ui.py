import re
from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the application
            page.goto("http://0.0.0.0:8000")

            # 2. Set up file chooser and click upload button
            file_path = "STLfiles/assets/ayalower.stl"

            # Use a lambda to handle the file chooser dialog
            with page.expect_file_chooser() as fc_info:
                page.get_by_role("button", name="Upload STL").click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            # 3. Wait for the upload to complete
            expect(page.locator("#status")).to_have_text("File uploaded and wire generator initialized.", timeout=15000)

            # 4. Click the "Generate Wire" button
            page.get_by_role("button", name="Generate Wire").click()

            # 5. Wait for wire generation to complete
            expect(page.locator("#status")).to_have_text("Wire generated successfully.", timeout=60000) # Increased timeout for generation

            # 6. Wait for the 3D canvas to be stable and take a screenshot
            page.wait_for_timeout(2000) # Wait for rendering to settle
            page.screenshot(path="jules-scratch/verification/verification.png")

            print("Verification script completed successfully.")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()