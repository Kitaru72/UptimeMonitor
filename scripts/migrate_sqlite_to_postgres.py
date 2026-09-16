from pathlib import Path

from sqlalchemy import (
    MetaData,
    Table,
    create_engine,
    func,
    select,
    text,
)

from app.database import engine as target_engine
from app.models.check import CheckModel
from app.models.monitor import MonitorModel


BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_PATH = BASE_DIR / "uptime_monitor.db"

source_engine = create_engine(
    f"sqlite:///{SQLITE_PATH.as_posix()}"
)

source_metadata = MetaData()

source_monitors = Table(
    "monitors",
    source_metadata,
    autoload_with=source_engine,
)

source_checks = Table(
    "checks",
    source_metadata,
    autoload_with=source_engine,
)


def read_sqlite_data():
    with source_engine.connect() as connection:
        monitors = [
            dict(row._mapping)
            for row in connection.execute(select(source_monitors))
        ]

        checks = [
            dict(row._mapping)
            for row in connection.execute(select(source_checks))
        ]

    return monitors, checks


def write_postgresql_data(monitors, checks):
    target_monitors = MonitorModel.__table__
    target_checks = CheckModel.__table__

    with target_engine.begin() as connection:
        monitor_count = connection.scalar(
            select(func.count()).select_from(target_monitors)
        )
        check_count = connection.scalar(
            select(func.count()).select_from(target_checks)
        )

        if monitor_count != 0 or check_count != 0:
            raise RuntimeError(
                "PostgreSQL tables are not empty. Migration cancelled."
            )

        connection.execute(
            target_monitors.insert(),
            monitors,
        )

        connection.execute(
            target_checks.insert(),
            checks,
        )

        connection.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence('monitors', 'id'),
                    MAX(id)
                )
                FROM monitors
                """
            )
        )

        connection.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence('checks', 'id'),
                    MAX(id)
                )
                FROM checks
                """
            )
        )


if __name__ == "__main__":
    monitors, checks = read_sqlite_data()

    print(f"Monitors found: {len(monitors)}")
    print(f"Checks found: {len(checks)}")

    write_postgresql_data(monitors, checks)

    print("Migration completed successfully.")