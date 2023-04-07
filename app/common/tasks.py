"""Модуль с кастомными классами задач Celery"""


import celery

from sqlalchemy.orm import Session
from app.db import get_session_pool


class DatabaseTask(celery.Task):
    _session = None
    _session_pool = None

    def after_return(self, *args, **kwargs):
        if self._session is not None:
            self._session.close()

    @property
    def session_pool(self):
        if self._session_pool is None:
            self._session_pool = get_session_pool(self._app.conf.get('db_url'))
        return self._session_pool

    @property
    def session(self):
        if self._session is None:
            self._session = self.session_pool()
        return self._session
