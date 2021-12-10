import { CreateDateColumn, UpdateDateColumn } from 'typeorm';

export class DateEntity {
  @CreateDateColumn({ type: 'timestamp' })
  createdAt?: Date;

  @UpdateDateColumn({ type: 'timestamp' })
  updatedAt?: Date;
}
