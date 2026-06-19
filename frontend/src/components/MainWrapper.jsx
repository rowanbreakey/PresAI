import { useState } from 'react'
import SlidesWrapper from './SlidesWrapper.jsx'
import RecordButton from './RecordButton.jsx'

function MainWrapper() {
    const [isRecording, setIsRecording] = useState(false)

    const toggleRecording = () => {
        setIsRecording((prev) => !prev)
    }
    return (
        <div className="card shadow p-4 m-4 mx-auto">
            <SlidesWrapper isRecording={isRecording} />
            <RecordButton isRecording={isRecording} onToggle={toggleRecording} />
        </div>
    )
}

export default MainWrapper