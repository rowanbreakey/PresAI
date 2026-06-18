import { useEffect } from "react"

function CameraArea({ isRecording}) {
    
    useEffect(() => {
    if (isRecording) {
      console.log("Camera Area: Starting webcam stream and recording...")
    } else {
      console.log("Camera Area: Stopping webcam stream and saving file...")
    }
  }, [isRecording])

    return (
        <div className="ratio ratio-16x9 bg-dark">
            {isRecording ? (
                <p>cam feed here</p>
            ) : (
                <p>no cam feed here</p>
            )}
        </div>
    )
}

export default CameraArea