import MainWrapper from './components/MainWrapper'
import LiveFeedback from './components/LiveFeedback'
import  SignInPage from './components/SignInPage'
import { useState } from 'react'

function App() {
  const [signingIn, setSigningIn] =  useState(true)

  const toggleRecording = () => {
    setSigningIn((prev) => !prev)
  }

  return (
    <>
      {signingIn ? (
        <div className="container">
          <div className="row">
            <SignInPage signingIn={signingIn} onSuccess={toggleRecording}/>
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
