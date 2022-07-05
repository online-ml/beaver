Much of Beaver's design can be traced back to some of Max Halford's [talks](https://maxhalford.github.io/links/#talks), with [this one](https://www.youtube.com/watch?v=nzFTmJnIakk&list=PLIU25-FciwNaz5PqWPiHmPCMOFYoEsJ8c&index=5) in particular.

The central object is the `Dam`. It holds all the components necessary to perform online machine learning. For instance, a `data_store` which will store predictions, features, and labels has to be chosen, while `model_store` has to be picked to store models. This is where Beaver is generic: you can use whatever model and data store you want, as long as they satisfy the necessary interfaces.

A strong design principle is that Beaver is technology agnostic. If you want to store data in Redis, or use MLFlow as a model store, then so be it. The only strong decision is that Beaver is written in Python.

Once instantiated, the `Dam` is supposed to be run on a server. There are then multiple ways to interact with it. The most common way would be to start an HTTP server, and interact with said server from a client. That is one way to use Beaver. But you can also directly use the `Dam` you instantiated, for instance if you don't need to have a client/server separation. This might be the case if you're deploying a model on an embedded device with no internet connection.

Beaver is the latest of an ongoing trial and error process.

## More reading

- https://vadosware.io/post/building-an-interface-with-one-implementation-is-unquestionably-right/
- https://www.ethanrosenthal.com/2022/05/10/database-bundling/
