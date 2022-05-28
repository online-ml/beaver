import beaver

dam = beaver.Dam(
    model_store=beaver.model_store.ShelveModelStore("~/store"),
    data_store=beaver.data_store.SQLDataStore("sqlite:///beaver.sqlite"),
)
dam.build()
