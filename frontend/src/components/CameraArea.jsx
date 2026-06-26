import { useEffect, useRef } from "react"

function CameraArea({ isRecording, passNewData }) {
    const videoRef = useRef(null);
    const audioRef = useRef(null)
    const frameBatch = useRef([]);
    const audio = useRef([]);
    const processingActive = useRef(false);

    useEffect(() => {
        if (isRecording) {
            let activeStream = null;
            
            async function getMedia(constraints) {
                let stream = null;

                try {
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                    activeStream = stream;
                
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                    }

                    const audioTracks = stream.getAudioTracks();
                    if (audioTracks.length > 0) {
                        const audioOnlyStream = new MediaStream([audioTracks[0]]);

                        const audioRecorder = new MediaRecorder(audioOnlyStream, { mimeType: 'audio/webm' });
                        audioRef.current = audioRecorder;

                        audioRef.current.ondataavailable = (event) => {
                            if (event.data.size > 0) {
                                audio.current.push(event.data);
                            }
                        };

                        audioRef.current.start();
                    }
                } catch (error) {
                    console.log("Camera or mic not working" + error.name);
                }
            }
            
            getMedia({video:true, audio: {channelCount : 1, sampleRate : 16000}});

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

                const videoBatch = frameBatch.current;
                frameBatch.current = [];
                
                let audioBatch = null;

                if (audioRef.current && audioRef.current.state === "recording") {
                    audioRef.current.stop();
                    
                    audioBatch = new Blob(audio.current, {type : 'audio/webm'});
                    audio.current = [];

                    audioRef.current.start();
                }

                processingActive.current = true;

                try {

                    const formData = new FormData();
                    formData.append('frames', JSON.stringify(videoBatch))
                    if (audioBatch) {
                        formData.append('audio', audioBatch, 'audio.webm')
                    }

                    const response = await fetch('http://127.0.0.1:8000/api/process-batch', {
                        method: 'POST',
                        body: formData
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