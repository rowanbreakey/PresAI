import { useState } from "react";

function SignInPage( {signingIn, onSuccess} ) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({text: '', isError: false});

    function ValidateEmail(data) {
        const input = document.createElement('input');
        input.type = 'email';
        input.value = data;

        return input.checkValidity();
    }

    const submitSignUp = async (event) => {
        event.preventDefault();
        setLoading(true);
        setMessage({text: "", isError: false})

        if (!ValidateEmail(email)) {
            setLoading(true);
            setMessage({text: "Enter a valid email addresss", isError: true});
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/signup', {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json', 
                }, 
                body: JSON.stringify({email, password}), 
            });

            const data = await response.json();

            if (!response.ok) {
                const errMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
                throw new Error(errMsg || 'Signup failed');
            }

            setMessage({ text: 'Success! ${data.message}', isError: false});
            setEmail('');
            setPassword('');
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
                        <h2>Sign In</h2>
                        <br/>
                        <label htmlFor="emailFormControl" className="form-label">Email:</label>
                        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="form-control" id="emailFormControl" placeholder="name@example.com" required></input>
                        <br/>
                        <label htmlFor="passwordFormControl" className="form-label">Password:</label>
                        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="form-control" id="passwordFormControl" required minLength={8}></input>
                        <br/>
                        <div className="d-grid gap-2">
                            <button type="submit" disabled={loading} className="btn btn-primary mt-3 ms-3 me-3">
                                {loading ? 'Creating Account...' : 'Sign Up'}
                            </button>
                        </div>
                    </form>
                    <div style={{ marginTop: '15px', alignContent:"center", fontSize: '10px', color: message.isError ? 'red' : 'green', fontWeight: 'bold' }}>
                        {message.text}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SignInPage