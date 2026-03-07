import React from 'react'

const noise = (seed: number) => {
  const value = Math.sin(seed * 12.9898) * 43758.5453
  return value - Math.floor(value)
}

type MeteorSeed = {
  id: number
  x: number
  y: number
  length: number
  duration: number
  delay: number
}

type StarSeed = {
  id: number
  x: number
  y: number
  size: number
  alpha: number
  twinkle: number
  delay: number
}

const starSeeds: StarSeed[] = Array.from({ length: 92 }, (_, index) => {
  const x = noise(index + 1) * 100
  const y = noise(index + 101) * 100
  const size = 1 + noise(index + 25) * 2.2
  const alpha = 0.2 + noise(index + 43) * 0.62
  const twinkle = 4 + noise(index + 66) * 8
  const delay = -noise(index + 88) * 10

  return { id: index, x, y, size, alpha, twinkle, delay }
})

const meteorSeeds: MeteorSeed[] = Array.from({ length: 14 }, (_, index) => {
  const x = 10 + noise(index + 9) * 86
  const y = 2 + noise(index + 22) * 44
  const length = 150 + Math.round(noise(index + 35) * 180)
  const duration = 5.4 + noise(index + 48) * 6.8
  const delay = -noise(index + 61) * 14

  return { id: index, x, y, length, duration, delay }
})

const MeteorField: React.FC = () => {
  return (
    <div className="meteor-layer" aria-hidden="true">
      {starSeeds.map((star) => (
        <span
          key={`star-${star.id}`}
          className="star"
          style={
            {
              left: `${star.x}%`,
              top: `${star.y}%`,
              '--size': `${star.size}px`,
              '--alpha': `${star.alpha}`,
              '--twinkle': `${star.twinkle}s`,
              '--delay': `${star.delay}s`,
            } as React.CSSProperties
          }
        />
      ))}
      {meteorSeeds.map((meteor) => (
        <span
          key={`meteor-${meteor.id}`}
          className="meteor"
          style={
            {
              left: `${meteor.x}%`,
              top: `${meteor.y}%`,
              '--length': `${meteor.length}px`,
              '--dur': `${meteor.duration}s`,
              '--delay': `${meteor.delay}s`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  )
}

export default MeteorField
