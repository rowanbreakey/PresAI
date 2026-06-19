import { useEffect, useRef } from "react"

function CameraArea({ isRecording }) {
    const videoRef = useRef(null);

    useEffect(() => {
        if (isRecording) {
            async function getMedia(constraints) {
                let stream = null;

                try {
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                } catch (error) {
                    console.log("Camera not working" + error.name)
                }
                
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            }
            getMedia({video:true, audio:false});
        } else {
            console.log("camera feed ending")
        }
    }, [isRecording])


    return (
        <>
            {isRecording ? (
                <div className="ratio ratio-16x9 bg-dark">
                    <video ref={videoRef} autoPlay playsInline style={{width :'100%'}} />
                </div>
            ) : (
                <div className="ratio ratio-16x9 bg-dark"></div>
            )}
        </>
    )
}

export default CameraArea