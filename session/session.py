import json

from django.utils import timezone

from session.models import Session


class SessionStore:
    def __init__(self, session_key=None):
        self.modified = False
        self.accessed = False
        self._session_cache = None
        self.model = None
        self.session_key = session_key

        if session_key:
            try:
                self.model = Session.objects.get(session_key=session_key)
                if self.model.is_expired():
                    self.model.delete()
                    self.model = None
                    self.session_key = None
            except Session.DoesNotExist:
                self.session_key = None

        if self.model is None:
            self.model = Session.create()
            self.session_key = self.model.session_key
            self.modified = True

    def _load(self):
        if self._session_cache is None:
            self.accessed = True
            try:
                self._session_cache = json.loads(self.model.session_data or "{}")
            except json.JSONDecodeError:
                self._session_cache = {}
        return self._session_cache

    def __getitem__(self, key):
        return self._load()[key]

    def __setitem__(self, key, value):
        self._load()[key] = value
        self.modified = True

    def __delitem__(self, key):
        del self._load()[key]
        self.modified = True

    def __contains__(self, key):
        return key in self._load()

    def get(self, key, default=None):
        return self._load().get(key, default)

    def pop(self, key, default=None):
        self.accessed = True
        value = self._load().pop(key, default)
        self.modified = True
        return value

    def clear(self):
        self._load().clear()
        self.modified = True

    def save(self, must_create=False):
        if not self.modified and not must_create:
            return
        self.model.session_data = json.dumps(self._load())
        self.model.save(update_fields=["session_data"])
        self.modified = False

    def flush(self):
        self._session_cache = {}
        self.model.delete()
        self.model = Session.create()
        self.session_key = self.model.session_key
        self.modified = True

    def cycle_key(self):
        old_data = self._load().copy()
        self.model.delete()
        self.model = Session.create()
        self.session_key = self.model.session_key
        self._session_cache = old_data
        self.modified = True
