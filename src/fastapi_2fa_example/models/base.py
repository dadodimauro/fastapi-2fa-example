from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

my_metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class Model(DeclarativeBase):
    __abstract__ = True

    metadata = my_metadata

    def to_dict(self) -> dict[str, object]:
        """
        Convert the model instance to a dictionary.
        This method is used for serialization purposes.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class TimestampedModel(Model):
    __abstract__ = True

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=utc_now, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        onupdate=utc_now,
        index=True,
    )
