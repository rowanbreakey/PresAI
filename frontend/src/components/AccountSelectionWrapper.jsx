import { useState } from "react"
import SignInPage from "./SignInPage"
import SignUpPage from "./SignUpPage"

function AccountSelectionWrapper( {onSuccess} ) {
    const [creatingAccount, setCreating] = useState(false)

    const changePage = () => {
        setCreating((prev) => !prev)
    }

    return(
        <>
            {creatingAccount ? (
                <SignUpPage onSuccess={changePage} onSwitch={changePage}/>
            ) : (
                <SignInPage onSuccess={onSuccess} onSwitch={changePage}/>
            )}
        </>
    )
}

export default AccountSelectionWrapper