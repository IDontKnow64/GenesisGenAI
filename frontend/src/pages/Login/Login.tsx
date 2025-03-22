import { FC, useState } from "react"
import { Button } from "../../components/ui/button"

const LoginPage: FC = () => {
    const [counter, setCounter] = useState<number>(0);

    const onConnectGmail = () => {
        setCounter(counter + 1);
    }
    const onConnectOutlook = () => {
        setCounter(counter + 10);
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 gap-15">
            <h1 className="text-5xl font-bold text-gray-800 mb-8 animate-fade-in">
                Connect to mail services
            </h1>

            <div className="flex flex-col items-center gap-3">
                <div className="flex flex-row items-center gap-6">
                    <Button onClick={onConnectGmail} className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Connect Google
                    </Button>
                    <Button onClick={onConnectOutlook} className="px-8 py-3 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Connect Outlook
                    </Button>
                    
                </div>
                <div className="text-3xl font-mono text-gray-600 mt-4">
                    Counter: {counter}
                </div>
            </div>
        </div>
    )
}

export default LoginPage;