<h1>🦫 Beaver — MLOps for (online) machine learning</h1>

- [👋 Introduction](#-introduction)
- [🤱 Getting started](#-getting-started)
- [👐 Examples](#-examples)
- [🚀 Deployment](#-deployment)
- [📝 License](#-license)

## 👋 Introduction

<div align="center" >
  <img src="https://user-images.githubusercontent.com/8095957/202878607-9fa71045-6379-436e-9da9-41209f8b39c2.png" width="25%" align="right" />
</div>

Beaver is...

✨ The whole package: it's a framework to develop, deploy, and maintain machine learning models.

🍥 Online-first: it is designed for online machine learning models, while also supporting batch models.

☝️ [Opinionated](https://www.youtube.com/watch?v=nzFTmJnIakk&list=PLIU25-FciwNaz5PqWPiHmPCMOFYoEsJ8c&index=5): it encourages you to [process data in SQL](https://www.ethanrosenthal.com/2022/05/10/database-bundling/) and build models with Python.

🔋 Batteries included: it provides basic infrastructure and monitoring by default.

🐢 [Interfaces all the way down](https://vadosware.io/post/building-an-interface-with-one-implementation-is-unquestionably-right/): you can plug in your existing message bus, stream processor, model store, etc.

## 🤱 Getting started

The easiest way is to run the provided `docker-compose.yaml`.

```sh
git clone https://github.com/online-ml/beaver
cd beaver
docker-compose up
```

Go to [localhost:3000](http://localhost:3000/) to check out the UI. This is a read-only interface. Interacting with the system happens through an API.

```py
from river import linear_model

model = linear_model.LogisticRegression()

client = beaver.HTTPClient(host='http://127.0.0.1:3000')
client.models.upload('my_model', model)
```

## 👐 Examples

- [🚕 Taxis](examples/taxis)

## 🚀 Deployment

🚧

## 📝 License

Beaver is free and open-source software licensed under the [3-clause BSD license](LICENSE).
