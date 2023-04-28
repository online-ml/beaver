from pprint import pprint
import beaver_sdk
from sklearn import datasets
from sklearn import ensemble

sdk = beaver_sdk.Instance(host="http://127.0.0.1:8000")

# Create a project

sdk.message_bus.create(name="sqlite", protocol="SQLITE", url="message_bus.db")
sdk.stream_processor.create(name="sqlite", protocol="SQLITE", url="message_bus.db")
sdk.job_runner.create(name="synchronous", protocol="SYNCHRONOUS")

project = sdk.project.create(
    name="batch_trees",
    task="BINARY_CLASSIFICATION",
    message_bus_name="sqlite",
    stream_processor_name="sqlite",
    job_runner_name="synchronous",
)

# Grab some data

X, y = datasets.fetch_kddcup99(
    subset="smtp", as_frame=True, return_X_y=True, shuffle=True
)
y = y != b"normal."

# Split into train and test

X_train, X_test = X[:-1000], X[-1000:]
y_train, y_test = y[:-1000], y[-1000:]

# Train models locally

models = [
    ensemble.RandomForestClassifier(max_depth=5, n_estimators=10),
    ensemble.GradientBoostingClassifier(max_depth=5, n_estimators=10),
]
for model in models:
    model.fit(X_train, y_train)

# Send in test set data

mb = sdk.message_bus("sqlite")
for i, (x, y) in enumerate(zip(X_test.to_dict(orient="records"), y_test)):
    mb.send(topic="features", key=i, value=x)
    mb.send(topic="targets", key=i, value=y)


# Create feature set and target

project.target.set(
    query="SELECT key, created_at, value FROM messages WHERE topic = 'targets'",
    key_field="key",
    ts_field="created_at",
    value_field="value",
)
project.feature_set.create(
    name="features",
    query="SELECT key, created_at, value FROM messages WHERE topic = 'features'",
    key_field="key",
    ts_field="created_at",
    value_field="value",
)

# Create experiments

experiments = [
    project.experiment.create(
        name=f"experiment_{i}",
        feature_set_name="features",
        model=model,
        start_from_top=True,
    )
    for i, model in enumerate(models)
]

pprint(project.state())
