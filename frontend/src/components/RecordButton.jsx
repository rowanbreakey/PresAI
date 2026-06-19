function RecordButton({ isRecording, onToggle }) {
    return (
        <button className="btn btn-primary m-3" onClick={onToggle}>
            {isRecording ? (
                "Stop"
            ) : (
                "Start"
            )}
        </button>
    )
}

export default RecordButton