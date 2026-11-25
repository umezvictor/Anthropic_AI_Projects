import { useState } from 'react'
import { calculateBmi, getCategory } from './bmi.js'
import './BmiCalculator.css'

const UNITS = {
  metric: { weight: 'kg', height: 'cm' },
  imperial: { weight: 'lb', height: 'in' },
}

export default function BmiCalculator() {
  const [unit, setUnit] = useState('metric')
  const [weight, setWeight] = useState('')
  const [height, setHeight] = useState('')

  const bmi = calculateBmi(weight, height, unit)
  const hasInput = weight !== '' || height !== ''

  return (
    <main className="bmi">
      <h1>BMI Calculator</h1>

      <div className="bmi-units" role="group" aria-label="Units">
        {Object.keys(UNITS).map((u) => (
          <button
            key={u}
            type="button"
            aria-pressed={unit === u}
            onClick={() => setUnit(u)}
          >
            {u === 'metric' ? 'Metric' : 'Imperial'}
          </button>
        ))}
      </div>

      <form className="bmi-form" onSubmit={(e) => e.preventDefault()}>
        <label>
          Weight ({UNITS[unit].weight})
          <input
            type="number"
            inputMode="decimal"
            min="0"
            step="any"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
          />
        </label>
        <label>
          Height ({UNITS[unit].height})
          <input
            type="number"
            inputMode="decimal"
            min="0"
            step="any"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
          />
        </label>
        <button
          type="button"
          className="bmi-reset"
          onClick={() => {
            setWeight('')
            setHeight('')
          }}
        >
          Reset
        </button>
      </form>

      <section className="bmi-result" aria-live="polite">
        {bmi !== null ? (
          <>
            <p className="bmi-value">{bmi.toFixed(1)}</p>
            <p>{getCategory(bmi)}</p>
          </>
        ) : (
          <p>
            {hasInput
              ? 'Enter a weight and height greater than zero.'
              : 'Enter your weight and height to see your BMI.'}
          </p>
        )}
      </section>
    </main>
  )
}
