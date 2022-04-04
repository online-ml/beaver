import pathlib
import ocean

app = ocean.App(
    model_store=ocean.model_store.ShelveModelStore(
        path=pathlib.Path.home() / "Downloads"
    )
)
