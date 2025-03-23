import { FC, useEffect, useState } from "react"
import { Button } from "../../components/ui/button"
import { initiateGoogleAuth } from '../../services/api';
import { useNavigate } from "react-router-dom";
import { emailService } from "../../services/api";
const LoginPage: FC = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [isLoading, setIsLoading] = useState(true)
    const [headerText, setHeaderText] = useState("")
    const navigate = useNavigate();
    const onConnectGmail = async () => {
        try {
            await initiateGoogleAuth();
        } catch (error) {
            // Show error to user
            alert(error)
            alert('Failed to start Google authentication');
        }
    }


    const onReturn = () => {
        navigate('/')
    }

    useEffect(() => {
        const checkEmailConnection = async () => {
            try {
              const response = await emailService.checkConnection();
              console.log(response)
              setIsConnected(response['connected']);
              if (response['connected']) {
                setHeaderText("You're connected!")
            } else {
                
                setHeaderText("You aren't connected!")
              }
            } catch (error) {
                console.error('Connection check failed:', error);
                setIsConnected(false);
            } finally {
                setIsLoading(false);
            }
        };

        checkEmailConnection();
    }, [])

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 gap-15">
            <h1 className="text-7xl font-bold text-gray-800 mb-8 animate-fade-in">
                { headerText }
            </h1>
            <h3 className="text-2xl font-bold text-gray-600 mb-8 animate-fade-in">
                Connect to Google mail services below.
            </h3>

            <div className="flex flex-col items-center gap-3">
                <div className="flex flex-row items-center gap-6">
                    <Button onClick={onConnectGmail} className="px-16 py-6 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        {isConnected ? "Disconnect" : "Connect"}
                        <span className="inline-flex gap-0.5">
                    <span style={{ color: "#4285F4" }}>G</span>
                    <span style={{ color: "#EA4335" }}>o</span>
                    <span style={{ color: "#FBBC05" }}>o</span>
                    <span style={{ color: "#4285F4" }}>g</span>
                    <span style={{ color: "#34A853" }}>l</span>
                    <span style={{ color: "#EA4335" }}>e</span>
                    </span>
                    </Button>
                    <Button onClick={onReturn} className="px-16 py-6 text-white 
                                    transition-colors duration-300
                                    shadow-lg transform hover:scale-105">
                        Back
                    </Button>
                </div>
            </div>
        </div>
    )
}

export default LoginPage;
