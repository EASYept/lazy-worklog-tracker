from __future__ import annotations


from lazy_worklog_tracker.app import WorklogTracker
from lazy_worklog_tracker.config import Container


if __name__ == "__main__":
    conteiner = Container()
    app = WorklogTracker(conteiner.repo())
    app.run()
