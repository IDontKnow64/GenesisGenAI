import { FC, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "../../components/ui/button"

const HomePage: FC = () => {
    const [counter, setCounter] = useState<number>(0);
    const navigate = useNavigate();

    const onConnectEmail = () => {
        setCounter(counter + 1);
        navigate("/login");
    }

    const onNavigateMail = () => {
        navigate("/mail")
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
            <h1 className="text-5xl font-bold text-gray-800 mb-8 animate-fade-in">
                Welcome to the Homepage
            </h1>
            
            <div className="flex flex-col items-center gap-6">
                <div className="flex flex-row items-center gap-4">
                    <Button onClick={onConnectEmail} className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Connect email
                    </Button>
                    <Button onClick={onNavigateMail} className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Go to Mail
                    </Button>
                </div>
                
                <div className="text-3xl font-mono text-gray-600 mt-4">
                    Counter: {counter}
                </div>
            </div>
        </div>
    )
}

export default HomePage;