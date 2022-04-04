import pathlib
import beaver

app = beaver.App(
    model_store=beaver.model_store.ShelveModelStore(
        path=pathlib.Path.home() / "Downloads"
    )
)
