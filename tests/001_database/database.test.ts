import { assert } from "chai";
import { Connection, createConnection, getConnectionManager } from "typeorm";

import { Database as DbConfig } from "./database.mock";

describe("Database Connection", () => {
  const CONNECTION_NAME = "test";
  let connection: Connection;
  const connectionManager = getConnectionManager();

  it("checks db connection has established", async function () {
    const connectionOptions: any = {
      name: CONNECTION_NAME,
      type: DbConfig.type,
      host: DbConfig.host,
      port: DbConfig.port,
      username: DbConfig.user,
      password: DbConfig.password,
      database: DbConfig.database,
      keepConnectionAlive: true,
      entities: [],
      logging: true,
    };

    connection = await createConnection(connectionOptions);

    connection = connectionManager.get(CONNECTION_NAME);

    assert.isTrue(connection.isConnected);
  });

  it("checks db connection has closed", async function () {
    await connection.close();
    assert.isFalse(connection.isConnected);
  });
});
