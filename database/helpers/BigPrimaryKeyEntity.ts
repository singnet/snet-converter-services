import { PrimaryGeneratedColumn } from 'typeorm';

import { DateEntity } from './DateEntity';

export class BigPrimary extends DateEntity {
  @PrimaryGeneratedColumn({ type: 'bigint' })
  id?: number;
}
