import pathlib
import beaver

app = beaver.App(
    model_store=beaver.model_store.ShelveModelStore(
        path=pathlib.Path.home() / "Downloads"
    ),
    data_store=beaver.data_store.SQLDataStore(url="sqlite://"),
)
app.build()
