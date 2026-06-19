import CameraArea from './CameraArea.jsx'

function SlidesWrapper ( {isRecording}) {
    
    return (
        <div className="ratio ratio-16x9 bg-dark rounded-4 shadow">
            <div>
                <div className="position-absolute bottom-0 start-0 m-3 rounded-3" style={{width:'20%'}}>
                    <div className="ratio ratio-4x3 rounded-3 overflow-hidden bg-secondary shadow">
                        <CameraArea isRecording={isRecording}/>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SlidesWrapper