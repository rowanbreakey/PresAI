import { useState, useEffect } from 'react'
import CameraWrapper from './components/CameraWrapper'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <CameraWrapper />
    </div>
  )
}

export default App
