from api import db
from api import sources


if __name__ == "__main__":

    db.init_db()

    with db.session() as session:
        default_source = sources.Source(
            name="Default source", protocol="Redpanda", host="broker", port="9092"
        )
        session.add(default_source)
        session.commit()
