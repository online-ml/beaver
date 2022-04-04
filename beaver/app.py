import pydantic

import beaver


class App(pydantic.BaseSettings):
    model_store: beaver.model_store.ModelStore

    @property
    def http_server(self):
        from beaver.api.server import api, Settings, get_settings

        def get_settings_override():
            return Settings(beaver_app=self)

        api.dependency_overrides[get_settings] = get_settings_override

        return api
