<h1>🦫 Beaver • MLOps for (online) machine learning</h1>

<p>

<a href=>

<!-- Tests -->
<a href="https://github.com/online-ml/beaver/actions/workflows/unit-tests.yml">
<img src="https://github.com/online-ml/beaver/actions/workflows/unit-tests.yml/badge.svg" alt="tests">
</a>

<!-- Code quality -->
<a href="https://github.com/online-ml/beaver/actions/workflows/code-quality.yml">
<img src="https://github.com/online-ml/beaver/actions/workflows/code-quality.yml/badge.svg" alt="code_quality">
</a>

<!-- Mypy -->
<a href="http://mypy-lang.org/">
<img src="http://www.mypy-lang.org/static/mypy_badge.svg" alt="mypy">
</a>
<!-- License -->
<a href="https://opensource.org/licenses/BSD-3-Clause">
<img src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square" alt="bsd_3_license">
</a>

</p>

[![Discord](https://dcbadge.vercel.app/api/server/qNmrKEZMAn)](https://discord.gg/qNmrKEZMAn)


<div align="center" >
  <img src="https://user-images.githubusercontent.com/8095957/202878607-9fa71045-6379-436e-9da9-41209f8b39c2.png" width="25%" align="right" />
</div>

Beaver is...

✔ [*The whole package*](https://www.youtube.com/watch?v=nzFTmJnIakk&list=PLIU25-FciwNaz5PqWPiHmPCMOFYoEsJ8c&index=5) • it's a framework to develop, deploy, and maintain machine learning models. And that includes feature engineering.

✔ *No fuss* • there's an SDK to do stuff, and a UI to see stuff.

✔ *Online-first* • it is designed for online machine learning models, while also supporting batch models.

✔ *Opinionated* • it encourages you to [process data with SQL](https://www.ethanrosenthal.com/2022/05/10/database-bundling/) and define models in Python.

✔ [*Interfaces all the way down*](https://vadosware.io/post/building-an-interface-with-one-implementation-is-unquestionably-right/) • you can plug in your existing message broker, stream processor, model store, etc. At least, that's the idea.

✔ *Batteries included* • default infrastructure and monitoring are provided if needed.

## 🤱 Getting started

There is a [pre-built image](https://ghcr.io/online-ml/beaver) you can pull and run 🐳

```sh
docker pull ghcr.io/online-ml/beaver:latest
docker run ghcr.io/online-ml/beaver
```

You can also build the provided [`docker-compose.yaml`](docker-compose.yaml) yourself:

```sh
git clone git@github.com:online-ml/beaver.git
cd beaver
docker-compose up
```

Go to [http://localhost:8501](http://localhost:8501/) to access the user interface.

This is all you need to run Beaver. Check out the examples to see how to use it.

## 👀 Examples

- [🚕 Taxis](examples/taxis)
- [🌳 Batch gradient boosting vs. random forest](examples/batch-trees)

## 📝 License

Beaver is free and open-source software licensed under the [3-clause BSD license](LICENSE).
