import pydantic

import ocean


class App(pydantic.BaseSettings):
    model_store: ocean.model_store.ModelStore

    @property
    def http_server(self):
        from ocean.api.server import api, Settings, get_settings

        def get_settings_override():
            return Settings(ocean_app=self)

        api.dependency_overrides[get_settings] = get_settings_override

        return api
