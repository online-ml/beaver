import dill
import pydantic

import beaver


class App(pydantic.BaseSettings):
    model_store: beaver.model_store.ModelStore
    data_store: beaver.data_store.DataStore

    def build(self):
        self.model_store.build()
        self.data_store.build()

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

    def make_prediction(self, event: dict, model_name: str):
        model_envelope = self.model_store.get(model_name)
        model = dill.loads(model_envelope.model_bytes)
        event = beaver.Event(content=event)
        prediction = beaver.Prediction(
            content=model.predict(event.content.copy()),
            model_name=model_name,
            loop_id=event.loop_id,
        )
        self.data_store.store_event(event)
        self.data_store.store_prediction(prediction)
        return prediction

    def store_label(self, loop_id: str, label: beaver.types.Label):
        self.data_store.store_label(beaver.Label(content=label, loop_id=loop_id))
