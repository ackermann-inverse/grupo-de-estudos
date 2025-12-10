/**
 * Gera um array determinístico de números usando um LCG.
 * A mesma fórmula é usada em todas as linguagens para comparabilidade.
 *
 * @param {number} count Número de elementos a gerar
 * @returns {number[]}
 */
export function generateData(count) {
  const data = new Array(count);
  let seed = 42;
  for (let i = 0; i < count; i++) {
    // aplica LCG com wrap para 32 bits sem sinal.
    seed = (seed * 1664525 + 1013904223) >>> 0;
    // valores no intervalo [100000, 999999]
    data[i] = 100000 + (seed % 900000);
  }
  return data;
}
