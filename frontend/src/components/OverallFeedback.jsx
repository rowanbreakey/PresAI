import { useState, useEffect } from 'react'


function OverallFeedback({readyForFeedback, setReadyForFeedback}) {
    const [feedback, setFeedback] = useState(null)

    useEffect(() => {
        async function getFeedback() {
            const response = await fetch(`http://${window.location.hostname}:8000/api/get-feedback`, {
                method: 'GET',
                credentials: 'include'
                });

            await fetch(`http://${window.location.hostname}:8000/api/delete-old-feedback`, {
                method: 'DELETE', 
                credentials: 'include'
            });

            return response
        }

         setFeedback(getFeedback())
    }, [])

    return (
        <div style={{position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0, 0, 0, 0.5)', backdropFilter: 'blur(5px)'}}>
            <div className="row justify-content-center align-items-center vh-100">
                <div className="col-12 col-md-6">
                    <div className="card shadow p-4 m-0 mx-auto">
                        <h1>Overall Feedback</h1>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default OverallFeedback;