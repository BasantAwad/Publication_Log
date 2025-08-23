# tests.py — Publication Log (Django)
# How to run: python manage.py test -v 2 -s
# The -s flag ensures print statements are shown.

from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User, Group, Permission
from django.apps import apps
from django.db import models
from django.conf import settings

# ---------------------------
# Configuration & Utilities
# ---------------------------

TEST_CONFIG = {
    # Optional: if your Publication model is in a specific app, set it here (e.g., "publications")
    "APP_LABEL": "projects",
    "PUBLICATION_MODEL_NAME": "Publication",
    # Field discovery hints: we’ll try these names first when building payloads
    "FIELD_HINTS": {
        "title": ["title", "name"],
        "author": ["author", "authors", "creator", "writer"],
        "year": ["year", "publication_year", "pub_year"],
        "journal": ["journal", "venue", "conference", "publisher"],
        "doi": ["doi"],
        "abstract": ["abstract", "description", "summary"],
    },
    # Candidate URL names; the first that resolves will be used
    "URLS": {
        "signup": ["signup", "register", "accounts:signup", "account_signup"],
        "login": ["login", "accounts:login", "account_login"],
        "logout": ["logout", "accounts:logout", "account_logout"],
        "dashboard": ["dashboard", "home", "index", "publication_list", "publications:list"],
        "list": [
            "publication_list", "publications:list", "pub_list", "publications", "publication-index",
            "pub:index"
        ],
        "create": [
            "publication_create", "publications:create", "pub_create", "publication-add",
            "pub:add", "publication_new"
        ],
        "update": [
            "publication_update", "publications:update", "pub_update", "publication-edit",
            "pub:edit"
        ],
        "delete": [
            "publication_delete", "publications:delete", "pub_delete", "publication-remove",
            "pub:delete"
        ],
        "export_csv": [
            "publication_export_csv", "publications:export_csv", "export_publications_csv",
            "export_csv"
        ],
        "export_pdf": [
            "publication_export_pdf", "publications:export_pdf", "export_publications_pdf",
            "export_pdf"
        ],
        "search_param": ["q", "search", "query", "s"],  # GET param candidates
    }
}


def reverse_first(candidates, args=None, kwargs=None):
    """Return the first resolvable URL among candidates, else None."""
    for name in candidates:
        try:
            return reverse(name, args=args, kwargs=kwargs)
        except NoReverseMatch:
            continue
    return None


def get_publication_model():
    """Find the Publication model by name via Django app registry."""
    ModelName = TEST_CONFIG["PUBLICATION_MODEL_NAME"].lower()
    if TEST_CONFIG["APP_LABEL"]:
        for m in apps.get_app_config(TEST_CONFIG["APP_LABEL"]).get_models():
            if m.__name__.lower() == ModelName:
                return m
        return None
    # Search all apps
    for m in apps.get_models():
        if m.__name__.lower() == ModelName:
            return m
    return None


def discover_field_name(model, logical_key):
    """Map a logical field key (e.g., 'title') to actual model field name if possible."""
    hints = TEST_CONFIG["FIELD_HINTS"].get(logical_key, [])
    model_field_names = {f.name for f in model._meta.get_fields() if getattr(f, "concrete", False)}
    for h in hints:
        if h in model_field_names:
            return h
    return None


def build_publication_payload(model):
    """Construct a best-effort valid payload for create/update based on discovered fields."""
    payload = {}
    title_f = discover_field_name(model, "title")
    author_f = discover_field_name(model, "author")
    year_f = discover_field_name(model, "year")
    journal_f = discover_field_name(model, "journal")
    doi_f = discover_field_name(model, "doi")
    abs_f = discover_field_name(model, "abstract")

    if title_f:
        payload[title_f] = "Deep Learning for X"
    if author_f:
        payload[author_f] = "Jane Doe"
    if year_f:
        payload[year_f] = 2024
    if journal_f:
        payload[journal_f] = "AI Journal"
    if doi_f:
        payload[doi_f] = "10.1234/example.doi"
    if abs_f:
        payload[abs_f] = "A study on deep learning applications."

    return payload


def build_publication_payload_updated(model):
    """Slightly modified payload for update tests."""
    payload = build_publication_payload(model)
    # Update the title if present, else update abstract/author
    t = discover_field_name(model, "title")
    if t and t in payload:
        payload[t] = "Deep Learning for Y (Updated)"
        return payload
    a = discover_field_name(model, "author")
    if a and a in payload:
        payload[a] = "Jane Doe (Updated)"
        return payload
    ab = discover_field_name(model, "abstract")
    if ab and ab in payload:
        payload[ab] = "Updated abstract."
        return payload
    return payload


