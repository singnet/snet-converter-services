import { Column, Entity } from "typeorm";
import { UUIDPrimaryKey } from "../helpers/UUIDPrimaryKeyEntity";

export enum Blockchain {
  ETHEREUM = "ETHEREUM",
  CARDANO = "CARDANO",
}

@Entity("token_addresses")
export class TokenAddress extends UUIDPrimaryKey {
  @Column({ type: "varchar", length: 40, nullable: false })
  blockchain: Blockchain;

  @Column({ type: "varchar", length: 60, nullable: false })
  token_address: string;

  @Column({ type: "varchar", length: 20, nullable: false })
  symbol: string;

  @Column({ type: "varchar", length: 60, nullable: false })
  contract: string;

  @Column({ type: "bit", nullable: false, default: true })
  is_active: boolean;
}
