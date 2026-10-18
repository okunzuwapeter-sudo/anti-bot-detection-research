# Experiment Notes: Local Anti-Bot Detection Signals

## 1. Objective

Compare the HTTP metadata exposed by a conventional Python `requests` client and a Chromium browser controlled by Playwright when both contact the same local observation server.

This experiment follows the local-lab approach in *How Modern Anti-Bot Systems Detect Scrapers*. It is intended to illustrate observable differences between client types, not to identify or classify traffic from a public website.

## 2. Files and roles

- `observer.py` — runs a local HTTP server at `127.0.0.1:8080`, records request metadata, and returns a JSON response.
- `requests_client.py` — sends a GET request to `/demo?source=requests` using `requests`.
- `browser_client.py` — opens `/demo?source=playwright` in headless Chromium through Playwright and prints the navigation status, page title, and response body.
- `requirements.txt` — lists `requests` and `playwright` as Python dependencies.

The observer is bound to the loopback interface, so this setup is intended for tests on the same computer.

## 3. Procedure

1. Install the Python dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Install the Chromium binary used by Playwright:
   ```bash
   python -m playwright install chromium
   ```
3. Start the observer in one terminal:
   ```bash
   python observer.py
   ```
4. In a second terminal, run the standard Python client:
   ```bash
   python requests_client.py
   ```
5. Run the browser client while the observer is still running:
   ```bash
   python browser_client.py
   ```
6. Compare the two observer records, paying attention to the request path, HTTP version, header names and values, and the response status.

## 4. Results

### 4.1 Standard Python client

The `requests_client.py` script sends a GET request to:

`http://127.0.0.1:8080/demo?source=requests`

The observer records the request method, path, client address, HTTP version, timestamp, request identifier, and the HTTP headers presented to Python's HTTP server. The client receives an HTTP success response (`200`) containing JSON with an `ok` field, a request identifier, a header count, and a note explaining that the lab records local HTTP metadata rather than a TLS fingerprint.

The client also prints the request headers available through the `requests` response object. These are useful for comparison with the server-side record, but they are not a packet capture.

### 4.2 Playwright Chromium client

The `browser_client.py` script navigates Chromium to:

`http://127.0.0.1:8080/demo?source=playwright`

The observer records the browser navigation as a separate GET request. The script prints the main navigation response status, the page title, and the body text returned by the local server. The response is JSON rather than a designed HTML page, so Chromium may display the JSON content directly; that is expected for this test endpoint.

The browser request can present a different set of HTTP headers from the `requests` client. The exact header values depend on the installed versions and runtime configuration, so the meaningful comparison is the actual pair of records from the local observer rather than a fixed list of supposedly universal header values.

### 4.3 Comparison summary

| Observation | `requests_client.py` | `browser_client.py` |
|---|---|---|
| Destination | Local observer at `127.0.0.1:8080` | Same local observer |
| Request path | `/demo?source=requests` | `/demo?source=playwright` |
| Main operation | Python HTTP GET request | Chromium top-level navigation |
| Server-side metadata | Method, path, client address, HTTP version, timestamp, request ID, and headers | Same categories of metadata |
| Client-side output | Status, JSON response, and request headers | Navigation status, page title, and response body |
| Header profile | Depends on the installed `requests` version and request configuration | Depends on Chromium, Playwright, and browser-context configuration |
| TLS fingerprint | Not collected | Not collected by this observer |

## 5. Interpretation

The lab demonstrates that a server-side observer can compare request metadata from different client implementations. Header sets and request context can contribute to traffic analysis, but a single header or missing browser-specific field is not proof of automated or malicious activity.

The request path deliberately labels each client (`source=requests` and `source=playwright`), making the records easy to distinguish. This label is part of the experiment URL; it is not itself a reliable bot-detection signal.

The observer reports the HTTP representation made available by Python's request parser. It does not preserve a byte-for-byte packet trace and does not inspect TLS ClientHello data. Consequently, this experiment does not measure JA3/JA4 fingerprints, TLS negotiation characteristics, JavaScript execution signals, browser interaction patterns, or how a real anti-bot service would score a request.

## 6. Limitations

- Only a local loopback endpoint is used; no third-party website is contacted.
- The test compares one ordinary Python client with one headless Chromium navigation.
- Header values can change with Python, `requests`, Playwright, Chromium, operating-system, and configuration updates.
- A headless browser is not guaranteed to behave identically to a person's everyday browser session.
- The experiment does not establish a general rule for all Python clients or all browsers.
- No conclusion about a real user's intent, legitimacy, or authorization can be drawn from these two requests alone.

## 7. Privacy and safe handling

The observer is designed to redact sensitive authentication and cookie header values from its printed output and does not log request bodies. Keep the server bound to `127.0.0.1`; do not expose this demonstration server to an untrusted network. Review any logs before publishing them, and remove environment-specific or personal information.

## 8. Conclusion

The local experiment provides a reproducible way to inspect and compare HTTP metadata generated by `requests` and Playwright-controlled Chromium. It supports a narrow conclusion: client implementations may produce distinguishable request metadata, but those differences must be interpreted in context. This small lab is a methodology demonstration, not a production anti-bot detector or a TLS-fingerprinting tool.
