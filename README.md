<h1>🦫 Beaver • MLOps for (online) machine learning</h1>

**🚧 The purpose of Beaver is to package [this](https://github.com/MaxHalford/taxi-demo-rp-mz-rv-rd-st) proof-of-concept. Beaver is not yet meant to be used seriously. Feel welcome to use it for inspiration and educative purposes though 🏗**

<div align="center" >
  <img src="https://user-images.githubusercontent.com/8095957/202878607-9fa71045-6379-436e-9da9-41209f8b39c2.png" width="25%" align="right" />
</div>

## 👋 Introduction

Beaver is...

🍱 [*The whole package*](https://www.youtube.com/watch?v=nzFTmJnIakk&list=PLIU25-FciwNaz5PqWPiHmPCMOFYoEsJ8c&index=5) • it's a framework to develop, deploy, and maintain machine learning models. Including feature engineering.

🤟 *Straightforward* • there's a UI to see stuff, and an API to do stuff.

🍥 *Online-first* • it is designed for online machine learning models, while also supporting batch models.

☝️ *Opinionated* • it encourages you to [process data with SQL](https://www.ethanrosenthal.com/2022/05/10/database-bundling/) and build models in Python.

🔋 *Batteries included* • default infrastructure and monitoring are provided.

🐢 [*Interfaces all the way down*](https://vadosware.io/post/building-an-interface-with-one-implementation-is-unquestionably-right/) • you can plug in your existing message broker, stream processor, model store, etc. At least, that's the idea.

## 🤱 Getting started

The easiest way is to run the provided [`docker-compose.yaml`](docker-compose.yaml) 🐳

```sh
git clone https://github.com/online-ml/beaver
cd beaver
docker-compose up
```

Go to [http://localhost:3000](http://localhost:3000/) to check out the UI. This is a read-only interface. Interacting with the system happens through an API.

The recommended next step is to move on to the examples. That will give you an understanding of the workflow which Beaver enables.

## 👀 Examples

- [🚕 Taxis](examples/taxis)

## 🚀 Deployment

The `docker-compose.yaml` file is meant for development. You'll want to edit it if you're looking to deploy Beaver.

## 📝 License

Beaver is free and open-source software licensed under the [3-clause BSD license](LICENSE).
