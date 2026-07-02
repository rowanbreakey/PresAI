import SubmitButton from "./submitButton"

function SignInPage( {signingIn, onSuccess} ) {
    const checkSignIn = () => {
        onSuccess()
    }
    return (
        <div className="row justify-content-center align-items-center vh-100">
            <div className="col-12 col-md-4">
                <div className="card shadow p-4 m-0 mx-auto">
                    <h2>Sign In</h2>
                    <br/>
                    <label for="emailFormControl" className="form-label">Email:</label>
                    <input type="email" class="form-control" id="emailFormControl" placeholder="name@example.com"></input>
                    <br/>
                    <label for="passwordFormControl" className="form-label">Password:</label>
                    <input type="password" class="form-control" id="passwordFormControl" placeholder="name@example.com"></input>
                    <br/>
                    <SubmitButton onClick={checkSignIn}/>
                </div>
            </div>
        </div>
    )
}

export default SignInPage