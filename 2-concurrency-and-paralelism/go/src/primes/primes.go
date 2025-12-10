package primes

func IsPrime(n int) bool {
	if n < 2 {
		return false
	}
	if n == 2 {
		return true
	}
	if n%2 == 0 {
		return false
	}
	for i := 3; i*i <= n; i += 2 {
		if n%i == 0 {
			return false
		}
	}
	return true
}

// GenerateData gera um slice de inteiros determinísticos usando LCG.
func GenerateData(count int) []int {
	data := make([]int, count)
	var seed uint32 = 42
	for i := 0; i < count; i++ {
		seed = seed*1664525 + 1013904223
		data[i] = 100000 + int(seed%900000)
	}
	return data
}
