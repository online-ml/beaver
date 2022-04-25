import pathlib
import beaver

if (existing_sqlite_file := pathlib.Path(__file__).parent / "taxis.sqlite").exists():
    existing_sqlite_file.unlink()

app = beaver.App(
    model_store=beaver.model_store.ShelveModelStore(
        path=pathlib.Path.home() / "Downloads"
    ),
    data_store=beaver.data_store.SQLDataStore(url="sqlite:///taxis.sqlite"),
)
app.build()
