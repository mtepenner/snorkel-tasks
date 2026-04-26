# [UI-831] Build static UI for testing

**As a** tester
**I need** a super basic static HTML page
**So that** I can run our e2e/unit test suite against it

**AC (Acceptance Criteria):**
* Drop it in the task root (`/app` in the sandbox container). The root URL (`/`) needs to serve this page. Just `index.html` is fine.
* Document `<title>` has to be exactly `UI task`. (Don't get creative here, the tests will fail).
* Add an `<h1>` (or similar heading) with exactly `Hello, UI task`.
* Needs a `<button>` with the label `Click me`.
* The button MUST be focusable when clicked.

**Notes:**
Plz don't overengineer this, just hardcoded HTML is fine. Need this ASAP so the verifier can run its checks. Thx.
