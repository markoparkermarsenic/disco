# Installation

You can use the `makefile` provided to quickly run common build commands; including running a debug version of the api

```bash
make api
```

Will launch the api.

You can use the .env file provided for convenience or make changes as necessary

## Note on default data 
When the server launches it will create a default user dev and admin and the default plans, basic, premium and enterprise.
The admin password is specified in .env

## DRF endpoints
The following endpoints can be used to create their respective objects!
http://localhost:8000/subscribers/
http://localhost:8000/plans/
http://localhost:8000/users/

## POSTING

To post images to the server you can do the following:
If you don't want to create a user you can set the `user` in header to `dev`

```bash
curl -F "image=/path/to/image.jpg" -H "user: <username>" localhost:8000/upload/
```

This will return a json object containing the links to the posted image

To pass an expiry you can do 
```bash
curl -F "image=/path/to/image.jpg" -H "user: <username>" -H "expires:500" localhost:8000/upload/
```
if expiry is valid for that user it will add an expiry to the link; otherwise it will not expire

## List images

```bash
curl -H "user: dev" localhost:8000/list_images/dev
```

this will return a json object of the form {'username':[{"id":<imageid>, "created":<timestamp>}]}

## Tests
tests can be run by attaching to the server container

```bash 
docker exec -it disco-server-1 /bin/bash
```

then running the tests

```bash
python manage.py test image
```

## Note
an image img.jpg is provided for your convenience


## Troubleshooting
you might have to run: 

```bash
chmod +x app/run.sh
```
if you get shim error on build 
