import { generateData } from './generateData.js';
import { isPrime } from './isPrime.js';

const N = parseInt(process.env.N || '100000', 10);
const workers = parseInt(process.env.WORKERS || '4', 10);

const data = generateData(N);
const sliceSize = Math.ceil(N / workers);

async function run() {
  const start = Date.now();
  const tasks = [];
  for (let i = 0; i < workers; i++) {
    const startIdx = i * sliceSize;
    const endIdx = Math.min(startIdx + sliceSize, N);
    const slice = data.slice(startIdx, endIdx);
    tasks.push(Promise.resolve().then(() => {
      let c = 0;
      let s = 0;
      for (const v of slice) {
        if (isPrime(v)) {
          c++;
          s += v;
        }
      }
      return { count: c, sum: s };
    }));
  }
  const results = await Promise.all(tasks);
  let totalCount = 0;
  let totalSum = 0;
  for (const res of results) {
    totalCount += res.count;
    totalSum += res.sum;
  }
  const elapsedSec = (Date.now() - start) / 1000;
  console.log(JSON.stringify({
    mode: 'concurrent',
    N,
    workers,
    primes: totalCount,
    sum: totalSum,
    time: elapsedSec
  }));
}

run().catch((err) => {
  console.error(err);
});
