api
===

The Gruntlr Backend API

In order to run the api webapp, you must set at least the following config variables: SECRET_KEY, LINKEDIN_KEY, LINKEDIN_SECRET.
You may do this either in gruntlr.py, or in a config file referenced by the environment variable GRUNTLR_SETTINGS as so:

```
export GRUNTLR_SETTINGS=/path/to/gruntlrio/api/settings.cfg
```

You must also configure your LinkedIn developer account to accept an auth redirect of the form

```
http://localhost:5000/authorize/callback
```

and update the LINKEDIN_CALLBACK config variable as necessary.