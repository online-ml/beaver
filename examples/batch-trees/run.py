import beaver_sdk

sdk = beaver_sdk.Instance(host="http://127.0.0.1:8000")

sdk.message_bus.create(name="sqlite", protocol="SQLITE", url="sqlite:///message_bus.db")
sdk.stream_processor.create(
    name="sqlite", protocol="SQLITE", url="sqlite:///message_bus.db"
)
sdk.job_runner.create(name="synchronous", protocol="SYNCHRONOUS")

project = sdk.project.create(
    name="batch-trees",
    task="BINARY_CLASSIFICATION",
    message_bus_name="sqlite",
    stream_processor_name="sqlite",
    job_runner_name="synchronous",
)
