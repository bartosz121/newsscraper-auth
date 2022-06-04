
# Newsscraper auth

Auth service for [newsscraper-frontend](https://github.com/bartosz121/newsscraper-frontend) using [SuperTokens](https://supertokens.com/)

## API

Docs for supertokens `EmailPassword` recipe available [here](https://app.swaggerhub.com/apis/supertokens/CDI/2.14.0#/) (signin/signup/signout)

---

#### Change password

```bash
  POST /change_password
```

#### Change email

```bash
  POST /change_email
```

#### Get user list of bookmarks

```bash
  GET /bookmark
```

#### Add bookmark

```bash
  POST /bookmark
```

#### Delete bookmark

```bash
  DELETE /bookmark
```

#### Check if article is bookmarked by user

```bash
  POST /bookmark/check
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file.

Get your own `APP_NAME`, `API_DOMAIN`, `API_KEY`, `WEBSITE_DOMAIN` and `CONNECTION_URI` from [supertokens](https://supertokens.com)

If you are running this together with [newsscraper-frontend](https://github.com/bartosz121/newsscraper-frontend) - `WEBSITE_DOMAIN` should point to the frontend url

```bash
APP_NAME=
API_DOMAIN=
WEBSITE_DOMAIN=
CONNECTION_URI=
API_KEY=
MONGO_URI=
MONGO_DB_NAME=
NEWSSCRAPER_API_URL=
```

## Run Locally

Clone the project

```bash
  git clone https://github.com/bartosz121/newsscraper-auth
```

Go to the project directory

```bash
  cd newsscraper-auth
```

Make sure you created .env file

Build and run the container

```bash
  docker build -t "newsscraper_auth" .

  docker run -d --name "newsscraper_auth" -p 8080:8080 newsscraper_auth
```

Test!

```bash
  curl http://localhost:8080
```
