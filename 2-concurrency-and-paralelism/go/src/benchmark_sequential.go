package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"time"

	"concurrency-benchmark-go/src/primes"
)

type ResultadoSeq struct {
	Mode   string  `json:"mode"`
	N      int     `json:"N"`
	Primes int     `json:"primes"`
	Sum    int     `json:"sum"`
	Time   float64 `json:"time"`
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
	data := primes.GenerateData(N)
	count := 0
	total := 0
	start := time.Now()
	for _, v := range data {
		if primes.IsPrime(v) {
			count++
			total += v
		}
	}
	elapsed := time.Since(start).Seconds()
	res := ResultadoSeq{
		Mode:   "sequential",
		N:      N,
		Primes: count,
		Sum:    total,
		Time:   elapsed,
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(res); err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
}
