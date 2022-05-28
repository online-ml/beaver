import beaver

dam = beaver.Dam(
    model_store=beaver.model_store.ShelveModelStore("~Downloads"),
    data_store=beaver.data_store.SQLDataStore("sqlite:///db.sqlite"),
)
dam.build()
