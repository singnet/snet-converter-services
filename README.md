# Snet Converter Services

Install the dependencies and devDependencies and start the service locally.

```sh
npm install -g serverless # Install serverless
npm install
```

config database from `config/database.ts`

### Database migrations

```sh
npm run migration:run
```

### Start the service

```sh
npm run start
```

### Database automigrations

```sh
npm run migration:generate "<Name>"
```

## Requirements

| Language     | Download                        |
| ------------ | ------------------------------- |
| Node JS 14.X | https://nodejs.org/en/download/ |
