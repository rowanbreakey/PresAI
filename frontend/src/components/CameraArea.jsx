import { useEffect, useRef } from "react"

function CameraArea({ isRecording }) {
    const videoRef = useRef(null);
    const frameBatch = useRef([]);

    useEffect(() => {
        if (isRecording) {
            let activeStream = null;
            
            async function getMedia(constraints) {
                let stream = null;

                try {
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                    activeStream = stream;
                } catch (error) {
                    console.log("Camera not working" + error.name);
                }
                
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            }
            getMedia({video:true, audio:false});

            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");

            const captureInterval = setInterval(() => {
                if (videoRef.current && videoRef.current.readyState === 4) {
                    const video = videoRef.current;

                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                    const frameData = canvas.toDataURL("image/webp", 0.6);

                    frameBatch.current.push(frameData);
                }
            }, 333);

            const uploadInterval = setInterval(() => {
                const batchToSend = frameBatch.current;
                frameBatch.current = [];

                try {
                    console.log("api stuff here");
                } catch (error) {
                    console.log(error);
                }
            }, 5000);

            return () => {
                if (activeStream) {
                    activeStream.getTracks().forEach(track => track.stop());
                }
                if (captureInterval) clearInterval(captureInterval);
                if (uploadInterval) clearInterval(uploadInterval);

                frameBatch.current = []
            };
        }
    }, [isRecording])


    return (
        <>
            {isRecording ? (
                <video ref={videoRef} autoPlay playsInline style={{width :'100%'}} />
            ) : (
                <></>
            )}
        </>
    )
}

export default CameraArea