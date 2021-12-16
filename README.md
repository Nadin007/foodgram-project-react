![yamdb_workflow](https://github.com/Nadin007/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)

# About "Grocery Assistant" project

Application "Grocery Assistant": a site where users will publish recipes, add other people's recipes to favorites and subscribe to publications of other authors. The "Shopping List" service allows you to create a list of products that you need to buy to prepare the selected dishes.

## Capabilities

- Unauthorized users can do
  - Create an account .
  - View recipes on the main page.
  - Retrieve a particular recipe-page.
  - View user pages.
  - Filter recipes by tags.

- Authorized users can do
  - Log in to the system using your username and password.
  - Log out from the system.
  - Update your password.
  - Create/edit/delete your recipe.
  - View recipes on the main page.
  - View user pages.
  - Retrieve a particular recipe-page.
  - Filter recipes by tags.
  - Work with your personal favorite list: add recipes to it or delete them, view your favorite page.
  - Work with your personal cart list: add/delete any recipes to it, download a file with the amount of required ingredients for recipes from the cart list.
  - Subscribe and unsubscribe to recipe authors' publications, view your subscription page. 

- Administrator can do
  - Administrator has all the rights of an authorized user.
  - Change password of any user.
  - Create/block/delete any user accounts.
  - Edit/delete any recipes.
  - Add/delete/edit ingredients.
  - Add/delete/edit tags.

## Technology

Uses a number of open source projects to work properly:

- [Django 3.2.9] - high-level Python web framework.
- [Python 3.9]
- PostgreSQL database.

And of course "Grocery Assistant" itself is open source in [repository][Nadin007/foodgram-project-react]
on GitHub.

## Installing the app

Clone and switch to the repository using the terminal:

```sh
git clone git@github.com:Nadin007/foodgram-project-react.git
```

```sh
cd backend/
```

### Running foodgram-project-react in development mode:

- Create and activate a virtual environment

```sh
python3 -m venv env

```
```sh
source venv/bin/activate

```
- Install dependencies from the requirements.txt file

```sh
pip install -r requirements.txt
```
- In the folder with the manage.py file, run the command:

```sh
cd recipe_backend/
```

```sh
python3 manage.py runserver
````

### Launch foodgram-project-react in [Docker]:

- Run the command:

```sh
cd ../../infra
```

- Launch a docker-compose:

```sh
docker-compose up -d --build
```
- Run migrations on the database:

```sh
docker-compose exec web python manage.py migrate --noinput
```
- Create superuser:

```sh
docker-compose exec web python manage.py createsuperuser
```
- Collect static files:

```sh
docker-compose exec web python manage.py collectstatic --no-input
```
- The project is available at:

`http://localhost/recipes`

## .env filling instructions

- Create a .env file with environment variables for working with the database in the infra/ directory:

```sh
touch .env
```
- Paste the variable environment data into the file:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

-  To generate a new private key, run the following command in a terminal:

```sh
python3 manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

- Copy the received key and paste it into the .env folder:

```sh
...

SECRET_KEY =полученный_ключ
```

## About the program for downloading CSV files

The file names have to match the names of the application models during importing data from CSV files into the database.You can use both uppercase and lowercase letters in filenames. Also make sure that the ForeignKey column names in the CSV files are named according to the principle <id_field_name> (example genre_id). All CSV files have to be uploaded to the directory: ../../data.

## Working with CSV file loader

In the folder with the manage.py file, run the command:

```sh
python3 manage.py load-csv ../../data

```

## License type

MIT


   [Django 3.2.9]: <https://www.djangoproject.com/download/>
   [Python 3.9]: <https://www.python.org/downloads/release/python-390/>
   [Docker]: <https://docs.docker.com/get-docker/>
   [Nadin007/foodgram-project-react]: https://github.com/Nadin007/foodgram-project-react
   
The project is available at: https://yatube-shareland.tk

Author:
Tumareva Nadia