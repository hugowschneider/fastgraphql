from datetime import datetime, date, time

from pydantic import BaseModel

from fastgraphql import FastGraphQL


class TestDateFormats:
    def test_default_date_types(self) -> None:
        time_format = "%H:%M:%S"
        date_format = "%Y-%m-%d"
        date_time_format = f"{date_format}T{time_format}%z"

        fast_graphql = FastGraphQL()

        assert fast_graphql.get_date_format() == date_format
        assert fast_graphql.get_time_format() == time_format
        assert fast_graphql.get_date_time_format() == date_time_format

    def test_set_date_format(self) -> None:

        date_format = "%d-%m-%Y"
        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            t_datetime: date

        d = date(year=2020, month=10, day=2)

        fast_graphql.set_date_format(date_format)

        assert fast_graphql.get_date_format() == date_format
        assert fast_graphql.schema.scalars["Date"].encoder
        assert fast_graphql.schema.scalars["Date"].encoder(d) == "02-10-2020"

    def test_set_time_format(self) -> None:
        time_format = "%H-%M-%S"

        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            t_datetime: time

        d = time(hour=9, minute=22, second=34)
        fast_graphql.set_time_format(time_format)

        assert fast_graphql.get_time_format() == time_format
        assert fast_graphql.schema.scalars["Time"].encoder
        assert fast_graphql.schema.scalars["Time"].encoder(d) == "09-22-34"

    def test_set_date_time_format(self) -> None:
        date_time_format = "%H:%M:%S D %Y-%m-%d"
        fast_graphql = FastGraphQL()

        @fast_graphql.type()
        class Model(BaseModel):
            t_datetime: datetime

        fast_graphql.set_date_time_format(date_time_format)

        d = datetime(year=2020, month=10, day=2, hour=9, minute=11, second=35)

        assert fast_graphql.get_date_time_format() == date_time_format
        assert fast_graphql.schema.scalars["DateTime"].encoder
        assert (
            fast_graphql.schema.scalars["DateTime"].encoder(d)
            == "09:11:35 D 2020-10-02"
        )

        fast_graphql = FastGraphQL()
        fast_graphql.set_date_time_format(date_time_format)

        assert fast_graphql.get_date_time_format() == date_time_format
