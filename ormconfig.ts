import { DbConfig as Database } from "./config/database";

const config = {
  type: Database.type,
  host: Database.host,
  port: Number(Database.port),
  username: Database.user,
  password: Database.password,
  database: Database.database,
  synchronize: false,
  logging: true,
  entities: ["database/entities/*.ts"],
  migrations: ["database/migrations/**/*.ts"],
  subscribers: ["database/subscribers/**/*.ts"],
  cli: {
    entitiesDir: "database/entities",
    migrationsDir: "database/migrations",
    subscribersDir: "database/subscribers",
  },
};

export = config;