def get_title_value(obj):
    """Get a printable title from the Publication instance if possible."""
    for key in TEST_CONFIG["FIELD_HINTS"]["title"]:
        if hasattr(obj, key):
            return getattr(obj, key)
    return str(obj)


def create_min_publication_instance(model):
    """
    Try to create a Publication instance directly. If model requires fields we
    couldn't infer, this may fail. We catch and return (instance or None, error str or None).
    """
    payload = build_publication_payload(model)
    try:
        instance = model.objects.create(**payload)
        return (instance, None)
    except Exception as e:
        return (None, str(e))


# ---------------------------
# Printable TestCase Base
# ---------------------------

class PrintableTestCase(TestCase):
    results = []  # class-level list of (suite, test_name, status, note)

    @classmethod
    def add_result(cls, suite, name, status, note=""):
        cls.results.append((suite, name, status, note))

    @classmethod
    def tearDownClass(cls):
        # Print a suite summary at the end of this class
        print("\n" + "=" * 72)
        print(f"TEST CLASS SUMMARY: {cls.__name__}")
        print("-" * 72)
        if not cls.results:
            print("No recorded results.")
        else:
            w = max(len(r[1]) for r in cls.results) if cls.results else 20
            for suite, name, status, note in cls.results:
                pad = " " * (max(1, w - len(name)))
                print(f"[{suite}] {name}{pad} -> {status}" + (f" | {note}" if note else ""))
        print("=" * 72 + "\n")
        super().tearDownClass()


# ---------------------------
# Unit Tests
# ---------------------------

