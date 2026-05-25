import { generateData } from './generateData.js';
import { Worker } from 'node:worker_threads';
import os from 'node:os';

const N = parseInt(process.env.N || '100000', 10);
const workers = parseInt(process.env.WORKERS || os.cpus().length.toString(), 10);

const data = generateData(N);
const sliceSize = Math.ceil(N / workers);

async function runParallel() {
  const start = Date.now();
  const tasks = [];
  for (let i = 0; i < workers; i++) {
    const startIdx = i * sliceSize;
    const endIdx = Math.min(startIdx + sliceSize, N);
    const slice = data.slice(startIdx, endIdx);
    tasks.push(new Promise((resolve, reject) => {
      const worker = new Worker(new URL('./worker.js', import.meta.url), {
        workerData: slice
      });
      worker.on('message', (msg) => resolve(msg));
      worker.on('error', reject);
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
    mode: 'parallel',
    N,
    workers,
    primes: totalCount,
    sum: totalSum,
    time: elapsedSec
  }));
}

runParallel().catch((err) => {
  console.error(err);
});
