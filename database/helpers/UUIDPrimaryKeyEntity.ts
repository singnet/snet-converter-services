import { PrimaryGeneratedColumn } from 'typeorm';
import { DateEntity } from './DateEntity';

export class UUIDPrimaryKey extends DateEntity {
  @PrimaryGeneratedColumn('uuid')
  id: String;
}