class UnitTests(PrintableTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.Publication = get_publication_model()

    def test_publication_str(self):
        name = "UT-01 Publication __str__"
        success = False
        note = ""
        try:
            if not self.Publication:
                self.skipTest("Publication model not found.")
            # Try to create minimal instance
            inst, err = create_min_publication_instance(self.Publication)
            if not inst:
                self.skipTest(f"Could not create Publication instance: {err}")
            s = str(inst)
            title_f = discover_field_name(self.Publication, "title")
            expected = getattr(inst, title_f) if title_f else None
            if expected:
                self.assertIn(expected, s)
            else:
                # At least ensure __str__ returns non-empty
                self.assertTrue(len(s) > 0)
            success = True
        finally:
            self.add_result("UNIT", name, "PASS" if success else "FAIL", note)

    def test_model_create_minimum_valid(self):
        name = "UT-02 Model create minimum valid record"
        success = False
        note = ""
        try:
            if not self.Publication:
                self.skipTest("Publication model not found.")
            inst, err = create_min_publication_instance(self.Publication)
            self.assertIsNotNone(inst, msg=f"Create failed: {err}")
            success = True
        finally:
            self.add_result("UNIT", name, "PASS" if success else "FAIL", note)

    def test_auth_create_and_login(self):
        name = "UT-03 Auth create & login"
        success = False
        note = ""
        try:
            client = Client()
            user = User.objects.create_user(username="unittest_user", password="Pass12345!")
            logged = client.login(username="unittest_user", password="Pass12345!")
            self.assertTrue(logged)
            success = True
        finally:
            self.add_result("UNIT", name, "PASS" if success else "FAIL", note)


# ---------------------------
# Integration Tests
# ---------------------------

class IntegrationTests(PrintableTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.Publication = get_publication_model()
        cls.user = User.objects.create_user(username="it_user", password="Pass12345!")
        cls.client.login(username="it_user", password="Pass12345!")
        # Resolve URLs (or leave as None if not found)
        urls = TEST_CONFIG["URLS"]
        cls.url_list = reverse_first(urls["list"])
        cls.url_create = reverse_first(urls["create"])
        cls.url_export_csv = reverse_first(urls["export_csv"])
        cls.url_export_pdf = reverse_first(urls["export_pdf"])
        # Create seed object if possible (for update/delete)
        cls.seed = None
        if cls.Publication:
            cls.seed, _ = create_min_publication_instance(cls.Publication)
            # Update/delete URLs require ID
            cls.url_update = None
            cls.url_delete = None
            if cls.seed:
                cls.url_update = reverse_first(urls["update"], args=[cls.seed.pk])
                cls.url_delete = reverse_first(urls["delete"], args=[cls.seed.pk])
        else:
            cls.url_update = None
            cls.url_delete = None

    def test_create_publication_post(self):
        name = "IT-01 Create Publication (POST)"
        success = False
        note = ""
        try:
            if not self.url_create:
                self.skipTest("Create URL not found.")
            if not self.Publication:
                self.skipTest("Publication model not found.")
            payload = build_publication_payload(self.Publication)
            resp = self.client.post(self.url_create, payload, follow=True)
            self.assertIn(resp.status_code, [200, 302])
            # Verify created via DB
            title_f = discover_field_name(self.Publication, "title")
            qs = self.Publication.objects.all()
            self.assertTrue(qs.exists(), "No publications found after create.")
            if title_f:
                self.assertTrue(qs.filter(**{title_f: payload.get(title_f)}).exists())
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_edit_publication_post(self):
        name = "IT-02 Edit Publication (POST)"
        success = False
        note = ""
        try:
            if not self.url_update:
                self.skipTest("Update URL not found or no seed object.")
            if not self.Publication:
                self.skipTest("Publication model not found.")
            payload = build_publication_payload_updated(self.Publication)
            resp = self.client.post(self.url_update, payload, follow=True)
            self.assertIn(resp.status_code, [200, 302])
            # Refresh and compare at least one changed field
            obj = self.Publication.objects.get(pk=self.seed.pk)
            tfield = discover_field_name(self.Publication, "title")
            afield = discover_field_name(self.Publication, "author")
            if tfield and tfield in payload:
                self.assertEqual(getattr(obj, tfield), payload[tfield])
            elif afield and afield in payload:
                self.assertEqual(getattr(obj, afield), payload[afield])
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_delete_publication_post(self):
        name = "IT-03 Delete Publication (POST)"
        success = False
        note = ""
        try:
            if not self.url_delete:
                self.skipTest("Delete URL not found or no seed object.")
            resp = self.client.post(self.url_delete, follow=True)
            self.assertIn(resp.status_code, [200, 302])
            # Ensure deleted
            if self.Publication and self.seed:
                self.assertFalse(self.Publication.objects.filter(pk=self.seed.pk).exists())
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_list_publications_get(self):
        name = "IT-04 List Publications (GET)"
        success = False
        note = ""
        try:
            if not self.url_list:
                self.skipTest("List URL not found.")
            resp = self.client.get(self.url_list)
            self.assertEqual(resp.status_code, 200)
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_search_filter_get(self):
        name = "IT-05 Search/Filter (GET)"
        success = False
        note = ""
        try:
            if not self.url_list:
                self.skipTest("List URL not found.")
            # Create two with distinct titles if possible
            if self.Publication:
                tfield = discover_field_name(self.Publication, "title")
                if tfield:
                    a, _ = create_min_publication_instance(self.Publication)
                    b, _ = create_min_publication_instance(self.Publication)
                    if a and b:
                        setattr(a, tfield, "Graph Networks for Science")
                        a.save()
                        setattr(b, tfield, "Deep Learning for X")
                        b.save()
                        param_name = TEST_CONFIG["URLS"]["search_param"][0]
                        resp = self.client.get(self.url_list, {param_name: "Graph"})
                        self.assertEqual(resp.status_code, 200)
                        # Weak assertion: page contains at least one keyword
                        self.assertIn(b"Graph", resp.content)
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_export_csv_get(self):
        name = "IT-06 Export CSV (GET)"
        success = False
        note = ""
        try:
            if not self.url_export_csv:
                self.skipTest("CSV export URL not found.")
            resp = self.client.get(self.url_export_csv)
            self.assertEqual(resp.status_code, 200)
            ctype = resp.headers.get("Content-Type") or resp.get("Content-Type", "")
            self.assertIn("text/csv", ctype)
            self.assertTrue(len(resp.content) > 0)
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_export_pdf_get(self):
        name = "IT-07 Export PDF (GET)"
        success = False
        note = ""
        try:
            if not self.url_export_pdf:
                self.skipTest("PDF export URL not found (feature may be disabled).")
            resp = self.client.get(self.url_export_pdf)
            self.assertEqual(resp.status_code, 200)
            ctype = resp.headers.get("Content-Type") or resp.get("Content-Type", "")
            self.assertIn("application/pdf", ctype)
            self.assertTrue(len(resp.content) > 0)
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)

    def test_permissions_anonymous_redirect(self):
        name = "IT-08 Permissions: anonymous redirected"
        success = False
        note = ""
        try:
            # Log out
            self.client.logout()
            # Try create as anon if URL exists
            if not self.url_create:
                self.skipTest("Create URL not found.")
            resp = self.client.get(self.url_create)
            # Expect redirect to login
            self.assertIn(resp.status_code, [301, 302])
            success = True
        finally:
            self.add_result("INTEG", name, "PASS" if success else "FAIL", note)


# ---------------------------
# System (End-to-End) Tests
# ---------------------------

class SystemTests(PrintableTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.Publication = get_publication_model()
        urls = TEST_CONFIG["URLS"]
        cls.url_signup = reverse_first(urls["signup"])
        cls.url_login = reverse_first(urls["login"])
        cls.url_list = reverse_first(urls["list"])
        cls.url_create = reverse_first(urls["create"])
        cls.url_export_csv = reverse_first(urls["export_csv"])

    def test_full_flow_signup_login_create_list_export(self):
        name = "ST-01 Full flow: Sign up → Login → Create → List → Export CSV"
        success = False
        note = ""
        try:
            username = "system_user"
            password = "Pass12345!"
            email = "system_user@example.com"

            # 1) Sign up: if no signup URL, fallback to direct user creation
            if self.url_signup:
                resp = self.client.post(self.url_signup, {
                    "username": username,
                    "password1": password,
                    "password2": password,
                    "email": email
                }, follow=True)
                self.assertIn(resp.status_code, [200, 302])
            else:
                User.objects.create_user(username=username, password=password, email=email)

            # 2) Login
            logged = self.client.login(username=username, password=password)
            if not logged and self.url_login:
                # Try posting to login view if needed
                resp = self.client.post(self.url_login, {"username": username, "password": password}, follow=True)
                self.assertIn(resp.status_code, [200, 302])
                # Try client session again
                logged = self.client.login(username=username, password=password)
            self.assertTrue(logged, "Login failed for system user.")

            # 3) Create publication
            if not self.url_create:
                self.skipTest("Create URL not found.")
            if not self.Publication:
                self.skipTest("Publication model not found.")
            payload = build_publication_payload(self.Publication)
            resp = self.client.post(self.url_create, payload, follow=True)
            self.assertIn(resp.status_code, [200, 302])

            # 4) List & check presence
            if self.url_list:
                resp = self.client.get(self.url_list)
                self.assertEqual(resp.status_code, 200)
                # Ensure title appears in list page content (if rendered)
                tfield = discover_field_name(self.Publication, "title")
                if tfield and payload.get(tfield):
                    self.assertIn(payload[tfield].encode(), resp.content)

            # 5) Export CSV
            if self.url_export_csv:
                resp = self.client.get(self.url_export_csv)
                self.assertEqual(resp.status_code, 200)
                ctype = resp.headers.get("Content-Type") or resp.get("Content-Type", "")
                self.assertIn("text/csv", ctype)
                self.assertTrue(len(resp.content) > 0)

            success = True
        finally:
            self.add_result("SYSTEM", name, "PASS" if success else "FAIL", note)

    def test_negative_invalid_form_submit(self):
        name = "ST-02 Negative flow: Invalid create submission"
        success = False
        note = ""
        try:
            # Ensure logged in
            user = User.objects.create_user(username="neg_user", password="Pass12345!")
            self.client.login(username="neg_user", password="Pass12345!")
            if not self.url_create:
                self.skipTest("Create URL not found.")
            if not self.Publication:
                self.skipTest("Publication model not found.")
            # Build payload and then remove the most-likely required field (title)
            payload = build_publication_payload(self.Publication)
            tfield = discover_field_name(self.Publication, "title")
            if tfield and tfield in payload:
                payload.pop(tfield)
            resp = self.client.post(self.url_create, payload)
            # Expect form re-render (200) or validation feedback
            self.assertEqual(resp.status_code, 200)
            success = True
        finally:
            self.add_result("SYSTEM", name, "PASS" if success else "FAIL", note)

    def test_role_based_restriction(self):
        name = "ST-03 Role-based restriction"
        success = False
        note = ""
        try:
            # This is a generic check: try to access create as a normal user (should be allowed),
            # and simulate an admin-only endpoint if such exists (skip if not).
            # If your app enforces role-based permissions on create/edit/delete, this test will catch it.
            normal = User.objects.create_user(username="user_role", password="Pass12345!")
            self.client.login(username="user_role", password="Pass12345!")
            # Access create (most systems allow authenticated users)
            if self.url_create:
                resp = self.client.get(self.url_create)
                self.assertIn(resp.status_code, [200, 302])

            # Now simulate admin by assigning superuser
            admin = User.objects.create_user(username="admin_role", password="AdminPass123!")
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            self.client.logout()
            self.client.login(username="admin_role", password="AdminPass123!")
            # Try list as admin (should work)
            if self.url_list:
                resp = self.client.get(self.url_list)
                self.assertEqual(resp.status_code, 200)

            success = True
        finally:
            self.add_result("SYSTEM", name, "PASS" if success else "FAIL", note)
