import MainWrapper from './components/MainWrapper'
import LiveFeedback from './components/LiveFeedback'
import { useState } from 'react'
import AccountSelectionWrapper from './components/AccountSelectionWrapper'

function App() {
  const [signingIn, setSigningIn] =  useState(false)

  const toggleAccountSelection = () => {
    setSigningIn((prev) => !prev)
  }

  return (
    <>
      {signingIn ? (
        <div className="container">
          <div className="row">
            <AccountSelectionWrapper onSuccess={toggleAccountSelection}/>
          </div>
      </div>
      ) : (
        <div className="container">
          <div className="row">
            <MainWrapper/>
          </div>
      </div>
      )}
    </>
  )
}

export default App
