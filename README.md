
# Wire - Pub/Sub middleware for the *is* architecture (python implementation)


## Installation & basic usage

1. Install the wire package using `pip` or `pipenv`:

```shell
  pip install --user is-wire
  pipenv install --user is-wire
```

## Development

### Tests

```shell
  # prepare environment
  pip install --user tox
  docker run -d --rm -p 5672:5672 -p 15672:15672 rabbitmq:3.7.6-management

  # run all the tests
  tox
```


