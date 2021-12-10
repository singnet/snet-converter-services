import { validateOrReject } from 'class-validator';

const validationOptions = {
  disableErrorMessages: false,
  skipMissingProperties: true,
  whitelist: true,
  transform: true,
  forbidUnknownValues: true,
  stopAtFirstError: true,
};

export const validate = async (inputs: any): Promise<unknown> => {
  try {
    return await validateOrReject(inputs, validationOptions);
  } catch (err) {
    const [errors] = err.map((e: { constraints: any[] }) => {
      return e.constraints;
    });

    for (const key in errors) {
      if (Object.prototype.hasOwnProperty.call(errors, key)) {
        throw errors[key];
      }
    }
  }
};
