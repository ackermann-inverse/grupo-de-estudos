// Worker que recebe um array de números e retorna quantos são primos e sua soma
import { parentPort, workerData } from 'node:worker_threads';

function isPrime(n) {
  if (n < 2) return false;
  if (n === 2) return true;
  if (n % 2 === 0) return false;
  const limit = Math.floor(Math.sqrt(n));
  for (let i = 3; i <= limit; i += 2) {
    if (n % i === 0) return false;
  }
  return true;
}

function processSlice(slice) {
  let count = 0;
  let sum = 0;
  for (const v of slice) {
    if (isPrime(v)) {
      count++;
      sum += v;
    }
  }
  return { count, sum };
}

const result = processSlice(workerData);
parentPort.postMessage(result);
