const LB_PER_KG = 2.20462
const IN_PER_CM = 0.393701

export function calculateBmi(weight, height, unit) {
  const w = Number(weight)
  const h = Number(height)
  if (!(w > 0) || !(h > 0)) return null

  const kg = unit === 'imperial' ? w / LB_PER_KG : w
  const m = (unit === 'imperial' ? h / IN_PER_CM : h) / 100
  return kg / (m * m)
}

export function getCategory(bmi) {
  if (bmi < 18.5) return 'Underweight'
  if (bmi < 25) return 'Normal weight'
  if (bmi < 30) return 'Overweight'
  return 'Obese'
}
