# Changelog

All notable changes to `tonpo` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [1.0.6] — 2026-05-04

### Added
- **Type Safety**: Full mypy strict mode compliance (`--strict --ignore-missing-imports`)
  - All 17 mypy type errors resolved
  - Complete type annotations on all public methods
  - Proper async/await type hints for websockets migration
  
- **Comprehensive Test Suite**: 1,400+ new test lines across 3 test modules
  - `test_client_validation.py` (578 lines) — parameter validation, edge cases
  - `test_transport_errors.py` (573 lines) — HTTP error handling, connection failures, HTML error page stripping
  - `test_websocket_resilience.py` (827 lines) — reconnection, orphan messages, callback resilience, task cleanup
  - Total of 97 tests covering transport, validation, and WebSocket layers

- **Input Validation**: Client-side parameter validation before gateway submission
  - Order volume must be positive
  - Order price required for limit/stop orders
  - Symbol cannot be empty or whitespace
  - Stop-loss and take-profit must be positive
  - Position close volume must be positive

- **New Method**: `get_position(ticket: int) -> Position`
  - Retrieve a single open position by ticket number

- **Code Quality & Linting**:
  - Ruff linter configuration (E, F, W, I checks)
  - Ruff format check with 100-char line length
  - MyPy strict type checking enabled in pyproject.toml

- **CI/CD Improvements**:
  - New `.github/workflows/quality-check.yml` — runs on push/PR
  - Updated `.github/workflows/publish.yml` — 2-stage pipeline (quality → publish)
  - Quality checks must pass before PyPI publishing

- **Documentation**:
  - Updated README with clearer API reference organization
  - Changelog entry for v1.0.6 features
  - Development setup instructions

- **Dependencies**:
  - Added `requirements.txt` (runtime: httpx, websockets)
  - Added `requirements-dev.txt` (dev: pytest, pytest-asyncio, respx, ruff, mypy)

### Fixed
- **WebSocket Async API Migration**
  - Changed import from `websockets.client.ClientConnection` (sync) to `websockets.asyncio.client.ClientConnection` (async)
  - Fixed type compatibility with modern websockets library (v11.0+)
  - Proper async/await handling throughout connection lifecycle

- **WebSocket Resilience**
  - Proper `asyncio.CancelledError` handling on disconnect
  - Task cleanup properly distinguishes between cancellation and other exceptions
  - Connection state consistency maintained during reconnect cycles

- **Error Logging**
  - Fixed `ConnectionClosed` exception logging (removed invalid `.rcvd_then` attribute access)
  - Safer string conversion with fallback for malformed exception data
  - Improved error messages for connection failures

- **Exception Handling**
  - All exceptions properly inherit from `TonpoError`
  - Connection errors no longer shadow Python's `builtins.ConnectionError`
  - Exception hierarchy fully documented

### Changed
- **Version**: 1.0.5 → 1.0.6 (patch release — bug fixes & quality improvements)
- **Code Organization**:
  - Alphabetically organized imports throughout codebase
  - Consistent type annotations (Dict[str, Any] instead of bare dict)
  - PEP 8 compliant formatting (100-char line limit, blank lines between methods)
  
- **README**:
  - "Tonpo Gateway" terminology updated to "Tonpo API" for clarity
  - API reference reorganized with better section hierarchy
  - Configuration options documented more clearly
  - Example code improved for clarity

- **pyproject.toml**:
  - Added `[tool.ruff]` configuration section
  - Added `[tool.mypy]` configuration section
  - Development dependencies now explicit

### Removed
- **CHANGELOG.md** (original file) — consolidated into this structured changelog
  - Previous changelog entries relocated to bottom of this file for historical reference

### Security
- No security changes in this release
- All dependencies locked to secure versions: httpx>=0.24.0, websockets>=11.0

### Performance
- No performance changes; all optimizations are internal
- WebSocket reconnection behavior unchanged (still respects max_reconnect_attempts)

### Deprecated
- No deprecations in this release

---

## [1.0.5] — 2026-04-19

### Added
- License file (Proprietary)

### Changed
- License updated to Proprietary (from previous license)
- `wait_for_active()` default timeout raised from 60s → 180s (Windows MT5 cold start takes 2–4 minutes on fresh VPS)

---

## [1.0.4] — 2026-04-24

### Added
- Bug fixes and improvements (details not documented)

---

## [1.0.0] — 2026-04-10

### Added
- **Initial Release**
- `TonpoClient` with `admin()` and `for_user()` factory methods
- Full account lifecycle: `create_account`, `wait_for_active`, `get_account_status`, `get_accounts`, `delete_account`, `pause_account`, `resume_account`
- Order placement: `place_market_buy`, `place_market_sell`, `place_limit_buy`, `place_limit_sell`, `place_stop_buy`, `place_stop_sell`
- Position management: `get_positions`, `get_position`, `close_position`, `modify_position`
- Account info: `get_account_info`
- Market data: `get_symbol_price` (REST + WebSocket cache fallback)
- WebSocket real-time data with auto-reconnection: ticks, quotes, candles, positions, order results, account updates
- Typed dataclass models: `TonpoConfig`, `UserCredentials`, `AccountCredentials`, `AccountInfo`, `Position`, `OrderResult`, `SymbolPrice`, `Tick`, `Quote`, `Candle`
- Exception hierarchy rooted at `TonpoError`
- `py.typed` marker for PEP 561 IDE type-hint support
- GitHub Actions workflow for automated PyPI publishing on git tag
- `TonpoConnectionError` named to avoid shadowing `builtins.ConnectionError`

---

## Release Notes Format

Use this format for PyPI/GitHub releases:

```markdown
## Tonpo Python SDK v1.0.6

**Release Date:** May 4, 2026

### Summary
Complete type safety and quality improvements release. All mypy errors resolved, comprehensive test suite added (1,400+ lines), and production-ready error handling implemented.

### What's New
- ✅ Full mypy strict mode compliance (0 type errors)
- ✅ 97 comprehensive tests across transport, validation, and WebSocket layers
- ✅ Client-side parameter validation (catches errors before API calls)
- ✅ WebSocket resilience improvements with proper error handling
- ✅ CI/CD quality gates ensure all future releases meet standards

### Bug Fixes
- Fixed WebSocket async API compatibility (websockets v11.0+)
- Fixed ConnectionClosed exception logging
- Improved disconnect task cleanup and error handling

### For Developers
- New `get_position(ticket)` method for single position lookup
- Strict type checking enabled (mypy --strict)
- Ruff linting configured (code quality gates)
- 1,400+ lines of production-ready tests

### Breaking Changes
None. All changes are backwards compatible.

### Upgrade Notes
Simply upgrade:
```bash
pip install --upgrade tonpo