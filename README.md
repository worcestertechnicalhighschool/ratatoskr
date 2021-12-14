# Ratatoskr: Worcester Tech's conference scheduling system

> _In Norse mythology, Ratatoskr is a squirrel who runs up and down the world tree Yggdrasil to carry messages between the eagle perched atop Yggdrasil, and the serpent Níðhöggr._\
> \- Wikipedia

# Running in a development environment

## 1. Install pipenv

### Windows

```shell
$ pip3 install --user pipenv
```

Note: If there is a warning in the output while installing that says that a directory isn't in your PATH, [add that directory to your PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)

Python on Windows tends to hairball PATH _very_ frequently

### Linux

Install `python-pipenv` from your preferred package manager

## 2. Clone the repository to your preferred directory and run

```shell
$ pipenv install
```

## 3. To start the server, run

```shell
$ pipenv shell
$ python manage.py migrate
$ python manage.py runserver
```
