#!/usr/bin/env python3
"""Test script for ha_health_record integration."""
import sys
import ast
import json
from pathlib import Path

def test_python_syntax():
    """Test all Python files for syntax errors."""
    print("=" * 60)
    print("Testing Python Syntax")
    print("=" * 60)

    errors = []
    base_path = Path(__file__).parent

    py_files = list(base_path.glob("*.py"))

    for py_file in py_files:
        if py_file.name == "test_integration.py":
            continue
        try:
            with open(py_file, "r") as f:
                source = f.read()
            ast.parse(source)
            print(f"  [OK] {py_file.name}")
        except SyntaxError as e:
            errors.append(f"{py_file.name}: {e}")
            print(f"  [FAIL] {py_file.name}: {e}")

    return len(errors) == 0, errors


def test_manifest():
    """Test manifest.json is valid."""
    print("\n" + "=" * 60)
    print("Testing manifest.json")
    print("=" * 60)

    manifest_path = Path(__file__).parent / "manifest.json"

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)

        required_keys = ["domain", "name", "version"]
        missing = [k for k in required_keys if k not in manifest]

        if missing:
            print(f"  [FAIL] Missing required keys: {missing}")
            return False, [f"Missing keys: {missing}"]

        print(f"  [OK] Domain: {manifest.get('domain')}")
        print(f"  [OK] Name: {manifest.get('name')}")
        print(f"  [OK] Version: {manifest.get('version')}")
        return True, []
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False, [str(e)]


def test_frontend_js():
    """Test frontend JavaScript file exists and has required components."""
    print("\n" + "=" * 60)
    print("Testing Frontend JavaScript")
    print("=" * 60)

    js_path = Path(__file__).parent / "frontend" / "ha-health-record-panel.js"

    if not js_path.exists():
        print(f"  [FAIL] Frontend file not found: {js_path}")
        return False, ["Frontend file not found"]

    with open(js_path, "r") as f:
        content = f.read()

    checks = [
        ("class HaHealthRecordPanel", "Panel class definition"),
        ("customElements.define", "Custom element registration"),
        ("_openGrowthDialog", "Growth dialog method"),
        ("_submitGrowth", "Growth submit method"),
        ("growth-btn", "Growth button class"),
        ("ha_health_record/update_growth", "Growth WebSocket call"),
        ("ha_health_record/log_activity", "Activity WebSocket call"),
        ("_renderQuickAddTab", "Quick Add tab render method"),
        ("_renderRecordTab", "Record tab render method"),
        ("_renderMembersManagement", "Members management render"),
    ]

    errors = []
    for check, desc in checks:
        if check in content:
            print(f"  [OK] {desc}")
        else:
            print(f"  [FAIL] Missing: {desc}")
            errors.append(f"Missing: {desc}")

    return len(errors) == 0, errors


def test_panel_registration():
    """Test panel.py uses correct registration method."""
    print("\n" + "=" * 60)
    print("Testing Panel Registration")
    print("=" * 60)

    panel_path = Path(__file__).parent / "panel.py"

    with open(panel_path, "r") as f:
        content = f.read()

    checks = [
        ("panel_custom.async_register_panel", "Uses panel_custom.async_register_panel"),
        ("async_remove_panel", "Has panel removal function"),
        ("PANEL_URL_PATH", "Has URL path constant"),
        ("FRONTEND_SCRIPT_PATH", "Has frontend script path constant"),
        ("webcomponent_name=", "Registers webcomponent"),
    ]

    # Check for incorrect usage
    bad_checks = []

    errors = []
    for check, desc in checks:
        if check in content:
            print(f"  [OK] {desc}")
        else:
            print(f"  [FAIL] Missing: {desc}")
            errors.append(f"Missing: {desc}")

    for check, desc in bad_checks:
        if check in content:
            print(f"  [FAIL] {desc}")
            errors.append(desc)
        else:
            print(f"  [OK] {desc}")

    return len(errors) == 0, errors


def test_websocket_apis():
    """Test all required WebSocket APIs are registered."""
    print("\n" + "=" * 60)
    print("Testing WebSocket APIs")
    print("=" * 60)

    panel_path = Path(__file__).parent / "panel.py"

    with open(panel_path, "r") as f:
        content = f.read()

    required_apis = [
        "ha_health_record/get_members",
        "ha_health_record/get_records",
        "ha_health_record/log_activity",
        "ha_health_record/update_growth",
        "ha_health_record/update_record",
        "ha_health_record/delete_record",
        "ha_health_record/add_activity_type",
        "ha_health_record/update_activity_type",
        "ha_health_record/delete_activity_type",
        "ha_health_record/add_growth_type",
        "ha_health_record/update_growth_type",
        "ha_health_record/delete_growth_type",
        "ha_health_record/add_member",
        "ha_health_record/update_member",
        "ha_health_record/delete_member",
    ]

    errors = []
    for api in required_apis:
        if api in content:
            print(f"  [OK] {api}")
        else:
            print(f"  [FAIL] Missing API: {api}")
            errors.append(f"Missing API: {api}")

    return len(errors) == 0, errors


def test_imports():
    """Test that all imports work correctly."""
    print("\n" + "=" * 60)
    print("Testing Python Imports")
    print("=" * 60)

    try:
        # Test basic imports that should work
        import voluptuous as vol
        print("  [OK] voluptuous")
    except ImportError as e:
        print(f"  [FAIL] voluptuous: {e}")
        return False, [str(e)]

    try:
        from homeassistant.components import websocket_api
        print("  [OK] homeassistant.components.websocket_api")
    except ImportError as e:
        print(f"  [FAIL] homeassistant.components.websocket_api: {e}")
        return False, [str(e)]

    try:
        from homeassistant.components.frontend import async_register_built_in_panel, async_remove_panel
        print("  [OK] homeassistant.components.frontend.async_register_built_in_panel")
        print("  [OK] homeassistant.components.frontend.async_remove_panel")
    except ImportError as e:
        print(f"  [FAIL] homeassistant.components.frontend: {e}")
        return False, [str(e)]

    try:
        from homeassistant.components.http import StaticPathConfig
        print("  [OK] homeassistant.components.http.StaticPathConfig")
    except ImportError as e:
        print(f"  [FAIL] homeassistant.components.http: {e}")
        return False, [str(e)]

    return True, []


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("# ha_health_record Integration Tests")
    print("#" * 60)

    all_passed = True
    all_errors = []

    tests = [
        ("Python Syntax", test_python_syntax),
        ("Manifest", test_manifest),
        ("Frontend JS", test_frontend_js),
        ("Panel Registration", test_panel_registration),
        ("WebSocket APIs", test_websocket_apis),
        ("Python Imports", test_imports),
    ]

    results = []
    for name, test_func in tests:
        passed, errors = test_func()
        results.append((name, passed, errors))
        if not passed:
            all_passed = False
            all_errors.extend(errors)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed, errors in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")

    print("\n" + "-" * 60)
    if all_passed:
        print("All tests PASSED!")
        return 0
    else:
        print(f"Some tests FAILED. Errors: {len(all_errors)}")
        for err in all_errors:
            print(f"  - {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
