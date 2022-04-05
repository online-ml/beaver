import dill
import pydantic

import beaver


class App(pydantic.BaseSettings):
    model_store: beaver.model_store.ModelStore

    @property
    def http_server(self):
        from beaver.api.server import api, Settings, get_settings

        def get_settings_override():
            return Settings(app=self)

        api.dependency_overrides[get_settings] = get_settings_override

        return api

    def store_model(self, name, model):

        if self.model_store.get(name):
            raise ValueError(f"'{name}' already exists")

        model_envelope = beaver.ModelEnvelope(
            name=name,
            is_featurizer=isinstance(model, beaver.Featurizer),
            is_learner=isinstance(model, beaver.Learner),
            model_bytes=dill.dumps(model),
        )
        self.model_store.store(model_envelope)
