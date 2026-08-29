import { useState, useEffect } from 'react'


function OverallFeedback({doneWithFeedback}) {
    const [feedback, setFeedback] = useState(null)

    useEffect(() => {
        async function getFeedback() {
            const response = await fetch(`http://${window.location.hostname}:8000/api/get-feedback`, {
                method: 'GET',
                credentials: 'include'
                });

            const data = await response.json();

            await fetch(`http://${window.location.hostname}:8000/api/delete-old-feedback`, {
                method: 'DELETE', 
                credentials: 'include'
            });

            return data;
        }

         getFeedback().then(data => setFeedback(data));
         console.log(feedback)
    }, [])

    if (!feedback) {
        return (
            <div onClick={doneWithFeedback} style={{position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0, 0, 0, 0.5)', backdropFilter: 'blur(5px)'}}>
                <div className="row justify-content-center align-items-center vh-100">
                    <div className="col-12 col-md-6">
                        <div className="card shadow p-4 m-0 mx-auto">
                            <h1>Overall Feedback</h1>
                            <br></br>
                            <h2>Score: Loading...</h2>
                            <br></br>
                            <h5>Feedback: Loading...</h5>
                            <h5>Click anywhere to return to presentation area</h5>
                        </div>
                    </div>
                </div>
            </div>
        )
    } else {
        return (
            <div onClick={doneWithFeedback} style={{position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0, 0, 0, 0.5)', backdropFilter: 'blur(5px)'}}>
                <div className="row justify-content-center align-items-center vh-100">
                    <div className="col-12 col-md-6">
                        <div className="card shadow p-4 m-0 mx-auto">
                            <h1>Overall Feedback</h1>
                            <br></br>
                            <h2>Score: {feedback.overall_score}</h2>
                            <br></br>
                            <h5>Feedback: {feedback.feedback_paragraph}</h5>
                            <br></br>
                            <h5>Click anywhere to return to presentation area</h5>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

export default OverallFeedback;