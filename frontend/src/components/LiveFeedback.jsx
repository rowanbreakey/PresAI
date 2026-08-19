import { useState, useEffect } from 'react'

function LiveFeedback({ data }) {
    if (!data) {
        return (
            <div className="card shadow p-4 m-4 mx-auto">
            <h1>Feedback</h1>
            <br />
            <h4>Eye Contact: Loading...</h4>
            <br />
            <h4>Pacing: Loading...</h4>
            <br />
            <h4>Filler Word Count: Loading...</h4>
            <br />
            <h4>Gesture Use: Loading...</h4>
            <br />
            <h4>Quick Tip: Loading...</h4>
        </div>
        )
    }
    
    return (
        <div className="card shadow p-4 m-4 mx-auto">
            <h1>Feedback</h1>
            <br />
            <h4>Eye Contact: {data.eye_contact}</h4>
            <br />
            <h4>Pacing: {data.pacing}</h4>
            <br />
            <h4>Filler Word Count: {data.filler_word_count}</h4>
            <br />
            <h4>Gesture Use: {data.gesture_use}</h4>
            <br />
            <h4>Quick Tip: {data.quick_tip}</h4>
        </div>
    )
}

export default LiveFeedback