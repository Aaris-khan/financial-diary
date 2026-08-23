# Universal Long-Press Premium PDF QA

The patched `index.html` was served locally and opened in Chromium. The app loaded without JavaScript runtime errors; the only console warning was the pre-existing missing `sw.js` service-worker response (HTTP 404).

A browser runtime check confirmed that `window.AarishTitaniumPDF` is an object and `aarishExportCardToPremiumPdfCoreV1` is a function. An isolated mock-state render produced one export card each for Milk, Credit Ledger, and Diary, with decoded metadata keys `Alice Test`, `Alice Test`, and `d1` respectively.

A synthetic touch pointer test on the Milk card held for 780 ms. The exporter was invoked exactly once, the pressed state was active during the hold, and the pressed state was removed after pointerup. This validates the 720 ms threshold and cleanup path.

Static validation also passed: all eight executable JavaScript blocks passed Node syntax checking, `git diff --check` passed, six card export types are present, and legacy inline long-press attributes/helper references were removed. The service-worker warning is unrelated to this feature and was not changed.

A second browser test verified that a short touch tap invoked the exporter zero times, and a pointer move beyond the 14 px tolerance before the threshold also invoked it zero times. The card visual state was cleaned up in both cases.

The export builder was runtime-tested with mocked Milk, Credit Ledger, and Diary records. It mapped Milk to one-row `MILK STATEMENT (LIFETIME)`, Credit to one-row `CREDIT LEDGER (LIFETIME)`, and Diary to the correct `d1` entry titled `Test page`.
