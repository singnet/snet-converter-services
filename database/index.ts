import "reflect-metadata";

import {
  Connection,
  ConnectionManager,
  createConnection,
  EntityTarget,
  getConnectionManager,
} from "typeorm";

import { TokenAddress } from "./entities/TokenAddress";

export * from "typeorm";

const entities = [TokenAddress];

export class Database {
  private connectionManager: ConnectionManager;

  constructor() {
    this.connectionManager = getConnectionManager();
  }

  public async getRepo(entity: EntityTarget<any>) {
    return (await this.connect()).getRepository(entity);
  }

  public async connect(): Promise<Connection> {
    const CONNECTION_NAME = "default";

    let connection: Connection;

    if (this.connectionManager.has(CONNECTION_NAME)) {
      connection = this.connectionManager.get(CONNECTION_NAME);

      if (!connection.isConnected) {
        connection = await connection.connect();
      }
    } else {
      const migrationsDir = "./migrations";

      const connectionOptions: any = {
        type: process.env.DB_TYPE,
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        username: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        database: process.env.DB_NAME,
        keepConnectionAlive: true,
        synchronize: false,
        entities,
        logging: true,
        migrations: [`${migrationsDir}/*.js`],
        cli: {
          migrationsDir,
        },
      };

      connection = await createConnection(connectionOptions);
    }

    return connection;
  }
}
