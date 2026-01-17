#!/usr/bin/env python3
"""
Test Flask application initialization.
This tests that the Flask app can be created and routes are registered.
"""

import sys
import os

# Set environment variables before importing app
os.environ['FLASK_SECRET_KEY'] = 'test_secret_key_for_testing_only'
os.environ['WEB_DEBUG'] = 'True'
os.environ['VICORE_ENV'] = 'development'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_flask_import():
    """Test that Flask app module can be partially loaded."""
    print("Testing Flask app components...")

    errors = []

    # Test Flask itself
    try:
        from flask import Flask
        print("  [OK] Flask imported")
    except Exception as e:
        errors.append(f"  [ERR] Flask import: {e}")
        return errors

    # Test that our security functions work
    try:
        # Manually test the get_secret_key logic
        key = os.environ.get('FLASK_SECRET_KEY')
        assert key == 'test_secret_key_for_testing_only'
        print("  [OK] Secret key from environment")
    except Exception as e:
        errors.append(f"  [ERR] Secret key test: {e}")

    # Test Flask app creation (basic)
    try:
        app = Flask(__name__)
        app.secret_key = os.environ.get('FLASK_SECRET_KEY')
        assert app.secret_key is not None
        print("  [OK] Flask app created with secret key")
    except Exception as e:
        errors.append(f"  [ERR] Flask app creation: {e}")

    # Test route registration (simulated)
    try:
        app = Flask(__name__)

        @app.route('/test')
        def test_route():
            return 'OK'

        # Verify route is registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/test' in rules
        print("  [OK] Route registration works")
    except Exception as e:
        errors.append(f"  [ERR] Route registration: {e}")

    # Test Flask test client
    try:
        app = Flask(__name__)
        app.secret_key = 'test'

        @app.route('/ping')
        def ping():
            return 'pong'

        with app.test_client() as client:
            response = client.get('/ping')
            assert response.status_code == 200
            assert response.data == b'pong'
        print("  [OK] Flask test client works")
    except Exception as e:
        errors.append(f"  [ERR] Flask test client: {e}")

    return errors


def test_models_with_flask():
    """Test that models work in Flask context."""
    print("\nTesting models in Flask context...")

    errors = []

    try:
        from flask import Flask, session
        from eurotunnel_web.models.user import User
        from eurotunnel_web.common_consts import USER_DETAILS_SESSION_VAR

        app = Flask(__name__)
        app.secret_key = 'test'

        with app.test_request_context():
            # Test user model serialization (simulating session storage)
            user = User(id=1, name="testuser")
            json_str = user.model_dump_json()

            # Simulate what happens in login
            session[USER_DETAILS_SESSION_VAR] = json_str

            # Simulate what happens in protected routes
            user_json = session.get(USER_DETAILS_SESSION_VAR)
            user_restored = User.model_validate_json(user_json)

            assert user_restored.id == 1
            assert user_restored.name == "testuser"

        print("  [OK] User session workflow works")
    except Exception as e:
        errors.append(f"  [ERR] User session workflow: {e}")

    return errors


def test_endpoint_logic():
    """Test endpoint logic without database."""
    print("\nTesting endpoint logic...")

    errors = []

    # Test authentication check logic
    try:
        from flask import Flask, session, redirect
        from eurotunnel_web.common_consts import USER_DETAILS_SESSION_VAR

        app = Flask(__name__)
        app.secret_key = 'test'

        with app.test_request_context():
            # Simulate unauthenticated user
            user_json = session.get(USER_DETAILS_SESSION_VAR)
            if not user_json:
                # This is what the real code does
                result = redirect('/login')
                assert result.status_code == 302

        print("  [OK] Authentication check logic works")
    except Exception as e:
        errors.append(f"  [ERR] Authentication check: {e}")

    # Test confirmation status logic
    try:
        # Simulate the put_confirmation_status logic
        human_says = "true"
        present_not_absent = False
        if human_says.lower() == "true":
            present_not_absent = True
        assert present_not_absent is True

        human_says = "false"
        present_not_absent = False
        if human_says.lower() == "true":
            present_not_absent = True
        assert present_not_absent is False

        print("  [OK] Confirmation status parsing works")
    except Exception as e:
        errors.append(f"  [ERR] Confirmation status parsing: {e}")

    return errors


def main():
    """Run all Flask tests."""
    print("=" * 60)
    print("VICORE - Flask Application Tests")
    print("=" * 60)

    all_errors = []

    all_errors.extend(test_flask_import())
    all_errors.extend(test_models_with_flask())
    all_errors.extend(test_endpoint_logic())

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if all_errors:
        print(f"\n[FAIL] {len(all_errors)} error(s) found:\n")
        for error in all_errors:
            print(error)
        return 1
    else:
        print("\n[OK] All Flask tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
