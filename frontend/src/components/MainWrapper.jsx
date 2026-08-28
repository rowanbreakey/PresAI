import { useState } from 'react'
import CameraArea from './CameraArea.jsx'
import RecordButton from './RecordButton.jsx'
import LiveFeedback from './LiveFeedback.jsx'
import PresentationArea from './PresentationArea.jsx'
import OverallFeedback from './OverallFeedback.jsx'

function MainWrapper() {
    const [isRecording, setIsRecording] = useState(false)
    const [metrics, setMetrics] = useState(null)
    const [readyForFeedback, setReadyForFeedback] = useState(false)

    const toggleRecording = () => {
        if (isRecording) {
            setReadyForFeedback(true);
        }
        setIsRecording((prev) => !prev);
    }

    return (
        <>
        <div className="col-12 col-md-8">
          <div className="card shadow p-4 m-4 mx-auto">
            <PresentationArea>
                <div>
                    <div className="position-absolute bottom-0 start-0 m-3 rounded-3" style={{width:'20%'}}>
                        <div className="ratio ratio-4x3 rounded-3 overflow-hidden bg-secondary shadow">
                            <CameraArea isRecording={isRecording} passNewData={setMetrics} />
                        </div>
                    </div>
                </div>
            </PresentationArea>
            <RecordButton isRecording={isRecording} onToggle={toggleRecording} />
        </div>
        </div>
        <div className="col-12 col-md-4">
          <LiveFeedback data={metrics} />
        </div>

        {readyForFeedback ? (
            <OverallFeedback readyForFeedback={readyForFeedback} setReadyForFeedback={setReadyForFeedback}/>
        ) : (
            <></>
        )}
        </>


    )
}

export default MainWrapper