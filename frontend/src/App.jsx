import { useState, useEffect } from 'react'
import CameraWrapper from './components/CameraWrapper'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="">
      <CameraWrapper />
    </div>
  )
}

export default App
