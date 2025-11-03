from __future__ import annotations


from lazy_worklog_tracker.config import Container


if __name__ == "__main__":
    conteiner = Container()
    app = conteiner.app()
    app.run()
