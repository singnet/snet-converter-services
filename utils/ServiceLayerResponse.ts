export const expiredTokenMessage = 'EXPIRED_TOKEN';
export const serviceResponse = (
  message: any = null,
  result: any = null,
  status: boolean = false,
) => {
  let statusCode = 400;

  if (status) {
    statusCode = 200;
  }

  if (message === null) {
    if (statusCode === 200) {
      message = 'OK';
    } else {
      message = 'FAILURE';
    }
  }
  if (message === expiredTokenMessage) {
    statusCode = 403;
  }

  return { result, statusCode, message };
};
