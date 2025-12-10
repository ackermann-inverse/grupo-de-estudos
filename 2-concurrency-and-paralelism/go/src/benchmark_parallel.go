package main

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"strconv"
	"sync"
	"time"

	"concurrency-benchmark-go/src/primes"
)

type ResultadoPar struct {
	Mode    string  `json:"mode"`
	N       int     `json:"N"`
	Workers int     `json:"workers"`
	Primes  int     `json:"primes"`
	Sum     int     `json:"sum"`
	Time    float64 `json:"time"`
}

func main() {
	nStr := os.Getenv("N")
	if nStr == "" {
		nStr = "100000"
	}
	N, err := strconv.Atoi(nStr)
	if err != nil {
		fmt.Fprintln(os.Stderr, "valor inválido para N")
		os.Exit(1)
	}
	workersStr := os.Getenv("WORKERS")
	var workers int
	if workersStr == "" {
		workers = runtime.NumCPU()
	} else {
		w, err := strconv.Atoi(workersStr)
		if err != nil || w < 1 {
			workers = runtime.NumCPU()
		} else {
			workers = w
		}
	}

	// paralelismo real
	runtime.GOMAXPROCS(workers)

	data := primes.GenerateData(N)
	sliceSize := (N + workers - 1) / workers

	var wg sync.WaitGroup
	wg.Add(workers)
	counts := make([]int, workers)
	sums := make([]int, workers)

	start := time.Now()
	for i := 0; i < workers; i++ {
		i := i
		go func() {
			defer wg.Done()
			startIdx := i * sliceSize
			endIdx := startIdx + sliceSize
			if endIdx > N {
				endIdx = N
			}
			c := 0
			s := 0
			for _, v := range data[startIdx:endIdx] {
				if primes.IsPrime(v) {
					c++
					s += v
				}
			}
			counts[i] = c
			sums[i] = s
		}()
	}
	wg.Wait()
	totalCount := 0
	totalSum := 0
	for i := 0; i < workers; i++ {
		totalCount += counts[i]
		totalSum += sums[i]
	}
	elapsed := time.Since(start).Seconds()
	res := ResultadoPar{
		Mode:    "parallel-goroutines",
		N:       N,
		Workers: workers,
		Primes:  totalCount,
		Sum:     totalSum,
		Time:    elapsed,
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(res); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
}
