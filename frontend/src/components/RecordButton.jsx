function RecordButton({ isRecording, onToggle }) {
    return (
        <button className="btn btn-primary" onClick={onToggle}>
            {isRecording ? (
                <p>Stop</p>
            ) : (
                <p>Start</p>
            )}
        </button>
    )
}

export default RecordButton