import { useState } from 'react'
import CameraArea from './CameraArea.jsx'
import RecordButton from './RecordButton.jsx'

function CameraWrapper() {
    const [isRecording, setIsRecording] = useState(false)

    const toggleRecording = () => {
        setIsRecording((prev) => !prev)
    }
    return (
        <div className="card shadow p-4 mx-auto" style={{ maxWidth: '550px' }}>
            <CameraArea isRecording={isRecording} />
            <RecordButton isRecording={isRecording} onToggle={toggleRecording} />
        </div>
    )
}

export default CameraWrapper