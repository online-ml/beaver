import beaver

dam = beaver.Dam(
    model_store=beaver.model_store.ShelveModelStore("~/model_store"),
    data_store=beaver.data_store.SQLDataStore("sqlite:///beaver.sqlite"),
    training_regimes=[beaver.training.Regime.ASAP, beaver.training.Regime.MANUAL],
)
dam.build()
