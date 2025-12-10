import { generateData } from './generateData.js';
import { isPrime } from './isPrime.js';

const N = parseInt(process.env.N || '100000', 10);

const data = generateData(N);

let count = 0;
let sum = 0;
const start = Date.now();
for (const value of data) {
  if (isPrime(value)) {
    count++;
    sum += value;
  }
}
const elapsedSec = (Date.now() - start) / 1000;

console.log(JSON.stringify({
  mode: 'sequential',
  N,
  primes: count,
  sum,
  time: elapsedSec
}));
