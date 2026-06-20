import { useEffect, useRef } from "react"

function CameraArea({ isRecording, passNewData }) {
    const videoRef = useRef(null);
    const frameBatch = useRef([]);
    const processingActive = useRef(false);

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

            const uploadInterval = setInterval(async () => {
                if (processingActive.current || frameBatch.current.length === 0) return;

                const batchToSend = frameBatch.current;
                frameBatch.current = [];

                processingActive.current = true

                try {
                    
                    const audio = "audio source will go here"

                    const response = await fetch('http://127.0.0.1:8000/api/process-batch', {
                        method: 'POST',
                        headers: {
                            'Content-Type' : 'application/json'
                        }, 
                        body: JSON.stringify({
                            frames: batchToSend,
                            audio: audio
                        }),
                    });

                    if (!response.ok) {
                        throw new Error("Server status error: ${response.status}");
                    }

                    const result = await response.json();
                    passNewData(result);

                } catch (error) {
                    console.log("couldnt process data", error);
                } finally {
                    processingActive.current = false;
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