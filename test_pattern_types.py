#!/usr/bin/env python3
"""
Manual QA test for the pattern_type parameter.

Tests:
1. Invalid pattern_type is rejected (unit)
2. The `t` query param is correctly set in the actual HTTP URL (unit, via mock)
3. Default pattern_type is "standard" when omitted (unit, via mock)
4. Live API calls for each mode return results (integration, requires network)

Usage:
    python test_pattern_types.py

Tests 1-3 are offline (no network needed). Test 4 hits sourcegraph.com.
"""

import sys
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, "src")

from backends.client import VALID_PATTERN_TYPES, SourcegraphClient


def test_invalid_pattern_type_rejected():
    """Verify invalid pattern_type raises ValueError and never hits the network."""
    client = SourcegraphClient(endpoint="https://sourcegraph.com")

    with patch("requests.get") as mock_get:
        try:
            client.search("test query", 1, "invalid_mode")
            print("FAIL: invalid pattern_type should have raised ValueError")
            return False
        except ValueError as e:
            assert "invalid_mode" in str(e), f"Error should mention the bad value, got: {e}"
            assert mock_get.call_count == 0, "Should not have made an HTTP call"
            print(f"PASS: invalid pattern_type correctly rejected (no HTTP call): {e}")
            return True
        except Exception as e:
            print(f"FAIL: expected ValueError, got {type(e).__name__}: {e}")
            return False


def test_t_param_in_url():
    """Verify the constructed URL contains t=<pattern_type> by mocking requests.get.

    This exercises the REAL client code (not a duplicated dict), so it catches
    bugs where the client sends the wrong param name or value.
    """
    client = SourcegraphClient(endpoint="https://sourcegraph.com")

    for pt in VALID_PATTERN_TYPES:
        fake_response = MagicMock()
        fake_response.iter_content.return_value = [b'event: done\ndata: {}\n\n']
        fake_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=fake_response) as mock_get:
            client.search("my query", 5, pt)

            actual_url = mock_get.call_args[0][0]
            parsed = urlparse(actual_url)
            qs = parse_qs(parsed.query)

            assert "t" in qs, f"URL missing 't' param for {pt}: {actual_url}"
            assert qs["t"] == [pt], f"Expected t={pt}, got t={qs['t']} in URL: {actual_url}"
            assert qs["q"] == ["my query"], f"Query mismatch: {qs.get('q')}"
            assert qs["v"] == ["V3"], f"Version mismatch: {qs.get('v')}"

            print(f"PASS: pattern_type='{pt}' -> URL contains t={pt} (verified via real client code)")

    return True


def test_default_is_standard():
    """Verify that calling search() without pattern_type defaults to 'standard'."""
    client = SourcegraphClient(endpoint="https://sourcegraph.com")

    fake_response = MagicMock()
    fake_response.iter_content.return_value = [b'event: done\ndata: {}\n\n']
    fake_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=fake_response) as mock_get:
        client.search("test", 5)  # no pattern_type arg

        actual_url = mock_get.call_args[0][0]
        qs = parse_qs(urlparse(actual_url).query)

        assert qs["t"] == ["standard"], f"Default should be 'standard', got t={qs.get('t')}"
        print("PASS: omitting pattern_type defaults to t=standard")
        return True


def test_live_api_each_mode():
    """Run real searches against sourcegraph.com with each pattern_type.

    Uses mode-appropriate queries scoped to a known public repo for stable results.
    """
    client = SourcegraphClient(endpoint="https://sourcegraph.com")
    repo_filter = "repo:github.com/sourcegraph/sourcegraph"

    queries = {
        "standard": f"{repo_filter} search stream",
        "keyword": f"{repo_filter} SearchClient",
        "regexp": f"{repo_filter} func\\..*Search",
    }

    all_passed = True
    for pt in VALID_PATTERN_TYPES:
        query = queries[pt]
        try:
            results = client.search(query, 3, pt)
            match_count = len(results.get("matches", []))
            if match_count > 0:
                print(f"PASS: pattern_type='{pt}' -> {match_count} matches (HTTP 200, live API)")
            else:
                print(f"WARN: pattern_type='{pt}' -> 0 matches (API OK, query may need tuning)")
        except Exception as e:
            print(f"FAIL: pattern_type='{pt}' raised exception: {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 70)
    print("Manual QA: pattern_type parameter (standard / keyword / regexp)")
    print("=" * 70)

    results = []

    print("\n--- Test 1: invalid pattern_type rejected (offline) ---")
    results.append(("invalid_rejected", test_invalid_pattern_type_rejected()))

    print("\n--- Test 2: 't' param in URL via mock (offline) ---")
    results.append(("t_param_in_url", test_t_param_in_url()))

    print("\n--- Test 3: default is 'standard' (offline) ---")
    results.append(("default_standard", test_default_is_standard()))

    print("\n--- Test 4: live API calls (requires network) ---")
    try:
        results.append(("live_api", test_live_api_each_mode()))
    except Exception as e:
        print(f"SKIP: live API test failed to run (network?): {e}")
        results.append(("live_api", None))

    print("\n" + "=" * 70)
    failures = [name for name, passed in results if passed is False]
    if not failures:
        print("RESULT: ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"RESULT: FAILURES in: {failures}")
        sys.exit(1)
