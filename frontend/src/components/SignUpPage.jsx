import { useState } from "react";

function SignUpPage( {onSuccess, onSwitch} ) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({text: '', isError: false});

    const submitSignUp = async (event) => {
        event.preventDefault();
        setLoading(true);
        setMessage({text: "", isError: false})

        try {
            const response = await fetch(`http://${window.location.hostname}:8000/auth/signup`, {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json', 
                }, 
                body: JSON.stringify({email, password}), 
            });

            const data = await response.json();

            if (!response.ok) {
                const errMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
                throw new Error(errMsg || 'Sign up failed');
            }

            setMessage({ text: 'Success! ${data.message}', isError: false});
            setEmail('');
            setPassword('');
            onSuccess();
        } catch (error) {
            setMessage({ text: error.message, isError: true});
        } finally {
            setLoading(false);
        }
    }
    
    return (
        <div className="row justify-content-center align-items-center vh-100">
            <div className="col-12 col-md-4">
                <div className="card shadow p-4 m-0 mx-auto">
                    <form onSubmit={submitSignUp}>
                        <h2>Sign Up</h2>
                        <br/>
                        <label htmlFor="emailFormControl" className="form-label">Email:</label>
                        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="form-control" id="emailFormControl" placeholder="name@example.com" required></input>
                        <br/>
                        <label htmlFor="passwordFormControl" className="form-label">Password:</label>
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="form-control" id="passwordFormControl" required minLength={8}></input>
                        <br/>
                        <div className="d-grid gap-2">
                            <button type="submit" disabled={loading} className="btn btn-primary mt-3 ms-3 me-3">
                                {loading ? 'Creating Account...' : 'Sign in'}
                            </button>
                        </div>
                    </form>
                    <button onClick={onSwitch} className="btn btn-link text-secondary">
                        Already have an account? Click here!
                    </button>
                    <div style={{ marginTop: '15px', textAlign:"center", fontSize: '10px', color: message.isError ? 'red' : 'green', fontWeight: 'bold' }}>
                        {message.text}
                    </div>
                    <div style={{ marginTop: '15px', textAlign:"center", fontSize: '10px', color: message.isError ? 'red' : 'green', fontWeight: 'bold' }}>
                        {message.text}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SignUpPage