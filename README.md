# Exegesis

A web app which annotates the SVG files exported from the Sketch app.

### How to install?

  - Clone this repo
  - Install the PIP packages
      ```sh
    $ cd annotator
    $ pip install - r requirements.txt
    ```
  - Install PostgreSQL, set up DB and User  
      ```sh
    $ sudo -u postgres psql
    postgres=# create database exegesis;
    postgres=# create user ex_user with password 'exegesis';
    postgres=# grant all privileges on database "exegesis" to ex_user;
    alter database exegesis owner to ex_user;
    ```
  - Create a config file similar to annotator/annotator/config_sampl.py, replacing SOCIAL_AUTH_GOOGLE_OAUTH2_KEY and SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET with correct values
  - Start the server
      ```sh
    $ cd annotator
    $ python manage.py runserver
    ```
  - Sample SVG files in annotator/exegesis/templates/sample_svg/ can be used for testing purpose.
